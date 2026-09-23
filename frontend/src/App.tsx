import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  useQuery as useTanstackQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { toast, Toaster } from "sonner";
import {
  AlertCircle,
  Check,
  ChevronLeft,
  ChevronRight,
  Copy,
  Download,
  FileText,
  FolderOpen,
  Gauge,
  KeyRound,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Paperclip,
  Search,
  ShieldCheck,
  Sun,
  UploadCloud,
  X,
} from "lucide-react";
import { authApi } from "@/api/auth.api";
import { documentsApi } from "@/api/documents.api";
import { extractionApi } from "@/api/extraction.api";
import { reviewApi } from "@/api/review.api";
import { downloadExport, type ExportFormat } from "@/api/exports.api";
import { useAuthStore } from "@/stores/auth.store";
import { useWorkspaceStore } from "@/stores/workspace.store";
import type {
  Document,
  Extraction,
  ReviewFlag,
  Section,
  StructuredData,
} from "@/types/api";
import { cn, formatBytes, friendlyError } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import "./App.css";

function useQuery<TData>(
  options: Parameters<typeof useTanstackQuery<TData>>[0],
) {
  return useTanstackQuery(options) as ReturnType<
    typeof useTanstackQuery<TData>
  > & { data: TData };
}

const authSchema = z.object({
  email: z.string().email("Enter a valid work email"),
  password: z.string().min(8, "Use at least 8 characters"),
});
type AuthForm = z.infer<typeof authSchema>;

function ShortcutBridge() {
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (
        event.key === "/" &&
        !["INPUT", "TEXTAREA"].includes(target.tagName)
      ) {
        event.preventDefault();
        globalThis.document
          .querySelector<HTMLInputElement>(".filing-search")
          ?.focus();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);
  return null;
}

