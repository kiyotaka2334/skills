import * as React from "react";

export interface TrustBarProps {
  /** Short promises, e.g. "Free US shipping". Three is the sweet spot. */
  items: string[];
}

/**
 * Thin pine-green strip of store promises in letter-spaced caps, shown
 * under the hero. Keep each item to a few words; three items max.
 */
export function TrustBar({ items }: TrustBarProps) {
  return (
    <div className="cc-trust-bar" role="note">
      <ul>
        {items.map((t) => (
          <li key={t}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
              <path d="M12 3l2.5 5 5.5.8-4 3.9.9 5.5-4.9-2.6-4.9 2.6.9-5.5-4-3.9 5.5-.8z" />
            </svg>
            {t}
          </li>
        ))}
      </ul>
    </div>
  );
}
