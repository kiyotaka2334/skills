import * as React from "react";
export interface TrustBarProps {
    /** Short promises, e.g. "Free US shipping". Three is the sweet spot. */
    items: string[];
}
/**
 * Thin pine-green strip of store promises in letter-spaced caps, shown
 * under the hero. Keep each item to a few words; three items max.
 */
export declare function TrustBar({ items }: TrustBarProps): React.JSX.Element;
