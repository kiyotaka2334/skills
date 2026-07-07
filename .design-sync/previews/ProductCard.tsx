import { ProductCard } from "@courtandclover/ui";

const tee = (label: string) =>
  "data:image/svg+xml," +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">' +
      '<rect width="800" height="1000" fill="#ECE5D4"/>' +
      '<path d="M326 200 L242 226 L108 386 L152 452 L232 402 L228 850 Q228 862 240 862 L560 862 Q572 862 572 850 L568 402 L648 452 L692 386 L558 226 L474 200 Q400 258 326 200 Z" fill="#F8F6F1" stroke="#DDD5C2" stroke-width="3"/>' +
      '<text x="400" y="520" font-family="Georgia,serif" font-size="56" text-anchor="middle" fill="#1F3D2B">' +
      label +
      "</text></svg>"
  );

export const Single = () => (
  <div style={{ width: 260 }}>
    <ProductCard image={tee("Rather")} name="The Rather Be Playing tee" price="$32" href="#" />
  </div>
);

export const GridRow = () => (
  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1.5rem", maxWidth: 720 }}>
    <ProductCard image={tee("Rather")} name="The Rather Be Playing tee" price="$32" href="#" />
    <ProductCard image={tee("Kitchen")} name="The Kitchen Rules tee" price="$32" href="#" />
    <ProductCard image={tee("Crest")} name="The Clover Crest tee" price="$34" href="#" />
  </div>
);
