import { BrassRule } from "@courtandclover/ui";

export const Centered = () => (
  <div style={{ textAlign: "center" }}>
    <p style={{ fontFamily: "var(--cc-font-display)", color: "var(--cc-pine)", fontSize: "1.4rem", margin: 0 }}>
      The gift for the one who'd rather be playing
    </p>
    <BrassRule />
  </div>
);

export const LeftAligned = () => (
  <div>
    <p style={{ fontFamily: "var(--cc-font-body)", margin: 0 }}>Left-set prose gets a left rule.</p>
    <BrassRule align="left" />
  </div>
);
