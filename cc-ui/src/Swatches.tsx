import * as React from "react";

export interface SwatchOption {
  /** Human color name — swatches are always named, never bare dots. */
  name: string;
  /** CSS color for the dot. */
  hex: string;
}

export interface SwatchesProps {
  /** Group label, e.g. "Color". */
  label?: string;
  options: SwatchOption[];
  /** Selected option name. */
  value?: string;
  onChange?: (name: string) => void;
}

/**
 * Named color swatches for product options. Each swatch shows the dot AND
 * the color name — the demographic reads labels, not just chips. The
 * selected swatch gets a pine-green border.
 */
export function Swatches({ label = "Color", options, value, onChange }: SwatchesProps) {
  const [internal, setInternal] = React.useState(value ?? options[0]?.name);
  const selected = value ?? internal;
  return (
    <div className="cc-option-group">
      <span className="cc-option-group__label">
        {label} — <strong>{selected}</strong>
      </span>
      <div className="cc-swatch-row" role="group" aria-label={label}>
        {options.map((o) => (
          <button
            key={o.name}
            type="button"
            className="cc-swatch"
            aria-pressed={o.name === selected}
            onClick={() => {
              setInternal(o.name);
              onChange?.(o.name);
            }}
          >
            <span className="cc-swatch__dot" style={{ background: o.hex }} /> {o.name}
          </button>
        ))}
      </div>
    </div>
  );
}
