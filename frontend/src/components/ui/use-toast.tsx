import * as React from "react";
import { Toast, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport } from "@/components/ui/toast";

interface ToastProps {
  title?: string;
  description?: string;
  variant?: "default" | "destructive";
}

const ToastContext = React.createContext<{
  toast: (props: ToastProps) => void;
}>({
  toast: () => {},
});

export function ToastContainer({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastProps[]>([]);

  const toast = React.useCallback(
    (props: ToastProps) => {
      setToasts((prev) => [...prev, props]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((_, i) => i !== 0));
      }, 5000);
    },
    []
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <ToastProvider>
        {toasts.map((toast, index) => (
          <Toast key={index} className={toast.variant === "destructive" ? "destructive" : ""}>
            {toast.title && <ToastTitle>{toast.title}</ToastTitle>}
            {toast.description && <ToastDescription>{toast.description}</ToastDescription>}
            <ToastClose />
          </Toast>
        ))}
        <ToastViewport />
      </ToastProvider>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const { toast } = React.useContext(ToastContext);
  return {toast} ;
}