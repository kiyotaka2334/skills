import { jsx as _jsx } from "react/jsx-runtime";
/**
 * Full-width editorial strip between brass rules — one italic Playfair
 * line of brand voice. Used mid-grid to turn a thin collection into
 * intentional restraint.
 */
export function EditorialBand({ children }) {
    return (_jsx("div", { className: "cc-editorial-band", children: _jsx("p", { children: children }) }));
}
