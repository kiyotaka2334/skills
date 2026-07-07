import * as React from "react";
export interface EditorialBandProps {
    /** One line of brand voice, set in Playfair italic. */
    children: React.ReactNode;
}
/**
 * Full-width editorial strip between brass rules — one italic Playfair
 * line of brand voice. Used mid-grid to turn a thin collection into
 * intentional restraint.
 */
export declare function EditorialBand({ children }: EditorialBandProps): React.JSX.Element;
