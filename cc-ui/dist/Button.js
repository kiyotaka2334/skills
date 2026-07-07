import { jsx as _jsx } from "react/jsx-runtime";
/**
 * The Court & Clover call-to-action. Pine-green fill with cream text, subtle
 * 3px radius (never a pill — pill reads casual, not heritage). One primary
 * button per view; pair with a ghost button for secondary actions.
 */
export function Button({ variant = "primary", fullWidth, href, onClick, disabled, children }) {
    const cls = ["cc-btn", variant === "ghost" ? "cc-btn--ghost" : "", fullWidth ? "cc-btn--full" : ""]
        .filter(Boolean)
        .join(" ");
    if (href && !disabled) {
        return (_jsx("a", { className: cls, href: href, onClick: onClick, children: children }));
    }
    return (_jsx("button", { type: "button", className: cls, onClick: onClick, disabled: disabled, children: children }));
}
