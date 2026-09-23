import { create } from "zustand";
type WorkspaceState = {
  selectedSection: number;
  selectedPage: number | null;
  search: string;
  pane: "structure" | "content" | "source";
  setSelected: (section: number, page?: number) => void;
  setSearch: (search: string) => void;
  setPane: (pane: WorkspaceState["pane"]) => void;
};
export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  selectedSection: 0,
  selectedPage: null,
  search: "",
  pane: "content",
  setSelected: (selectedSection, selectedPage) =>
    set({
      selectedSection,
      selectedPage: selectedPage ?? null,
      pane: "content",
    }),
  setSearch: (search) => set({ search }),
  setPane: (pane) => set({ pane }),
}));
