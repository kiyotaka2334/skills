import * as React from "react";

export interface ProductCardProps {
  /** Product photo, 4:5 ratio. Studio flat-lay on the cream-deep well. */
  image: string;
  imageAlt?: string;
  name: string;
  /** Display price, e.g. "$32". */
  price: string;
  href?: string;
}

/**
 * Collection-grid product card: 4:5 image in a brass-hairline well, name,
 * price. No quick-add clutter — the card is one calm link. Grids run 2-up
 * on mobile, 3-up on desktop.
 */
export function ProductCard({ image, imageAlt = "", name, price, href = "#" }: ProductCardProps) {
  return (
    <article className="cc-product-card">
      <a href={href}>
        <div className="cc-product-card__media">
          <img src={image} alt={imageAlt} width={800} height={1000} loading="lazy" />
        </div>
        <h3>{name}</h3>
        <p className="cc-product-card__price">{price}</p>
      </a>
    </article>
  );
}
