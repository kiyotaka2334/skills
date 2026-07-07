import { SizePicker } from "@courtandclover/ui";

const sizes = [
  { label: "S" },
  { label: "M" },
  { label: "L" },
  { label: "XL" },
  { label: "2XL" },
  { label: "3XL", upcharge: 3 },
];

export const Unselected = () => (
  <SizePicker sizes={sizes} note="Relaxed, boxy fit — between sizes? Size down." />
);

export const MediumSelected = () => (
  <SizePicker sizes={sizes} value="M" note="Relaxed, boxy fit — between sizes? Size down." />
);
