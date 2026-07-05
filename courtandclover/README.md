# Court & Clover — standalone storefront

A complete, self-contained e-commerce website for Court & Clover (premium pickleball gifts), built from the project's website blueprint: five core pages, a global design system, per-product pages, a working cart, and a demo checkout. No frameworks, no build step — plain HTML, CSS, and vanilla JS, so it runs from any static host or straight off the filesystem.

## Pages

| Page | File |
|---|---|
| Homepage — editorial, type-led | `index.html` |
| Collection: Pickleball | `collection.html` |
| Product detail (catalog-driven: `?id=rather\|kitchen\|dink\|crest`) | `product.html` |
| Cart | `cart.html` |
| Checkout + order confirmation (demo — no payment taken) | `checkout.html` |
| About | `about.html` |
| Size / Shipping / Returns | `size-shipping-returns.html` |
| Privacy / Terms / Refund | `policies.html` |
| 404 | `404.html` |

## How it works

- `js/products.js` is the catalog — the single source of truth for names, prices, copy, and per-color imagery. `product.html` is one template hydrated from it via the `?id=` parameter.
- `js/main.js` runs the store: PDP hydration, gallery, color swatches that swap the garment image, size upcharges (+$3 for 3XL), a localStorage cart with quantity steppers, and the demo checkout flow that ends in an order confirmation.
- `css/main.css` holds the whole design system as CSS variables: Cream `#F4EFE4`, Pine Green `#1F3D2B`, Clover `#3E6B47`, Brass `#B8893E`, Ink `#222019`; Playfair Display display type over Inter body at a 17px base; 3px radii; no shadows or gradients. Mobile-first at 390px.
- Product imagery is generated SVG flat-lay mockups (every design × every garment color). Regenerate after design changes:

  ```bash
  python3 scripts/generate_mockups.py
  ```

Adding a product = one entry in `js/products.js`, one print design in `scripts/generate_mockups.py`, and a card in `collection.html`/`index.html`.

## Run it

Open `index.html` directly, or serve the folder:

```bash
npx http-server . -p 8080
```

Note: the demo checkout takes no payment and requests no card details — wiring in a real payment provider is the one thing this site intentionally leaves out.

## Credits / tooling used in the build

- `anthropics/skills @ frontend-design` — design-pass guidance (installed in `.agents/skills/`)
- `vercel-labs/agent-skills @ web-design-guidelines` — accessibility/UX floor (skip links, focus states, reduced motion, semantic landmarks)
- Repo skills: `ui-ux-pro-max` (design-token conventions), `find-skills` (skill discovery workflow)
- 21st.dev connector — the PDP breadcrumb pattern and the swatch→image-swap interaction were adapted (vanilla-JS ports) from catalog components `product-detail-page` (@kavikatiyar) and `product-card` (@YoucefBnm)
