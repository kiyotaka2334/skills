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
export declare function SizePicker({ label, sizes, value, onChange, note }: SizePickerProps): React.JSX.Element;
