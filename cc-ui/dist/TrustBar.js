import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Thin pine-green strip of store promises in letter-spaced caps, shown
 * under the hero. Keep each item to a few words; three items max.
 */
export function TrustBar({ items }) {
    return (_jsx("div", { className: "cc-trust-bar", role: "note", children: _jsx("ul", { children: items.map((t) => (_jsxs("li", { children: [_jsx("svg", { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, "aria-hidden": "true", children: _jsx("path", { d: "M12 3l2.5 5 5.5.8-4 3.9.9 5.5-4.9-2.6-4.9 2.6.9-5.5-4-3.9 5.5-.8z" }) }), t] }, t))) }) }));
}
