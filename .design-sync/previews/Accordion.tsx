import { Accordion } from "@courtandclover/ui";

const items = [
  {
    title: "Fabric & care",
    content: (
      <p>
        100% ring-spun US cotton, 6.1 oz — garment-dyed for a lived-in color. Machine wash cold, inside
        out. Tumble dry low. No ironing over the print.
      </p>
    ),
  },
  {
    title: "Returns",
    content: <p>Free replacement for any defect or misprint — email a photo within 30 days.</p>,
  },
  {
    title: "How long until it arrives?",
    content: <p>Printed for you in 2–5 business days; most US orders arrive within 5–9 business days.</p>,
  },
];

export const Closed = () => (
  <div style={{ width: 420 }}>
    <Accordion items={items} />
  </div>
);

export const FirstOpen = () => (
  <div style={{ width: 420 }}>
    <Accordion items={items} defaultOpen={0} />
  </div>
);
