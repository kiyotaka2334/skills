import * as React from "react";

export interface SizeOption {
  label: string;
  /** Optional price bump for extended sizes, e.g. 3 for "+$3". */
  upcharge?: number;
}

export interface SizePickerProps {
  /** Group label, e.g. "Size". */
  label?: string;
  sizes: SizeOption[];
  /** Selected size label. */
  value?: string;
  onChange?: (label: string) => void;
  /** Fit note shown under the row, e.g. "Between sizes? Size down." */
  note?: string;
}

/**
 * Size selector row. Square-ish buttons, selected gets a pine-green
 * border. Always pair with an honest fit note and a size-guide link —
 * sizing anxiety is the top conversion killer for gift buyers.
 */
export function SizePicker({ label = "Size", sizes, value, onChange, note }: SizePickerProps) {
  const [internal, setInternal] = React.useState<string | undefined>(value);
  const selected = value ?? internal;
  return (
    <div className="cc-option-group">
      <span className="cc-option-group__label">
        {label} — <strong>{selected ?? "select one"}</strong>
      </span>
      <div className="cc-size-row" role="group" aria-label={label}>
        {sizes.map((s) => (
          <button
            key={s.label}
            type="button"
            className="cc-size-btn"
            aria-pressed={s.label === selected}
            onClick={() => {
              setInternal(s.label);
              onChange?.(s.label);
            }}
          >
            {s.label}
          </button>
        ))}
      </div>
      {note ? <p className="cc-option-group__note">{note}</p> : null}
    </div>
  );
}
