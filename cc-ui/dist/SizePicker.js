import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import * as React from "react";
/**
 * Size selector row. Square-ish buttons, selected gets a pine-green
 * border. Always pair with an honest fit note and a size-guide link —
 * sizing anxiety is the top conversion killer for gift buyers.
 */
export function SizePicker({ label = "Size", sizes, value, onChange, note }) {
    const [internal, setInternal] = React.useState(value);
    const selected = value !== null && value !== void 0 ? value : internal;
    return (_jsxs("div", { className: "cc-option-group", children: [_jsxs("span", { className: "cc-option-group__label", children: [label, " \u2014 ", _jsx("strong", { children: selected !== null && selected !== void 0 ? selected : "select one" })] }), _jsx("div", { className: "cc-size-row", role: "group", "aria-label": label, children: sizes.map((s) => (_jsx("button", { type: "button", className: "cc-size-btn", "aria-pressed": s.label === selected, onClick: () => {
                        setInternal(s.label);
                        onChange === null || onChange === void 0 ? void 0 : onChange(s.label);
                    }, children: s.label }, s.label))) }), note ? _jsx("p", { className: "cc-option-group__note", children: note }) : null] }));
}
