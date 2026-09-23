import { api } from "./client";
export type ExportFormat = "json" | "csv" | "markdown";
export async function downloadExport(id: string, format: ExportFormat) {
  const response = await api.get(`/documents/${id}/export/${format}`, {
    responseType: "blob",
  });
  const url = URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = `filing.${format === "markdown" ? "md" : format}`;
  link.click();
  URL.revokeObjectURL(url);
}
