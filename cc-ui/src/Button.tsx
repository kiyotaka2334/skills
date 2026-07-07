import * as React from "react";

export interface ButtonProps {
  /** Visual weight. `primary` is the pine-green fill; `ghost` is the outlined variant. */
  variant?: "primary" | "ghost";
  /** Stretch to the container's full width (mobile buy buttons). */
  fullWidth?: boolean;
  /** Render as an anchor when set — the design system's CTAs are usually links. */
  href?: string;
  onClick?: React.MouseEventHandler;
  disabled?: boolean;
  children: React.ReactNode;
}

/**
 * The Court & Clover call-to-action. Pine-green fill with cream text, subtle
 * 3px radius (never a pill — pill reads casual, not heritage). One primary
 * button per view; pair with a ghost button for secondary actions.
 */
export function Button({ variant = "primary", fullWidth, href, onClick, disabled, children }: ButtonProps) {
  const cls = ["cc-btn", variant === "ghost" ? "cc-btn--ghost" : "", fullWidth ? "cc-btn--full" : ""]
    .filter(Boolean)
    .join(" ");
  if (href && !disabled) {
    return (
      <a className={cls} href={href} onClick={onClick}>
        {children}
      </a>
    );
  }
  return (
    <button type="button" className={cls} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}