function App() {
  return (
    <BrowserRouter>
      <Toaster position="bottom-right" />
      <ShortcutBridge />
      <Routes>
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/register" element={<AuthPage mode="register" />} />
        <Route element={<ProtectedLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/filings/:id" element={<FilingWorkspace />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

function AuthPage({ mode }: { mode: "login" | "register" }) {
  const navigate = useNavigate();
  const setTokens = useAuthStore((state) => state.setTokens);
  const loadUser = useAuthStore((state) => state.loadUser);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const form = useForm<AuthForm>({
    resolver: zodResolver(authSchema),
    defaultValues: { email: "", password: "" },
  });
  async function submit(values: AuthForm) {
    setError("");
    try {
      const response =
        mode === "login"
          ? await authApi.login(values.email, values.password)
          : await authApi
              .register(values.email, values.password)
              .then(() => authApi.login(values.email, values.password));
      setTokens(response.data.access_token, response.data.refresh_token);
      await loadUser();
      toast.success(
        mode === "login" ? "Welcome back to FilingLens" : "Account created",
      );
      navigate("/dashboard");
    } catch (err) {
      setError(
        friendlyError(
          err,
          mode === "login"
            ? "Unable to sign in. Check your credentials."
            : "Unable to create your account.",
        ),
      );
    }
  }
  return (
    <main className="auth-page">
      <div className="auth-art">
        <div className="brand brand-light">
          Filing<span>Lens</span>
        </div>
        <div className="art-copy">
          <p className="eyebrow">SERFF filing intelligence</p>
          <h1>Turn complex filings into review-ready data.</h1>
          <p>
            Evidence-linked extraction for the moments when every page, field,
            and flag matters.
          </p>
        </div>
        <div className="art-stamp">
          <ShieldCheck size={16} /> Source evidence preserved
        </div>
      </div>
      <section className="auth-form">
        <div className="auth-form-inner">
          <div className="mobile-brand brand">
            Filing<span>Lens</span>
          </div>
          <p className="eyebrow">Reviewer access</p>
          <h2>{mode === "login" ? "Welcome back" : "Create your workspace"}</h2>
          <p className="muted">
            {mode === "login"
              ? "Sign in to continue reviewing your filings."
              : "Start structuring SERFF filings with your team."}
          </p>
          {error && (
            <Alert tone="danger">
              <AlertCircle size={16} />
              {error}
            </Alert>
          )}
          <form onSubmit={form.handleSubmit(submit)}>
            <label>
              Email address
              <Input
                type="email"
                placeholder="you@company.com"
                {...form.register("email")}
              />
            </label>
            {form.formState.errors.email && (
              <span className="field-error">
                {form.formState.errors.email.message}
              </span>
            )}
            <label>
              Password
              <div className="password-field">
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="8+ characters"
                  {...form.register("password")}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((value) => !value)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <X size={16} /> : <KeyRound size={16} />}
                </button>
              </div>
            </label>
            {form.formState.errors.password && (
              <span className="field-error">
                {form.formState.errors.password.message}
              </span>
            )}
            <Button
              type="submit"
              className="full-button"
              disabled={form.formState.isSubmitting}
            >
              {form.formState.isSubmitting
                ? "Working..."
                : mode === "login"
                  ? "Sign in"
                  : "Create account"}
              <ChevronRight size={16} />
            </Button>
          </form>
          <p className="auth-switch">
            {mode === "login" ? (
              <>
                Don't have an account? <Link to="/register">Create one</Link>
              </>
            ) : (
              <>
                Already have an account? <Link to="/login">Sign in</Link>
              </>
            )}
          </p>
        </div>
      </section>
    </main>
  );
}

function ProtectedLayout() {
  const loading = useAuthStore((state) => state.loading);
  const user = useAuthStore((state) => state.user);
  const loadUser = useAuthStore((state) => state.loadUser);
  useEffect(() => {
    void loadUser();
  }, [loadUser]);
  if (loading)
    return (
      <div className="app-loading">
        <Gauge />
        <span>Loading workspace</span>
      </div>
    );
  return user ? <AppShell /> : <Navigate to="/login" replace />;
}

function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const user = useAuthStore((state) => state.user);
  const clear = useAuthStore((state) => state.clear);
  const navigate = useNavigate();
  const location = useLocation();
  const [dark, setDark] = useState(
    localStorage.getItem("filinglens_theme") === "dark",
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("filinglens_theme", dark ? "dark" : "light");
  }, [dark]);

  const logout = () => {
    clear();
    toast.success("Signed out");
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <aside className={cn("sidebar", mobileOpen && "sidebar-open")}>
        <div className="sidebar-top">
          <Link to="/dashboard" className="brand">
            Filing<span>Lens</span>
          </Link>
          <button className="mobile-close" onClick={() => setMobileOpen(false)}>
            <X size={18} />
          </button>
        </div>
        <p className="eyebrow">Workspace</p>
        <nav>
          <NavItem
            to="/dashboard"
            icon={<LayoutDashboard size={17} />}
            label="Overview"
            active={location.pathname === "/dashboard"}
            close={() => setMobileOpen(false)}
          />
          <NavItem
            to="/upload"
            icon={<UploadCloud size={17} />}
            label="Upload filing"
            active={location.pathname === "/upload"}
            close={() => setMobileOpen(false)}
          />
        </nav>
        <div className="sidebar-note">
          <span className="live-dot" />
          Extraction engine online
          <br />
          <small>Evidence is never discarded</small>
        </div>
        <div className="user-row">
          <div className="avatar">{user?.email.slice(0, 1).toUpperCase()}</div>
          <div className="user-copy">
            <strong>{user?.email}</strong>
            <span>Reviewer</span>
          </div>
          <button aria-label="Sign out" onClick={logout}>
            <LogOut size={16} />
          </button>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setMobileOpen(true)}>
            <Menu size={20} />
          </button>
          <div className="crumb">
            FilingLens <ChevronRight size={14} />{" "}
            <span>
              {location.pathname.includes("filings")
                ? "Filing workspace"
                : "Workspace"}
            </span>
          </div>
          <div className="top-actions">
            <button
              className="icon-button"
              aria-label="Toggle dark mode"
              onClick={() => setDark((value) => !value)}
            >
              {dark ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <div className="top-avatar">
              {user?.email.slice(0, 1).toUpperCase()}
            </div>
          </div>
        </header>
        <div className="page-content">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/filings/:id" element={<FilingWorkspace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

function NavItem({
  to,
  icon,
  label,
  active,
  close,
}: {
  to: string;
  icon: ReactNode;
  label: string;
  active: boolean;
  close: () => void;
}) {
  return (
    <Link
      onClick={close}
      className={cn("nav-item", active && "nav-active")}
      to={to}
    >
      {icon}
      <span>{label}</span>
    </Link>
  );
}

type PaginatedDocuments = {
  items: Document[];
  total: number;
  page: number;
  page_size: number;
};

function Dashboard() {
  const pageSize = 10;
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");

  const { data, isLoading, error, isFetching } = useQuery({
    queryKey: ["documents", page, pageSize],
    queryFn: async (): Promise<PaginatedDocuments> => {
      const res = await documentsApi.list({ page, page_size: pageSize });
      const raw = res.data as
        | Document[]
        | {
            items?: Document[];
            total?: number;
            page?: number;
            page_size?: number;
          };
      if (Array.isArray(raw)) {
        const start = (page - 1) * pageSize;
        return {
          items: raw.slice(start, start + pageSize),
          total: raw.length,
          page,
          page_size: pageSize,
        };
      }
      return {
        items: raw.items ?? [],
        total: raw.total ?? raw.items?.length ?? 0,
        page: raw.page ?? page,
        page_size: raw.page_size ?? pageSize,
      };
    },
    placeholderData: (prev) => prev,
  });

  const documents = useMemo(() => data?.items ?? [], [data]);
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const visible = useMemo(
    () =>
      documents.filter(
        (item) =>
          (filter === "All" || statusGroup(item.status) === filter) &&
          item.filename.toLowerCase().includes(search.toLowerCase()),
      ),
    [documents, filter, search],
  );

  const reviewCount = documents.filter(
    (item) => item.status === "completed",
  ).length;

  return (
    <section className="dashboard">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Operations overview</p>
          <h1>Good morning, reviewer.</h1>
          <p className="muted">
            A clear view of filings moving through your review queue.
          </p>
        </div>
        <Link to="/upload">
          <Button>
            <UploadCloud size={17} /> Upload filing
          </Button>
        </Link>
      </div>

      <div className="metric-grid">
        <Metric
          icon={<FileText />}
          label="Total filings"
          value={total}
          detail="In your workspace"
        />
        <Metric
          icon={<Gauge />}
          label="Processing"
          value={
            documents.filter((i) => ["queued", "processing"].includes(i.status))
              .length
          }
          detail="On this page"
        />
        <Metric
          icon={<Check />}
          label="Ready"
          value={documents.filter((i) => i.status === "completed").length}
          detail="Ready to review"
        />
        <Metric
          icon={<AlertCircle />}
          label="Needs review"
          value={reviewCount}
          detail="Extraction flags"
          tone="warning"
        />
      </div>

      <div className="section-heading">
        <div>
          <p className="eyebrow">Filing queue</p>
          <h2>Recent filings</h2>
        </div>
        <div className="search-box">
          <Search size={16} />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search filenames"
          />
        </div>
      </div>

      <div className="filter-tabs">
        {["All", "Processing", "Ready", "Needs Review", "Failed"].map(
          (item) => (
            <button
              key={item}
              className={filter === item ? "filter-active" : ""}
              onClick={() => setFilter(item)}
            >
              {item}
            </button>
          ),
        )}
      </div>

      {error && (
        <Alert tone="danger">
          <AlertCircle size={16} />
          Unable to load filings. Check that the backend is running.
        </Alert>
      )}

      {isLoading ? (
        <div className="skeleton-grid">
          <div />
          <div />
          <div />
        </div>
      ) : visible.length ? (
        <>
          <div className={cn("filing-grid", isFetching && "is-fetching")}>
            {visible.map((item) => (
              <FilingCard key={item.id} document={item} />
            ))}
          </div>

          <div className="pagination">
            <Button
              variant="ghost"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || isFetching}
            >
              Previous
            </Button>
            <span>
              Page {page} of {totalPages}
            </span>
            <Button
              variant="ghost"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || isFetching}
            >
              Next
            </Button>
          </div>
        </>
      ) : (
        <EmptyState />
      )}
    </section>
  );
}

