import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Centered page header: eyebrow, oversized Playfair title, optional
 * sub-line, closed by a brass rule. Opens every top-level page.
 */
export function PageHead({ eyebrow, title, children }) {
    return (_jsxs("div", { className: "cc-page-head", children: [eyebrow ? _jsx("p", { className: "cc-eyebrow", children: eyebrow }) : null, _jsx("h1", { children: title }), children ? _jsx("p", { className: "cc-page-head__sub", children: children }) : null, _jsx("hr", { className: "cc-brass-rule" })] }));
}
