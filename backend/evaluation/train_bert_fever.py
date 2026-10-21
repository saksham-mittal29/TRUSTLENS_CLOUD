import os
import sys
import json
import random
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup
)
from datasets import load_dataset
from sklearn.metrics import accuracy_score, f1_score

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_MODEL_DIR = BASE_DIR / "models" / "bert-fever-finetuned"

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)

# Model configuration
BASE_MODEL = "textattack/bert-base-uncased-MNLI"  # Warm start from MNLI for fast convergence

# Label mapping
# 0 -> CONTRADICTED
# 1 -> SUPPORTED
# 2 -> NOT ENOUGH EVIDENCE
LABEL_MAP = {
    "REFUTES": 0,
    "SUPPORTS": 1,
    "NOT ENOUGH INFO": 2
}

ID2LABEL = {
    0: "CONTRADICTED",
    1: "SUPPORTED",
    2: "NOT ENOUGH EVIDENCE"
}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}


class FeverNLIDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


def prepare_balanced_data(split_name="train", samples_per_class=2500):
    print(f"Loading '{split_name}' split from pietrolesci/nli_fever...")
    ds = load_dataset("pietrolesci/nli_fever", split=split_name)
    
    by_class = {0: [], 1: [], 2: []}
    for item in ds:
        gold_label = item.get("fever_gold_label")
        if gold_label not in LABEL_MAP:
            continue
        class_idx = LABEL_MAP[gold_label]
        
        # In pietrolesci/nli_fever:
        # 'hypothesis' is the Wikipedia evidence snippet
        # 'premise' is the claim
        evidence = item.get("hypothesis", "").strip()
        claim = item.get("premise", "").strip()
        
        if evidence and claim:
            by_class[class_idx].append({
                "premise": evidence,
                "hypothesis": claim,
                "label": class_idx
            })
            
    selected = []
    for c_idx in [0, 1, 2]:
        pool = by_class[c_idx]
        random.shuffle(pool)
        taken = pool[:samples_per_class]
        selected.extend(taken)
        print(f"  Class {ID2LABEL[c_idx]} ({c_idx}): sampled {len(taken)} examples")
        
    random.shuffle(selected)
    return selected


def train_fever_model(samples_per_class=2000, epochs=2, batch_size=32, lr=2e-5):
    print("=" * 70)
    print("FINE-TUNING BERT ON FEVER FACT-VERIFICATION DATASET")
    print("=" * 70)
    print(f"Hyperparameters: epochs={epochs}, batch_size={batch_size}, lr={lr}, samples/class={samples_per_class}")
    
    # 1. Device selection
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using Apple Silicon MPS acceleration.")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("Using CUDA acceleration.")
    else:
        device = torch.device("cpu")
        print("Using CPU device.")
        
    # 2. Prepare Data
    train_data = prepare_balanced_data(split_name="train", samples_per_class=samples_per_class)
    val_data = prepare_balanced_data(split_name="dev", samples_per_class=max(100, samples_per_class // 10))
    
    print(f"\nTotal training pairs: {len(train_data)}")
    print(f"Total validation pairs: {len(val_data)}")
    
    # 3. Load Tokenizer & Model
    print(f"\nInitializing model from: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=3,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        ignore_mismatched_sizes=True
    )
    model.to(device)
    
    # 4. Tokenize
    print("Tokenizing datasets...")
    train_encodings = tokenizer(
        [x["premise"] for x in train_data],
        [x["hypothesis"] for x in train_data],
        truncation=True,
        max_length=256,
        padding=True,
        return_tensors="pt"
    )
    val_encodings = tokenizer(
        [x["premise"] for x in val_data],
        [x["hypothesis"] for x in val_data],
        truncation=True,
        max_length=256,
        padding=True,
        return_tensors="pt"
    )
    
    train_dataset = FeverNLIDataset(train_encodings, [x["label"] for x in train_data])
    val_dataset = FeverNLIDataset(val_encodings, [x["label"] for x in val_data])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # 5. Training Setup
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    warmup_steps = int(total_steps * 0.1)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps
    )
    
    best_val_f1 = 0.0
    OUTPUT_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\nStarting Training Loop...")
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        
        for step, batch in enumerate(train_loader, start=1):
            optimizer.zero_grad()
            
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            scheduler.step()
            
            total_loss += loss.item()
            
            if step % 25 == 0 or step == len(train_loader):
                avg_step_loss = total_loss / step
                print(f"  Epoch {epoch}/{epochs} | Step {step}/{len(train_loader)} | Loss: {avg_step_loss:.4f}")
                
        # Validation
        model.eval()
        val_preds = []
        val_trues = []
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"]
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=-1).cpu().numpy()
                
                val_preds.extend(preds)
                val_trues.extend(labels.numpy())
                
        val_acc = accuracy_score(val_trues, val_preds)
        val_f1 = f1_score(val_trues, val_preds, average="macro")
        
        print(f"--> Epoch {epoch} Validation: Accuracy = {val_acc*100:.2f}% | Macro-F1 = {val_f1:.4f}")
        
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            print(f"    * New best validation score! Saving to {OUTPUT_MODEL_DIR}")
            model.save_pretrained(OUTPUT_MODEL_DIR)
            tokenizer.save_pretrained(OUTPUT_MODEL_DIR)
            
    print("\n" + "=" * 70)
    print(f"Training complete! Best FEVER Validation Macro-F1: {best_val_f1:.4f}")
    print(f"Saved model to: {OUTPUT_MODEL_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fine-tune BERT on FEVER NLI dataset")
    parser.add_argument("--epochs", type=int, default=2, help="Number of training epochs (default: 2)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size (default: 32)")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate (default: 2e-5)")
    parser.add_argument("--samples-per-class", type=int, default=2000, help="Samples per class (default: 2000)")
    args = parser.parse_args()
    
    train_fever_model(
        samples_per_class=args.samples_per_class,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )
