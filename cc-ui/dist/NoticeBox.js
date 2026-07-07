import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Brass-bordered inline notice with a clock icon — the made-to-order
 * timeline block. Conversion-critical on product pages: state production
 * and delivery windows explicitly.
 */
export function NoticeBox({ title, children }) {
    return (_jsxs("div", { className: "cc-notice", children: [_jsxs("svg", { viewBox: "0 0 24 24", fill: "none", stroke: "#B8893E", strokeWidth: 1.6, "aria-hidden": "true", children: [_jsx("circle", { cx: "12", cy: "12", r: "9" }), _jsx("path", { d: "M12 7v5l3.5 2" })] }), _jsxs("p", { children: [title ? _jsxs("strong", { children: [title, " "] }) : null, children] })] }));
}
