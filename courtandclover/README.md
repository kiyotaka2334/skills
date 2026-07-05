# Court & Clover — storefront build

A hand-coded, portfolio-grade storefront implementing the **Court & Clover website blueprint** (five pages, design system, checkout-adjacent trust content). Built static so it can be previewed anywhere and later ported section-by-section into a Shopify theme (Dawn), per the blueprint's platform choice.

## Pages (built in blueprint order)

| Page | File | Blueprint section |
|---|---|---|
| Product detail (money page) | `product.html` | 4.1 |
| Collection: Pickleball | `collection.html` | 4.2 |
| Homepage — Direction A, type-led | `index.html` | 4.3 |
| About | `about.html` | 4.4 |
| Size / Shipping / Returns | `size-shipping-returns.html` | 4.5 |
| Privacy / Terms / Refund (v1 placeholders) | `policies.html` | Part 6 |
| 404 | `404.html` | QA checklist |

## Design system (Part 3)

Tokens live once in `css/main.css` as CSS variables: Cream `#F4EFE4`, Pine Green `#1F3D2B`, Clover `#3E6B47`, Brass `#B8893E`, Ink `#222019`; Playfair Display for display type, Inter for body at 17px base; 3px button radius; no shadows, no gradients. Mobile-first — every section designed at 390px before desktop.

## What's implemented

- PDP: 4:5 gallery (garment / print close-up / size-context flat lay), named color swatches that **swap the garment image per color**, size selector with +$3 upcharge for 3XL, size-guide **drawer** (not a page), made-to-order timeline block, fabric & care accordion, one-line returns summary, brass trust row. No reviews module (per blueprint — hidden until ~5 reviews exist).
- Collection: 2-up mobile / 3-up desktop grid, sort dropdown (no sidebar filters at this SKU count), editorial band mid-grid.
- Homepage: gift-led hero headline, trust bar, featured grid, gift-occasion block, brand strip, email capture with a real incentive.
- Trust page: real Comfort Colors 1717 flat measurements, both shipping clocks (production + transit) with a gift-deadline note, plain-language returns.
- Global: skip link, visible focus states, reduced-motion support, semantic landmarks, OG image + favicon in brand palette, per-page long-tail titles/descriptions.

Demo-only stand-ins for what Shopify provides natively: cart count (localStorage), email-capture confirmation, add-to-cart message.

## Assets

Product mockups are generated SVG flat-lays (placeholder until the sample is shot — blueprint launches on Direction A for exactly this reason). Regenerate after design changes:

```bash
python3 scripts/generate_mockups.py
```

`assets/og-image.png` is exported from `assets/og-image.svg` (screenshot at 1200×630).

## Preview

Open `index.html` directly, or:

```bash
npx http-server . -p 8080
```

## Credits / tooling used in the build

- `anthropics/skills @ frontend-design` — design-pass guidance (installed in `.agents/skills/`)
- `vercel-labs/agent-skills @ web-design-guidelines` — UI compliance review
- Repo skills: `ui-ux-pro-max` (design-token conventions), `find-skills` (skill discovery workflow)
- 21st.dev connector — PDP breadcrumb pattern and the color-swatch→image-swap interaction were adapted (vanilla-JS ports) from catalog components `product-detail-page` (@kavikatiyar) and `product-card` (@YoucefBnm)

## Not in scope (launch gate, Part 7)

Shopify provisioning, Printful connection, Stripe/PayPal, LLC — those are the go-live machinery. This build is everything before the gate.
