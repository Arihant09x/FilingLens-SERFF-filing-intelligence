export type User = {
  id: string;
  email: string;
  is_active: boolean;
};

export type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type Document = {
  id: string;
  filename: string;
  file_size: number;
  page_count: number | null;
  stage: string | null; // ← add
  message: string | null; // ← add
  job_id: string | null; // ← add
  attempt_count: number; // ← add
  started_at: string | null; // ← add
  completed_at: string | null; // ← add
  last_progress_at: string | null; // ← add
  error_message: string | null; // ← add
  status: string;
  current_page: number;
  total_pages: number | null;
  progress_percentage: number;
  created_at: string;
  // NOTE: removed the bogus `querySelector` field that was here
};

export type UploadResponse = {
  document_id: string;
  job_id: string;
  status: string;
};

export type Source = {
  page?: number;
  bbox?: [number, number, number, number];
};

export type MetadataValue = {
  value: string;
  source?: Source;
};

export type Section = {
  heading: string;
  level: string;
  text: string;
  section_type: string;
  page_start: number;
  page_end: number;
  confidence: number;
  source?: Source;
};

export type TableRecord = {
  title: string;
  page: number;
  columns: string[];
  rows: string[][];
  bbox?: [number, number, number, number];
  confidence: number;
};

export type Attachment = {
  name: string;
  category: string;
  status: string;
  public_access: boolean | null;
  page?: number;
  confidence: number;
  source?: Source;
};

export type Correspondence = {
  type: string;
  status: string;
  created_by: string | null;
  created_on: string | null;
  submitted_date: string | null;
  responded_by: string | null;
  response_date: string | null;
  page?: number;
  confidence: number;
  text: string;
  source?: Source;
};

export type ReviewFlag = {
  type: string;
  severity: string;
  message: string;
  page: number | null;
  confidence?: number;
  field?: string;
};

export type Snapshot = {
  section_count: number;
  table_count: number;
  attachment_count: number;
  correspondence_count: number;
  average_confidence: number;
  low_confidence_count: number;
  review_flag_count: number;
  page_count: number;
};

export type StructuredData = {
  metadata: Record<string, MetadataValue>;
  sections: Section[];
  tables: TableRecord[];
  attachments: Attachment[];
  correspondence: Correspondence[];
  pages: { page: number; text: string }[];
  review_flags: ReviewFlag[];
  snapshot: Snapshot;
};

export type Extraction = {
  id: string;
  document_id: string;
  version: number;
  strategy: string;
  status: string;
  structured_data: StructuredData;
  confidence_summary: Snapshot;
};

export type ReviewResponse = {
  flags: ReviewFlag[];
};

/**
 * Generic paginated envelope used by list endpoints.
 * The backend returns `{ items, total, page, page_size }` for paginated
 * endpoints, but the API layer also tolerates a bare array response.
 */
export type Paginated<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};
