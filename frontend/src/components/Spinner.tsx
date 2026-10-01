export function Spinner({ className = "border-white/40 border-t-white" }: { className?: string }) {
  return <span aria-hidden className={`inline-block h-3.5 w-3.5 shrink-0 animate-spin rounded-full border-2 ${className}`} />
}
