import { useState } from "react"
import { ApiError } from "../api"
import { Icon } from "./Icon"

export function reportDelete(caught: unknown) {
  window.alert(caught instanceof ApiError ? caught.message : "Could not delete that.")
}

export function DeleteButton({
  label,
  disabled,
  onDelete,
  className = "",
}: {
  label: string
  disabled?: boolean
  onDelete: () => void
  className?: string
}) {
  const [armed, setArmed] = useState(false)
  return (
    <button
      type="button"
      aria-label={armed ? `Confirm delete ${label}` : `Delete ${label}`}
      disabled={disabled}
      onClick={() => {
        if (!armed) {
          setArmed(true)
          return
        }
        onDelete()
      }}
      onBlur={() => setArmed(false)}
      className={`inline-grid place-items-center rounded-md text-mist/70 transition hover:bg-ember/10 hover:text-ember disabled:opacity-40 ${armed ? "h-7 px-2 text-xs font-medium text-ember" : "h-7 w-7"} ${className}`}
    >
      {armed ? "Delete" : <Icon name="trash" className="h-3.5 w-3.5" />}
    </button>
  )
}
