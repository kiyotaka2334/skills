export interface LogoProps {
    /** Renders the wordmark in cream for pine-green surfaces (footer, email capture). */
    onDark?: boolean;
    /** Link target; defaults to the home page. */
    href?: string;
}
/**
 * The Court & Clover wordmark: four-leaf clover mark plus the name set in
 * Playfair Display. Use `onDark` on pine-green surfaces.
 */
export declare function Logo({ onDark, href }: LogoProps): import("react").JSX.Element;
