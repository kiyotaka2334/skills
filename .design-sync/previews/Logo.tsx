import { Logo } from "@courtandclover/ui";

export const OnCream = () => <Logo />;

export const OnPine = () => (
  <div style={{ background: "var(--cc-pine)", padding: "1.25rem" }}>
    <Logo onDark />
  </div>
);
