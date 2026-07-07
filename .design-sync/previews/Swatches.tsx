import { Swatches } from "@courtandclover/ui";

const colors = [
  { name: "White", hex: "#F8F6F1" },
  { name: "Bay", hex: "#A9C0CB" },
  { name: "Light Green", hex: "#C4CEB5" },
];

export const ColorChoice = () => <Swatches label="Color" options={colors} value="White" />;

export const BaySelected = () => <Swatches label="Color" options={colors} value="Bay" />;
