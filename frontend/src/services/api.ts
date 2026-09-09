import type {
  VerificationResponse,
  VerificationDetailResponse,
} from "../types/verification";
import type { VerificationHistoryResponse } from "../types/history";
import { auth } from "../firebase";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function verifyResponse(
  response: string
): Promise<VerificationResponse> {
  const user = auth.currentUser;

  if (!user) {
    throw new Error("User is not authenticated.");
  }

  const idToken = await user.getIdToken();

  const result = await fetch(`${API_BASE_URL}/api/verify`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({
      response,
    }),
  });

  if (!result.ok) {
    const errorData = await result.json().catch(() => null);

    throw new Error(
      errorData?.detail || "Verification request failed."
    );
  }

  return result.json();
}

export async function getVerificationHistory(): Promise<VerificationHistoryResponse> {
  const user = auth.currentUser;

  if (!user) {
    throw new Error("User is not authenticated.");
  }

  const idToken = await user.getIdToken();

  const result = await fetch(
    `${API_BASE_URL}/api/verifications`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${idToken}`,
      },
    }
  );

  if (!result.ok) {
    const errorData = await result.json().catch(() => null);

    throw new Error(
      errorData?.detail ||
        "Failed to load verification history."
    );
  }

  return result.json();
}

export async function getVerificationDetail(
  verificationId: number
): Promise<VerificationDetailResponse> {
  const user = auth.currentUser;

  if (!user) {
    throw new Error("User is not authenticated.");
  }

  const idToken = await user.getIdToken();

  const result = await fetch(
    `${API_BASE_URL}/api/verifications/${verificationId}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${idToken}`,
      },
    }
  );

  if (!result.ok) {
    const errorData = await result.json().catch(() => null);

    throw new Error(
      errorData?.detail ||
        "Failed to load verification details."
    );
  }

  return result.json();
}
