import { useState, useEffect, useCallback } from 'react';
import { ToastContext } from '../hooks/useToast';

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map((toast) => (
          <Toast key={toast.id} toast={toast} onRemove={removeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function Toast({ toast, onRemove }) {
  useEffect(() => {
    const timer = setTimeout(() => onRemove(toast.id), 4000);
    return () => clearTimeout(timer);
  }, [toast.id, onRemove]);

  const bgColor = {
    error: 'bg-red-950/90 border-red-500/50 text-red-300',
    success: 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300',
    info: 'bg-slate-900/90 border-slate-700 text-slate-300',
  }[toast.type] || 'bg-slate-900/90 border-slate-700 text-slate-300';

  return (
    <div
      className={`rounded-lg border px-4 py-3 shadow-lg font-mono text-xs max-w-sm animate-in fade-in slide-in-from-right-4 duration-300 ${bgColor}`}
    >
      <div className="flex items-center justify-between gap-3">
        <span>{toast.message}</span>
        <button
          onClick={() => onRemove(toast.id)}
          className="text-slate-500 hover:text-slate-300 transition-colors"
        >
          ×
        </button>
      </div>
    </div>
  );
}
