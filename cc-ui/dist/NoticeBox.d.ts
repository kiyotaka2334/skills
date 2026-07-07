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
export declare function NoticeBox({ title, children }: NoticeBoxProps): React.JSX.Element;
