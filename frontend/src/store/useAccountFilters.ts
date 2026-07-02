import { create } from "zustand";

interface AccountFiltersState {
  search: string;
  setSearch: (search: string) => void;
}

export const useAccountFilters = create<AccountFiltersState>((set) => ({
  search: "",
  setSearch: (search) => set({ search })
}));
