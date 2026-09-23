import { api } from "./client";
import type { Document, Paginated, UploadResponse } from "@/types/api";

export type ListDocumentsParams = {
  page?: number;
  page_size?: number;
};

export const documentsApi = {
  /**
   * GET /documents?page=&page_size=
   *
   * The backend uses FastAPI pagination. Depending on your response_model,
   * it may return either `{ items, total, page, page_size }` or a bare
   * `Document[]`. The return type covers both, and the caller normalizes.
   */
  list: (params?: ListDocumentsParams) =>
    api.get<Document[] | Paginated<Document>>("/documents", { params }),

  get: (id: string) => api.get<Document>(`/documents/${id}`),

  upload: (file: File, onProgress?: (progress: number) => void) => {
    const body = new FormData();
    body.append("file", file);
    return api.post<UploadResponse>("/documents/upload", body, {
      // NOTE: do NOT set Content-Type manually — axios sets it with the
      // correct multipart boundary when it detects a FormData body.
      onUploadProgress: (event) => {
        if (!event.total) {
          onProgress?.(0);
          return;
        }
        onProgress?.(Math.round((event.loaded / event.total) * 100));
      },
    });
  },

  extract: (id: string) => api.post<UploadResponse>(`/documents/${id}/extract`),

  remove: (id: string) => api.delete(`/documents/${id}`),
};