function Metric({
  icon,
  label,
  value,
  detail,
  tone,
}: {
  icon: ReactNode;
  label: string;
  value: number;
  detail: string;
  tone?: string;
}) {
  return (
    <Card className={cn("metric-card", tone)}>
      <div className="metric-icon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
    </Card>
  );
}
function FilingCard({ document }: { document: Document }) {
  const navigate = useNavigate();
  const isProcessing = ["queued", "processing"].includes(document.status);
  const progress = document.progress_percentage ?? 0;
  const hasProgress =
    typeof document.progress_percentage === "number" &&
    typeof document.current_page === "number" &&
    typeof document.total_pages === "number";

  return (
    <Card
      className="filing-card"
      onClick={() =>
        document.status === "completed"
          ? navigate(`/filings/${document.id}`)
          : undefined
      }
    >
      <CardHeader>
        <div className="file-mark">
          <FileText size={19} />
        </div>
        <Badge tone={statusTone(document.status)}>{document.status}</Badge>
      </CardHeader>
      <CardContent>
        <h3>{document.filename}</h3>
        <p>
          {new Date(document.created_at).toLocaleDateString(undefined, {
            month: "short",
            day: "numeric",
            year: "numeric",
          })}
          {document.page_count ? ` · ${document.page_count} pages` : ""}
        </p>

        {isProcessing && (
          <>
            <Progress
              value={hasProgress ? progress : undefined}
              indeterminate={!hasProgress}
            />
            {hasProgress && (
              <small className="progress-note">
                Page {document.current_page} / {document.total_pages} ·{" "}
                {progress}%
              </small>
            )}
          </>
        )}

        <div className="card-foot">
          <span>
            {document.status === "completed"
              ? "Open workspace"
              : document.status === "failed"
                ? "Extraction failed"
                : "Processing filing..."}
          </span>
          <ChevronRight size={15} />
        </div>
      </CardContent>
    </Card>
  );
}

