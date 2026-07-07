import { SpecTable } from "@courtandclover/ui";

export const SizeChart = () => (
  <div style={{ maxWidth: 440 }}>
    <SpecTable
      caption="Comfort Colors 1717, measured flat, in inches"
      columns={["Size", "Width", "Length"]}
      rows={[
        ["S", 18, 27],
        ["M", 20, 28],
        ["L", 22, 29],
        ["XL", 24, 30],
        ["2XL", 26, 31],
        ["3XL", 28, 32],
      ]}
    />
  </div>
);
