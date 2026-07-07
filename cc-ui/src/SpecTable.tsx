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
export function SpecTable({ caption, columns, rows }: SpecTableProps) {
  return (
    <div className="cc-table-scroll">
      <table className="cc-spec-table">
        {caption ? <caption>{caption}</caption> : null}
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c} scope="col">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {r.map((cell, j) =>
                j === 0 ? (
                  <th key={j} scope="row">
                    {cell}
                  </th>
                ) : (
                  <td key={j}>{cell}</td>
                )
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
