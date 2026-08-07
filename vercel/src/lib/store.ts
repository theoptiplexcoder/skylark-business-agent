import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
}

interface Workspace {
  id: string;
  name: string;
  connectedBoards: number;
}

interface AppState {
  user: User | null;
  workspace: Workspace | null;
  isAuthenticated: boolean;
  isSidebarOpen: boolean;
  setUser: (user: User | null) => void;
  setWorkspace: (workspace: Workspace | null) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  workspace: { id: "ws-1", name: "Acme Corp", connectedBoards: 3 }, // Mock workspace
  isAuthenticated: false,
  isSidebarOpen: true,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  setWorkspace: (workspace) => set({ workspace }),
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (isOpen) => set({ isSidebarOpen: isOpen }),
}));
