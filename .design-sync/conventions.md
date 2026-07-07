# Court & Clover — build conventions

This is a heritage-clubhouse retail system: cream surfaces, pine-green ink, brass accents, Playfair Display headlines over Inter body. No drop shadows, no gradients, no neon, no pill buttons — whitespace and restraint are the premium signal.

## Setup

No provider is required. Components are styled by plain CSS classes; the stylesheet ships with the bundle and loads via `styles.css`. Set page backgrounds and text with the tokens below — components assume they sit on cream (`--cc-cream`).

## Styling idiom: CSS custom properties, `--cc-*`

Style your own layout glue with these tokens (defined in `styles.css`; do not invent new ones):

| Token | Use |
|---|---|
| `--cc-cream` `#F4EFE4` | page background |
| `--cc-cream-deep` `#ECE5D4` | image wells, tinted sections |
| `--cc-pine` `#1F3D2B` | headings, primary fills, dark bands |
| `--cc-clover` `#3E6B47` | links, hovers |
| `--cc-brass` `#B8893E` | rules, eyebrows, accents (sparingly) |
| `--cc-ink` `#222019` / `--cc-ink-soft` `#55503F` | body / secondary text |
| `--cc-font-display` | Playfair Display — headlines only, sentence case |
| `--cc-font-body` | Inter — everything else, 16–18px base |
| `--cc-radius` `3px` | corner radius everywhere |
| `--cc-hairline` | brass hairline borders/dividers |

Example glue: `style={{ background: "var(--cc-cream)", fontFamily: "var(--cc-font-body)", color: "var(--cc-ink)" }}`. Headlines: `fontFamily: "var(--cc-font-display)", color: "var(--cc-pine)"`.

## Components (all on `window.CCUI`)

`Button` (variant `primary`/`ghost`, `fullWidth`, `href`), `Eyebrow`, `BrassRule`, `PageHead`, `Logo` (`onDark` on pine), `ProductCard` (4:5 image), `Swatches` (named colors), `SizePicker`, `Accordion`, `TrustBar`, `NoticeBox` (timeline/notice), `SpecTable` (size charts), `EmailCapture`, `EditorialBand`. Per-component API: each `components/general/<Name>/<Name>.d.ts`; truth for the look: `styles.css` and its imports.

## Composition rules

- Section pattern: `Eyebrow` → Playfair heading → optional sub-line → `BrassRule`. Centered for page/section heads.
- Product grids: 2-up mobile / 3-up desktop, `ProductCard` only — no quick-add buttons. Break up thin grids with an `EditorialBand`.
- One primary `Button` per view; secondary actions are `variant="ghost"`.
- Dark bands (`TrustBar`, `EmailCapture`, footers) are pine green with cream text and brass accents.

## Idiomatic snippet

```jsx
const { PageHead, ProductCard, EditorialBand, Button } = window.CCUI;

<div style={{ background: "var(--cc-cream)", minHeight: "100vh" }}>
  <PageHead eyebrow="The collection" title="Pickleball">
    Shirts worth gifting, on blanks worth keeping.
  </PageHead>
  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "2rem", maxWidth: 1100, margin: "0 auto", padding: "0 1.25rem" }}>
    <ProductCard image="…" name="The Rather Be Playing tee" price="$32" />
    <ProductCard image="…" name="The Kitchen Rules tee" price="$32" />
    <ProductCard image="…" name="The Clover Crest tee" price="$34" />
  </div>
  <EditorialBand>Few designs, on purpose.</EditorialBand>
  <div style={{ textAlign: "center", padding: "2rem" }}>
    <Button href="#collection">Shop the pickleball collection</Button>
  </div>
</div>
```
