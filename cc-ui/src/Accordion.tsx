import * as React from "react";

export interface AccordionItem {
  title: string;
  content: React.ReactNode;
}

export interface AccordionProps {
  items: AccordionItem[];
  /** Index of an item to render open initially. */
  defaultOpen?: number;
}

/**
 * Brass-hairline accordion for secondary content — fabric & care, FAQ,
 * returns. Native `<details>` semantics; the marker is a brass +/−.
 */
export function Accordion({ items, defaultOpen }: AccordionProps) {
  return (
    <div className="cc-accordion">
      {items.map((it, i) => (
        <details key={it.title} open={i === defaultOpen}>
          <summary>{it.title}</summary>
          <div className="cc-accordion__body">{it.content}</div>
        </details>
      ))}
    </div>
  );
}
