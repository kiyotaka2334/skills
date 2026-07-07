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
export declare function Swatches({ label, options, value, onChange }: SwatchesProps): React.JSX.Element;
