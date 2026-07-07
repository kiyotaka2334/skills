import * as React from "react";

export interface EyebrowProps {
  children: React.ReactNode;
}

/**
 * Wide letter-spaced brass caps that label a section ("THE COLLECTION",
 * "OUR STORY"). Always sits above a Playfair heading, never alone.
 */
export function Eyebrow({ children }: EyebrowProps) {
  return <p className="cc-eyebrow">{children}</p>;
}
