import * as React from "react";

export interface EmailCaptureProps {
  /** Lead with the incentive, e.g. "10% off your first order" — never "join our newsletter". */
  heading: string;
  description?: string;
  buttonLabel?: string;
  onSubmit?: (email: string) => void;
}

/**
 * Pine-green email capture band with a brass submit button. The heading
 * carries a real incentive; the confirmation replaces vague promises with
 * a concrete next step.
 */
export function EmailCapture({ heading, description, buttonLabel = "Get 10% off", onSubmit }: EmailCaptureProps) {
  const [msg, setMsg] = React.useState("");
  const inputRef = React.useRef<HTMLInputElement>(null);
  return (
    <section className="cc-email-capture">
      <h2>{heading}</h2>
      {description ? <p>{description}</p> : null}
      <form
        className="cc-email-form"
        onSubmit={(e) => {
          e.preventDefault();
          const v = inputRef.current?.value ?? "";
          if (!v) return;
          setMsg(`You're in. Check ${v} for your welcome code.`);
          onSubmit?.(v);
        }}
      >
        <label className="cc-visually-hidden" htmlFor="cc-email-input">
          Email address
        </label>
        <input id="cc-email-input" ref={inputRef} type="email" placeholder="you@example.com" required />
        <button className="cc-btn cc-btn--brass" type="submit">
          {buttonLabel}
        </button>
      </form>
      <p className="cc-email-form__msg" role="status">
        {msg}
      </p>
    </section>
  );
}
