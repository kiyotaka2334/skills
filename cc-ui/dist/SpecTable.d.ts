import * as React from "react";
export interface SpecTableProps {
    /** Small caption above the table, e.g. measurement units. */
    caption?: string;
    /** Column headers; the first column renders as row headers. */
    columns: string[];
    rows: (string | number)[][];
}
/**
 * Brass-ruled specification table — the size chart. Numbers centered,
 * first column is the row label. Wrap in a horizontally scrollable
 * container on narrow screens (the component does this itself).
 */
export declare function SpecTable({ caption, columns, rows }: SpecTableProps): React.JSX.Element;