function EmptyState() {
  return (
    <Card className="empty-state">
      <FolderOpen size={30} />
      <h3>No filings yet</h3>
      <p>Upload your first SERFF filing to begin extracting structured data.</p>
      <Link to="/upload">
        <Button>Upload a filing</Button>
      </Link>
    </Card>
  );
}

function UploadPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [working, setWorking] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  async function upload() {
    if (!file) return;
    setWorking(true);
    setError("");
    try {
      const response = await documentsApi.upload(file, setProgress);
      toast.success("Filing uploaded");
      await queryClient.invalidateQueries({ queryKey: ["documents"] });
      navigate(`/filings/${response.data.document_id}`);
    } catch (err) {
      setError(
        friendlyError(
          err,
          "Unable to upload this filing. Please verify the PDF and try again.",
        ),
      );
    } finally {
      setWorking(false);
    }
  }
  function choose(selected: File | undefined) {
    if (!selected) return;
    if (
      selected.type !== "application/pdf" &&
      !selected.name.toLowerCase().endsWith(".pdf")
    ) {
      setError("Only PDF filings are supported.");
      return;
    }
    if (selected.size > 50 * 1024 * 1024) {
      setError("This filing exceeds the 50 MB upload limit.");
      return;
    }
    setFile(selected);
    setError("");
  }
  return (
    <section className="upload-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">New filing</p>
          <h1>Upload a SERFF filing</h1>
          <p className="muted">
            The backend will validate, store, and process your PDF
            asynchronously.
          </p>
        </div>
        <Link to="/dashboard" className="back-link">
          Back to overview
        </Link>
      </div>
      {error && (
        <Alert tone="danger">
          <AlertCircle size={16} />
          {error}
        </Alert>
      )}
      <Card
        className={cn("drop-card", file && "has-file")}
        onClick={() => input.current?.click()}
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          choose(event.dataTransfer.files[0]);
        }}
      >
        <input
          ref={input}
          type="file"
          accept="application/pdf"
          hidden
          onChange={(event) => choose(event.target.files?.[0])}
        />
        {file ? (
          <>
            <div className="upload-icon success">
              <Check size={26} />
            </div>
            <h2>{file.name}</h2>
            <p>{formatBytes(file.size)} · PDF selected</p>
            <button
              className="text-button"
              onClick={(event) => {
                event.stopPropagation();
                setFile(null);
              }}
            >
              Choose a different file
            </button>
          </>
        ) : (
          <>
            <div className="upload-icon">
              <UploadCloud size={27} />
            </div>
            <h2>Drop your PDF here</h2>
            <p>or click to browse from your computer</p>
            <span className="drop-meta">PDF only · up to 50 MB</span>
          </>
        )}
      </Card>
      {file && (
        <Card className="upload-action">
          <div>
            <strong>Ready to process</strong>
            <span>Upload begins when you start extraction.</span>
          </div>
          <Button onClick={upload} disabled={working}>
            {working ? "Uploading..." : "Upload and extract"}
            <ChevronRight size={16} />
          </Button>
          {working && <Progress value={progress} />}
        </Card>
      )}
      <div className="upload-guidance">
        <ShieldCheck size={18} />
        <span>
          <strong>Your filing stays protected.</strong> Validation happens again
          on the backend and source evidence is retained for review.
        </span>
      </div>
    </section>
  );
}

type SidebarTab =
  | "structure"
  | "review"
  | "attachments"
  | "correspondence"
  | "history";

