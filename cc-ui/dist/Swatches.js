import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import * as React from "react";
/**
 * Named color swatches for product options. Each swatch shows the dot AND
 * the color name — the demographic reads labels, not just chips. The
 * selected swatch gets a pine-green border.
 */
export function Swatches({ label = "Color", options, value, onChange }) {
    var _a;
    const [internal, setInternal] = React.useState(value !== null && value !== void 0 ? value : (_a = options[0]) === null || _a === void 0 ? void 0 : _a.name);
    const selected = value !== null && value !== void 0 ? value : internal;
    return (_jsxs("div", { className: "cc-option-group", children: [_jsxs("span", { className: "cc-option-group__label", children: [label, " \u2014 ", _jsx("strong", { children: selected })] }), _jsx("div", { className: "cc-swatch-row", role: "group", "aria-label": label, children: options.map((o) => (_jsxs("button", { type: "button", className: "cc-swatch", "aria-pressed": o.name === selected, onClick: () => {
                        setInternal(o.name);
                        onChange === null || onChange === void 0 ? void 0 : onChange(o.name);
                    }, children: [_jsx("span", { className: "cc-swatch__dot", style: { background: o.hex } }), " ", o.name] }, o.name))) })] }));
}
