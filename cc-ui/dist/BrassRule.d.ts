export interface BrassRuleProps {
    /** Center (default) for section heads; left for left-aligned prose. */
    align?: "center" | "left";
}
/**
 * The brand's only ornament: a short 1px brass rule used under headings and
 * between sections. Use sparingly — one per section at most.
 */
export declare function BrassRule({ align }: BrassRuleProps): import("react").JSX.Element;