function FilingWorkspace() {
  const { id } = useParams();
  const [pickedVersion, setPickedVersion] = useState<number | null>(null);
  const [sidebarTab, setSidebarTab] = useState<SidebarTab>("structure");
  const [mobilePane, setMobilePane] = useState<
    "structure" | "content" | "source"
  >("content");

  const { data: filingData } = useQuery({
    queryKey: ["document", id],
    queryFn: async () => (await documentsApi.get(id!)).data,
    enabled: Boolean(id),
    refetchInterval: (query) =>
      ["queued", "processing"].includes(query.state.data?.status ?? "")
        ? 2000
        : false,
  });

  const { data: extractions, isLoading } = useQuery({
    queryKey: ["extractions", id],
    queryFn: async () => (await extractionApi.list(id!)).data,
    enabled: Boolean(id) && filingData?.status === "completed",
  });

  // Derive the current version instead of syncing it via an effect.
  const version = useMemo(() => {
    if (!extractions?.length) return 1;
    if (
      pickedVersion !== null &&
      extractions.some((item) => item.version === pickedVersion)
    ) {
      return pickedVersion;
    }
    return extractions[0].version;
  }, [extractions, pickedVersion]);

  const extraction =
    extractions?.find((item) => item.version === version) ?? extractions?.[0];
  const data = extraction?.structured_data;

  const review = useQuery({
    queryKey: ["review", id],
    queryFn: async () => (await reviewApi.get(id!)).data,
    enabled: Boolean(id) && filingData?.status === "completed",
  });

  const workspace = useWorkspaceStore();

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      const inField = ["INPUT", "TEXTAREA"].includes(target.tagName);

      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        document.querySelector<HTMLInputElement>(".filing-search")?.focus();
      }
      if (event.key === "Escape") workspace.setSearch("");
      if (!inField && event.key === "/") {
        event.preventDefault();
        document.querySelector<HTMLInputElement>(".filing-search")?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [workspace]);

  if (!filingData || filingData.status !== "completed" || isLoading || !data)
    return <ProcessingView document={filingData} id={id!} />;

  const sections = data.sections;
  const filteredSections = sections.filter((section) =>
    `${section.heading} ${section.text}`
      .toLowerCase()
      .includes(workspace.search.toLowerCase()),
  );
  const selected = sections[workspace.selectedSection] ?? sections[0];

  const reviewFlags = review.data?.flags ?? data.review_flags ?? [];

  const sidebarTabs: {
    key: SidebarTab;
    label: string;
    icon: ReactNode;
    badge?: number;
    tone?: "warning";
  }[] = [
    {
      key: "structure",
      label: "Tree",
      icon: <FolderOpen size={14} />,
      badge: sections.length,
    },
    {
      key: "review",
      label: "Review",
      icon: <AlertCircle size={14} />,
      badge: reviewFlags.length,
      tone: reviewFlags.length ? "warning" : undefined,
    },
    {
      key: "attachments",
      label: "Files",
      icon: <Paperclip size={14} />,
      badge: data.attachments.length,
    },
    {
      key: "correspondence",
      label: "Mail",
      icon: <FileText size={14} />,
      badge: data.correspondence.length,
    },
    {
      key: "history",
      label: "Runs",
      icon: <Gauge size={14} />,
      badge: extractions?.length ?? 0,
    },
  ];

  return (
    <section className="workspace-page">
      <div className="workspace-head">
        <div>
          <Link to="/dashboard" className="back-link">
            Overview
          </Link>
          <h1>{filingData.filename}</h1>
          <p className="muted">
            Extraction v{extraction?.version} · {data.snapshot.page_count}{" "}
            source pages · Extraction confidence{" "}
            {Math.round(data.snapshot.average_confidence * 100)}%
          </p>
        </div>
        <ExportMenu id={id!} data={data} />
      </div>

      <Snapshot document={filingData} data={data} />

      <div className="mobile-panes">
        {(["structure", "content", "source"] as const).map((pane) => (
          <button
            key={pane}
            className={mobilePane === pane ? "active" : ""}
            onClick={() => setMobilePane(pane)}
          >
            {pane}
          </button>
        ))}
      </div>

      <div className="review-workspace">
        {/* LEFT: sidebar with tabs */}
        <aside
          className={cn(
            "workspace-pane structure-pane",
            mobilePane !== "structure" && "mobile-hidden",
          )}
        >
          <div className="sidebar-tabs">
            {sidebarTabs.map((t) => (
              <button
                key={t.key}
                className={cn(sidebarTab === t.key && "active")}
                onClick={() => setSidebarTab(t.key)}
                title={t.label}
              >
                {t.icon}
                <span className="tab-label">{t.label}</span>
                {t.badge !== undefined && t.badge > 0 && (
                  <span
                    className={cn(
                      "tab-badge",
                      t.tone === "warning" && "tab-badge-warning",
                    )}
                  >
                    {t.badge}
                  </span>
                )}
              </button>
            ))}
          </div>

          <div className="pane-scroll">
            {sidebarTab === "structure" && (
              <>
                {sections.map((section, index) => (
                  <button
                    key={`${section.heading}-${index}`}
                    className={cn(
                      "tree-item",
                      workspace.selectedSection === index && "tree-selected",
                    )}
                    onClick={() =>
                      workspace.setSelected(index, section.page_start)
                    }
                  >
                    <span className="tree-line" />
                    <span className="tree-copy">
                      <strong>{section.heading}</strong>
                      <small>
                        {section.level} · p. {section.page_start}
                      </small>
                    </span>
                    <Confidence value={section.confidence} />
                  </button>
                ))}
              </>
            )}

            {sidebarTab === "review" && <ReviewPanel flags={reviewFlags} />}
            {sidebarTab === "attachments" && <AttachmentPanel data={data} />}
            {sidebarTab === "correspondence" && (
              <CorrespondencePanel data={data} />
            )}
            {sidebarTab === "history" && (
              <HistoryPanel
                id={id!}
                versions={extractions ?? []}
                version={version}
                setVersion={setPickedVersion}
              />
            )}
          </div>
        </aside>

        {/* CENTER: content */}
        <main
          className={cn(
            "workspace-pane content-pane",
            mobilePane !== "content" && "mobile-hidden",
          )}
        >
          <PaneTitle
            icon={<FileText size={15} />}
            label="Extracted content"
            count={filteredSections.length}
          />
          <div className="content-tools">
            <div className="search-box full">
              <Search size={16} />
              <Input
                className="filing-search"
                value={workspace.search}
                onChange={(event) => workspace.setSearch(event.target.value)}
                placeholder="Search this filing..."
              />
            </div>
            <button
              className="copy-button"
              onClick={() => {
                navigator.clipboard.writeText(
                  JSON.stringify(selected, null, 2),
                );
                toast.success("Section JSON copied");
              }}
            >
              <Copy size={15} /> Copy section
            </button>
          </div>
          <div className="pane-scroll content-scroll">
            {workspace.search && (
              <p className="search-note">
                Showing {filteredSections.length} sections matching “
                {workspace.search}”
              </p>
            )}
            {filteredSections.map((section) => (
              <SectionArticle
                key={`${section.heading}-${section.page_start}`}
                section={section}
                active={section === selected}
                onClick={() => {
                  const index = sections.indexOf(section);
                  workspace.setSelected(index, section.page_start);
                  workspace.setPane("source");
                }}
              />
            ))}
          </div>
        </main>

        {/* RIGHT: source */}
        <aside
          className={cn(
            "workspace-pane source-pane",
            mobilePane !== "source" && "mobile-hidden",
          )}
        >
          <PaneTitle icon={<Gauge size={15} />} label="Source evidence" />
          <SourceViewer
            key={selected?.page_start ?? "empty"}
            data={data}
            selected={selected}
          />
        </aside>
      </div>
    </section>
  );
}

