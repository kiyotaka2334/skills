import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Collection-grid product card: 4:5 image in a brass-hairline well, name,
 * price. No quick-add clutter — the card is one calm link. Grids run 2-up
 * on mobile, 3-up on desktop.
 */
export function ProductCard({ image, imageAlt = "", name, price, href = "#" }) {
    return (_jsx("article", { className: "cc-product-card", children: _jsxs("a", { href: href, children: [_jsx("div", { className: "cc-product-card__media", children: _jsx("img", { src: image, alt: imageAlt, width: 800, height: 1000, loading: "lazy" }) }), _jsx("h3", { children: name }), _jsx("p", { className: "cc-product-card__price", children: price })] }) }));
}
