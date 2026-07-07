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
export function Logo({ onDark, href = "/" }: LogoProps) {
  return (
    <a className={onDark ? "cc-logo cc-logo--on-dark" : "cc-logo"} href={href}>
      <svg viewBox="0 0 64 64" aria-hidden="true" fill="currentColor">
        <circle cx="25" cy="24" r="10" />
        <circle cx="39" cy="24" r="10" />
        <circle cx="25" cy="38" r="10" />
        <circle cx="39" cy="38" r="10" />
        <rect x="30.5" y="34" width="3" height="22" rx="1.5" transform="rotate(18 32 34)" />
      </svg>
      Court &amp; Clover
    </a>
  );
}
