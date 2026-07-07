import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * The Court & Clover wordmark: four-leaf clover mark plus the name set in
 * Playfair Display. Use `onDark` on pine-green surfaces.
 */
export function Logo({ onDark, href = "/" }) {
    return (_jsxs("a", { className: onDark ? "cc-logo cc-logo--on-dark" : "cc-logo", href: href, children: [_jsxs("svg", { viewBox: "0 0 64 64", "aria-hidden": "true", fill: "currentColor", children: [_jsx("circle", { cx: "25", cy: "24", r: "10" }), _jsx("circle", { cx: "39", cy: "24", r: "10" }), _jsx("circle", { cx: "25", cy: "38", r: "10" }), _jsx("circle", { cx: "39", cy: "38", r: "10" }), _jsx("rect", { x: "30.5", y: "34", width: "3", height: "22", rx: "1.5", transform: "rotate(18 32 34)" })] }), "Court & Clover"] }));
}
