import type { ReactNode } from "react";

/** Wraps native date/time pickers — hides OS arrow and draws our own inset chevron. */
export function FormPickerShell({ children }: { children: ReactNode }) {
  return (
    <div className="form-input-shell">
      <div className="form-input-shell__field">{children}</div>
    </div>
  );
}
