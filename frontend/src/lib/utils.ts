export { cn } from "cn";

export function formatBytes(bytes: number) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1,
  );
  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`;
}

export function friendlyError(error: unknown, fallback: string) {
  const status = (error as { response?: { status?: number } })?.response
    ?.status;
  return status === 401
    ? "Your session has expired. Please sign in again."
    : fallback;
}