function PaneTitle({
  icon,
  label,
  count,
}: {
  icon: ReactNode;
  label: string;
  count?: number;
}) {
  return (
    <div className="pane-title">
      <span>
        {icon}
        {label}
      </span>
      {count !== undefined && <Badge>{count}</Badge>}
    </div>
  );
}
function Confidence({ value }: { value: number }) {
  const percent = Math.round(value * 100);
  return (
    <Badge
      tone={percent >= 85 ? "success" : percent >= 65 ? "warning" : "danger"}
    >
      {percent}%
    </Badge>
  );
}
function SectionArticle({
  section,
  active,
  onClick,
}: {
  section: Section;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <article
      className={cn("section-article", active && "article-active")}
      onClick={onClick}
    >
      <div className="article-meta">
        <Badge tone="info">{section.section_type.replaceAll("_", " ")}</Badge>
        <span>
          Page {section.page_start}
          {section.page_end !== section.page_start
            ? `–${section.page_end}`
            : ""}
        </span>
        <Confidence value={section.confidence} />
      </div>
      <h2>{section.heading}</h2>
      <p>{section.text || "No body text was extracted for this section."}</p>
    </article>
  );
}
function SourceViewer({
  data,
  selected,
}: {
  data: StructuredData;
  selected?: Section;
}) {
  const total = data.snapshot.page_count;
  const initialPage = selected?.source?.page ?? selected?.page_start ?? 1;
  const [page, setPage] = useState(initialPage);
  const source = data.pages.find((item) => item.page === page);

  // The section that was clicked lives on its own page — bbox callout
  // should only show there, not on other pages the user navigates to.
  const selectedPage = selected?.source?.page ?? selected?.page_start;

  const go = (next: number) => {
    if (next < 1 || next > total) return;
    setPage(next);
  };

  return (
    <div className="source-view">
      <div className="source-view-body">
        <div className="source-toolbar">
          <span>Source page</span>
          <strong>
            {page} / {total}
          </strong>
        </div>
        <div className="source-paper">
          <div className="paper-top">
            <span>FilingLens evidence</span>
            <span>Page {page}</span>
          </div>
          <p>{source?.text || "Source text is unavailable for this page."}</p>
          {selected?.source?.bbox && page === selectedPage && (
            <div className="evidence-callout">
              <span />
              Bounding box available for “{selected.heading}”
            </div>
          )}
        </div>
        <p className="source-note">
          Evidence is linked to the original extraction page. PDF rendering
          becomes available when the backend exposes a source file endpoint.
        </p>
      </div>

      <div className="source-pager">
        <button
          type="button"
          onClick={() => go(page - 1)}
          disabled={page <= 1}
          aria-label="Previous page"
        >
          <ChevronLeft size={14} />
        </button>
        <span>
          Page {page} of {total}
        </span>
        <button
          type="button"
          onClick={() => go(page + 1)}
          disabled={page >= total}
          aria-label="Next page"
        >
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  );
}

