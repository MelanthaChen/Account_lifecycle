import { create } from "zustand";

export type ToastTone = "success" | "error" | "info";

export interface ToastMessage {
  id: string;
  message: string;
  tone: ToastTone;
}

interface ToastState {
  messages: ToastMessage[];
  dismiss: (id: string) => void;
  notify: (message: string, tone?: ToastTone) => void;
}

export const useToast = create<ToastState>((set) => ({
  messages: [],
  dismiss: (id) => set((state) => ({ messages: state.messages.filter((toast) => toast.id !== id) })),
  notify: (message, tone = "info") => {
    const id = crypto.randomUUID();
    set((state) => ({ messages: [...state.messages, { id, message, tone }] }));
    window.setTimeout(() => {
      set((state) => ({ messages: state.messages.filter((toast) => toast.id !== id) }));
    }, 3500);
  }
}));
