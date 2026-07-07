import { jsx as _jsx } from "react/jsx-runtime";
/**
 * Wide letter-spaced brass caps that label a section ("THE COLLECTION",
 * "OUR STORY"). Always sits above a Playfair heading, never alone.
 */
export function Eyebrow({ children }) {
    return _jsx("p", { className: "cc-eyebrow", children: children });
}
