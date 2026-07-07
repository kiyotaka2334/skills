import * as React from "react";

export interface NoticeBoxProps {
  /** Bolded lead-in, e.g. "Made to order, for you." */
  title?: string;
  children: React.ReactNode;
}

/**
 * Brass-bordered inline notice with a clock icon — the made-to-order
 * timeline block. Conversion-critical on product pages: state production
 * and delivery windows explicitly.
 */
export function NoticeBox({ title, children }: NoticeBoxProps) {
  return (
    <div className="cc-notice">
      <svg viewBox="0 0 24 24" fill="none" stroke="#B8893E" strokeWidth={1.6} aria-hidden="true">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3.5 2" />
      </svg>
      <p>
        {title ? <strong>{title} </strong> : null}
        {children}
      </p>
    </div>
  );
}
