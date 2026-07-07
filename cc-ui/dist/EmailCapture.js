import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import * as React from "react";
/**
 * Pine-green email capture band with a brass submit button. The heading
 * carries a real incentive; the confirmation replaces vague promises with
 * a concrete next step.
 */
export function EmailCapture({ heading, description, buttonLabel = "Get 10% off", onSubmit }) {
    const [msg, setMsg] = React.useState("");
    const inputRef = React.useRef(null);
    return (_jsxs("section", { className: "cc-email-capture", children: [_jsx("h2", { children: heading }), description ? _jsx("p", { children: description }) : null, _jsxs("form", { className: "cc-email-form", onSubmit: (e) => {
                    var _a, _b;
                    e.preventDefault();
                    const v = (_b = (_a = inputRef.current) === null || _a === void 0 ? void 0 : _a.value) !== null && _b !== void 0 ? _b : "";
                    if (!v)
                        return;
                    setMsg(`You're in. Check ${v} for your welcome code.`);
                    onSubmit === null || onSubmit === void 0 ? void 0 : onSubmit(v);
                }, children: [_jsx("label", { className: "cc-visually-hidden", htmlFor: "cc-email-input", children: "Email address" }), _jsx("input", { id: "cc-email-input", ref: inputRef, type: "email", placeholder: "you@example.com", required: true }), _jsx("button", { className: "cc-btn cc-btn--brass", type: "submit", children: buttonLabel })] }), _jsx("p", { className: "cc-email-form__msg", role: "status", children: msg })] }));
}
