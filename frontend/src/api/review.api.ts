import { api } from "./client";
import type { ReviewResponse } from "@/types/api";
export const reviewApi = {
  get: (id: string) => api.get<ReviewResponse>(`/documents/${id}/review`),
};
