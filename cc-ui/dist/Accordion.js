import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Brass-hairline accordion for secondary content — fabric & care, FAQ,
 * returns. Native `<details>` semantics; the marker is a brass +/−.
 */
export function Accordion({ items, defaultOpen }) {
    return (_jsx("div", { className: "cc-accordion", children: items.map((it, i) => (_jsxs("details", { open: i === defaultOpen, children: [_jsx("summary", { children: it.title }), _jsx("div", { className: "cc-accordion__body", children: it.content })] }, it.title))) }));
}
