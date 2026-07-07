import * as React from "react";

export interface PageHeadProps {
  /** Brass caps label above the title, e.g. "The collection". */
  eyebrow?: string;
  /** Playfair Display headline, sentence case. */
  title: string;
  /** Optional one-line positioning sentence under the title. */
  children?: React.ReactNode;
}

/**
 * Centered page header: eyebrow, oversized Playfair title, optional
 * sub-line, closed by a brass rule. Opens every top-level page.
 */
export function PageHead({ eyebrow, title, children }: PageHeadProps) {
  return (
    <div className="cc-page-head">
      {eyebrow ? <p className="cc-eyebrow">{eyebrow}</p> : null}
      <h1>{title}</h1>
      {children ? <p className="cc-page-head__sub">{children}</p> : null}
      <hr className="cc-brass-rule" />
    </div>
  );
}
