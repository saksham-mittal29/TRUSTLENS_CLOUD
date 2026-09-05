from app.services.evidence_search import search_evidence

results = search_evidence("Eiffel Tower height")

for result in results:
    print(result)
