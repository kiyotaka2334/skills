/* Court & Clover — product catalog.
   Single source of truth for the PDP, cart, and checkout. */

window.CC_PRODUCTS = {
  rather: {
    name: "The Rather Be Playing tee",
    price: 32,
    seoTitle: "Funny Pickleball Shirt — The Rather Be Playing Tee | Court & Clover",
    designSlug: "rather",
    defaultColor: "White",
    description: [
      "The gift for the player who has everything — and would still rather be on the court. The Rather Be Playing tee says it for them, in a hand-set clubhouse print that skips the neon-and-clipart look the sport usually gets.",
      "It's printed on the Comfort Colors 1717: a heavyweight, garment-dyed cotton blank with a soft, broken-in feel from the first wear. The cut is boxy and relaxed — honest truth: if you like a closer fit, order one size down."
    ],
    extraViews: [
      { src: "assets/photo-tee-rather-detail.jpg", label: "View: print close-up", alt: "Close crop of the Rather Be Playing print, showing the ink sitting in the cotton jersey" }
    ]
  },
  kitchen: {
    name: "The Kitchen Rules tee",
    price: 32,
    seoTitle: "Stay Out of the Kitchen Pickleball Shirt — The Kitchen Rules Tee | Court & Clover",
    designSlug: "kitchen",
    defaultColor: "White",
    description: [
      "Every pickleball house has one rule, and this shirt states it with the manners of a clubhouse sign: stay out of the kitchen. For the player who calls foot faults at family gatherings — affectionately.",
      "Printed on the Comfort Colors 1717, a heavyweight garment-dyed blank with a soft, already-broken-in feel. Boxy, relaxed cut — size down if you prefer it closer."
    ],
    extraViews: [
      { src: "assets/photo-tee-kitchen-detail.jpg", label: "View: print close-up", alt: "Close crop of the Kitchen Rules print on the cotton jersey" }
    ]
  },
  dink: {
    name: "The Dink Responsibly tee",
    price: 32,
    seoTitle: "Pickleball Gift Shirt — The Dink Responsibly Tee | Court & Clover",
    designSlug: "dink",
    defaultColor: "White",
    description: [
      "A public-service announcement for the soft-game specialist: dink responsibly. The joke lands quietly, in serif type on a garment-dyed blank — the way a clubhouse would tell it.",
      "Printed on the Comfort Colors 1717, heavyweight ring-spun cotton with a lived-in feel from day one. The fit is boxy and relaxed; between sizes, go down."
    ],
    extraViews: [
      { src: "assets/photo-tee-dink-detail.jpg", label: "View: print close-up", alt: "Close crop of the Dink Responsibly print on the cotton jersey" }
    ]
  },
  crest: {
    name: "The Clover Crest tee",
    price: 34,
    seoTitle: "Pickleball Club Crest Shirt — The Clover Crest Tee | Court & Clover",
    designSlug: "crest",
    defaultColor: "White",
    description: [
      "The house mark, worn plainly: the Court & Clover crest, drawn like the badge of a club that takes its Tuesday round seriously. No joke on this one — just the insignia.",
      "Printed on the Comfort Colors 1717, a heavyweight garment-dyed blank that softens with every wash. Boxy, relaxed cut — order a size down for a closer fit."
    ],
    extraViews: [
      { src: "assets/photo-tee-crest-detail.jpg", label: "View: print close-up", alt: "Close crop of the Clover Crest print on the cotton jersey" }
    ]
  }
};

window.CC_COLORS = [
  { name: "White", slug: "white", hex: "#F8F6F1" },
  { name: "Bay", slug: "bay", hex: "#A9C0CB" },
  { name: "Light Green", slug: "lightgreen", hex: "#C4CEB5" }
];

window.CC_IMG = function (designSlug, colorName) {
  var color = window.CC_COLORS.find(function (c) { return c.name === colorName; });
  return "assets/photo-tee-" + designSlug + "-" + (color ? color.slug : "white") + ".jpg";
};
