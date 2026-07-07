import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Brass-ruled specification table — the size chart. Numbers centered,
 * first column is the row label. Wrap in a horizontally scrollable
 * container on narrow screens (the component does this itself).
 */
export function SpecTable({ caption, columns, rows }) {
    return (_jsx("div", { className: "cc-table-scroll", children: _jsxs("table", { className: "cc-spec-table", children: [caption ? _jsx("caption", { children: caption }) : null, _jsx("thead", { children: _jsx("tr", { children: columns.map((c) => (_jsx("th", { scope: "col", children: c }, c))) }) }), _jsx("tbody", { children: rows.map((r, i) => (_jsx("tr", { children: r.map((cell, j) => j === 0 ? (_jsx("th", { scope: "row", children: cell }, j)) : (_jsx("td", { children: cell }, j))) }, i))) })] }) }));
}
