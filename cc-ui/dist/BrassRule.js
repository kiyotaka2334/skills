import { jsx as _jsx } from "react/jsx-runtime";
/**
 * The brand's only ornament: a short 1px brass rule used under headings and
 * between sections. Use sparingly — one per section at most.
 */
export function BrassRule({ align = "center" }) {
    return _jsx("hr", { className: align === "left" ? "cc-brass-rule cc-brass-rule--left" : "cc-brass-rule" });
}
