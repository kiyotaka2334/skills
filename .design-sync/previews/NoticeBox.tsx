import { NoticeBox } from "@courtandclover/ui";

export const MadeToOrder = () => (
  <div style={{ maxWidth: 440 }}>
    <NoticeBox title="Made to order, for you.">
      Printed in 2–5 business days, delivered in 5–9 business days total. Ordering for an occasion? Allow
      10 days to be safe.
    </NoticeBox>
  </div>
);

export const GiftDeadline = () => (
  <div style={{ maxWidth: 440 }}>
    <NoticeBox>Ordering for Father's Day? Order by June 5 and you're comfortably ahead of both clocks.</NoticeBox>
  </div>
);