function Snapshot({
  document,
  data,
}: {
  document: Document;
  data: StructuredData;
}) {
  const metadata = Object.entries(data.metadata).slice(0, 4);
  return (
    <Card className="snapshot-card">
      <div className="snapshot-title">
        <div>
          <p className="eyebrow">Filing snapshot</p>
          <h2>
            {metadata.find(([key]) => key === "company")?.[1].value ||
              document.filename}
          </h2>
          <span>
            {metadata.find(([key]) => key === "state")?.[1].value ||
              "State not detected"}{" "}
            · {data.snapshot.page_count} pages
          </span>
        </div>
        <Badge tone="success">
          <Check size={13} /> Extraction complete
        </Badge>
      </div>
      <Separator />
      <div className="snapshot-metrics">
        <SnapshotMetric label="Sections" value={data.snapshot.section_count} />
        <SnapshotMetric label="Tables" value={data.snapshot.table_count} />
        <SnapshotMetric
          label="Attachments"
          value={data.snapshot.attachment_count}
        />
        <SnapshotMetric
          label="Confidence"
          value={`${Math.round(data.snapshot.average_confidence * 100)}%`}
        />
      </div>
      <div className="metadata-strip">
        {metadata.map(([key, value]) => (
          <div key={key}>
            <span>{key.replaceAll("_", " ")}</span>
            <strong>{value.value}</strong>
          </div>
        ))}
      </div>
    </Card>
  );
}
function SnapshotMetric({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
function ProcessingView({ document, id }: { document?: Document; id: string }) {
  const navigate = useNavigate();
  const retry = async () => {
    try {
      await documentsApi.extract(id);
      toast.success("Extraction started");
    } catch {
      toast.error("We could not start extraction. Please try again.");
    }
  };
  return (
    <section className="processing-page">
      <div className="processing-orbit">
        <Gauge size={34} />
      </div>
      <p className="eyebrow">Filing workspace</p>
      <h1>
        {document?.status === "failed"
          ? "Extraction needs attention"
          : "Processing your filing"}
      </h1>
      <p className="muted">
        {document?.filename || "Your filing"} ·{" "}
        {document?.status === "failed"
          ? "The backend reported a failure."
          : "Analyzing structure, evidence, and SERFF signals."}
      </p>
      {document?.status === "failed" ? (
        <>
          <Alert tone="danger">
            <AlertCircle size={16} />
            We couldn't extract this filing. You can retry extraction.
          </Alert>
          <div className="processing-actions">
            <Button onClick={retry}>Retry extraction</Button>
            <Button variant="ghost" onClick={() => navigate("/dashboard")}>
              Back to dashboard
            </Button>
          </div>
        </>
      ) : (
        <>
          <Progress indeterminate />
          <div className="processing-status">
            <span>Status</span>
            <Badge tone="info">{document?.status || "queued"}</Badge>
          </div>
          <p className="muted small">
            Live page progress is shown when the backend exposes it.
          </p>
        </>
      )}
    </section>
  );
}
// function WorkspaceBottom({
//   data,
//   versions,
//   version,
//   setVersion,
// }: {
//   data: StructuredData;
//   versions: Extraction[];
//   version: number;
//   setVersion: (value: number) => void;
// }) {
//   const id = useParams().id!;
//   const [tab, setTab] = useState<
//     "radar" | "attachments" | "correspondence" | "history"
//   >("radar");
//   return (
//     <div className="workspace-bottom">
//       <div className="bottom-tabs">
//         {[
//           ["radar", "Review Radar"],
//           ["attachments", `Attachments ${data.attachments.length}`],
//           ["correspondence", `Correspondence ${data.correspondence.length}`],
//           ["history", `History ${versions.length}`],
//         ].map(([key, label]) => (
//           <button
//             key={key}
//             className={tab === key ? "active" : ""}
//             onClick={() => setTab(key as typeof tab)}
//           >
//             {label}
//           </button>
//         ))}
//       </div>
//       {tab === "radar" && <ReviewPanel flags={data.review_flags} />}
//       {tab === "attachments" && <AttachmentPanel data={data} />}
//       {tab === "correspondence" && <CorrespondencePanel data={data} />}
//       {tab === "history" && (
//         <HistoryPanel
//           id={id}
//           versions={versions}
//           version={version}
//           setVersion={setVersion}
//         />
//       )}
//     </div>
//   );
// }
function ReviewPanel({ flags }: { flags: ReviewFlag[] }) {
  return (
    <div className="bottom-content">
      {flags.length ? (
        flags.map((flag, index) => (
          <div className="radar-item" key={`${flag.type}-${index}`}>
            <AlertCircle size={16} />
            <div>
              <Badge tone={flag.severity === "medium" ? "warning" : "info"}>
                {flag.severity}
              </Badge>
              <strong>{flag.message}</strong>
              <span>
                {flag.page ? `Page ${flag.page}` : "Filing-wide signal"}
                {flag.confidence
                  ? ` · ${Math.round(flag.confidence * 100)}% confidence`
                  : ""}
              </span>
            </div>
          </div>
        ))
      ) : (
        <div className="empty-inline">
          <Check size={17} /> No extraction issues detected.
        </div>
      )}
    </div>
  );
}
function AttachmentPanel({ data }: { data: StructuredData }) {
  return (
    <div className="bottom-content record-grid">
      {data.attachments.length ? (
        data.attachments.map((item, index) => (
          <div className="record-row" key={`${item.name}-${index}`}>
            <Paperclip size={15} />
            <div>
              <strong>{item.name}</strong>
              <span>
                {item.category.replaceAll("_", " ")} · Page {item.page ?? "—"}
              </span>
            </div>
            <Confidence value={item.confidence} />
          </div>
        ))
      ) : (
        <div className="empty-inline">
          No attachments were detected in this filing.
        </div>
      )}
    </div>
  );
}
function CorrespondencePanel({ data }: { data: StructuredData }) {
  return (
    <div className="bottom-content timeline">
      {data.correspondence.length ? (
        data.correspondence.map((item, index) => (
          <div className="timeline-item" key={`${item.type}-${index}`}>
            <span className="timeline-dot" />
            <div>
              <Badge tone="info">{item.type.replaceAll("_", " ")}</Badge>
              <strong>{item.text}</strong>
              <span>
                Page {item.page ?? "—"} · {item.status}
              </span>
            </div>
          </div>
        ))
      ) : (
        <div className="empty-inline">
          No correspondence was detected in this filing.
        </div>
      )}
    </div>
  );
}
function HistoryPanel({
  versions,
  version,
  setVersion,
}: {
  id: string;
  versions: Extraction[];
  version: number;
  setVersion: (value: number) => void;
}) {
  return (
    <div className="bottom-content history-list">
      {versions.map((item) => (
        <button
          key={item.version}
          className={item.version === version ? "history-active" : ""}
          onClick={() => setVersion(item.version)}
        >
          <span>Version {item.version}</span>
          <Badge tone={item.version === version ? "success" : "neutral"}>
            {item.strategy}
          </Badge>
          <small>
            {item.confidence_summary.section_count} sections ·{" "}
            {item.confidence_summary.page_count} pages
          </small>
        </button>
      ))}
    </div>
  );
}
function ExportMenu({ id, data }: { id: string; data: StructuredData }) {
  const [open, setOpen] = useState(false);
  async function exportFile(format: ExportFormat) {
    try {
      await downloadExport(id, format);
      toast.success(`${format.toUpperCase()} export ready`);
    } catch {
      toast.error("Unable to generate this export.");
    } finally {
      setOpen(false);
    }
  }
  return (
    <div className="export-wrap">
      <Button variant="secondary" onClick={() => setOpen((value) => !value)}>
        <Download size={16} /> Export
      </Button>
      {open && (
        <div className="export-menu">
          {(["json", "csv", "markdown"] as ExportFormat[]).map((format) => (
            <button key={format} onClick={() => void exportFile(format)}>
              {format.toUpperCase()}
              <small>
                {format === "json"
                  ? "Full structured data"
                  : format === "csv"
                    ? "Flattened records"
                    : "Review-ready document"}
              </small>
            </button>
          ))}
          <button
            onClick={() => {
              navigator.clipboard.writeText(JSON.stringify(data, null, 2));
              toast.success("Full extraction copied");
              setOpen(false);
            }}
          >
            <Copy size={14} /> Copy JSON
          </button>
        </div>
      )}
    </div>
  );
}
function statusGroup(status: string) {
  if (["queued", "processing"].includes(status)) return "Processing";
  if (status === "completed") return "Ready";
  if (status === "failed") return "Failed";
  return "All";
}
function statusTone(
  status: string,
): "neutral" | "success" | "warning" | "danger" | "info" {
  if (status === "completed") return "success";
  if (status === "failed") return "danger";
  if (["queued", "processing"].includes(status)) return "info";
  return "neutral";
}
function NotFound() {
  return (
    <main className="not-found">
      <FileText size={36} />
      <h1>Page not found</h1>
      <Link to="/dashboard">
        <Button>Return to workspace</Button>
      </Link>
    </main>
  );
}

export default App;
