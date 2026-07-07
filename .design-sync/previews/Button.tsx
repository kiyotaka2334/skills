import { Button } from "@courtandclover/ui";

export const Primary = () => <Button>Shop the pickleball collection</Button>;

export const Ghost = () => <Button variant="ghost">View the full collection</Button>;

export const FullWidth = () => (
  <div style={{ width: 340 }}>
    <Button fullWidth>Add to cart — free US shipping</Button>
  </div>
);

export const AsLink = () => <Button href="#collection">Find their gift</Button>;

export const Disabled = () => <Button disabled>Sold out</Button>;
