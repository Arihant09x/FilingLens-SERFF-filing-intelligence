import { api } from "./client";
import type { Extraction } from "@/types/api";
export const extractionApi = {
  list: (id: string) => api.get<Extraction[]>(`/documents/${id}/extractions`),
  get: (id: string, version: number) =>
    api.get<Extraction>(`/documents/${id}/extractions/${version}`),
};
