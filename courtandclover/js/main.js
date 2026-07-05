/* Court & Clover — storefront behavior.
   Static-site stand-ins for what Shopify handles natively (cart, capture);
   everything here is presentational demo logic for the build phase. */

(function () {
  "use strict";

  /* ---------- Mobile nav ---------- */

  var navToggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- Demo cart count (localStorage) ---------- */

  var CART_KEY = "cc-cart-count";
  var cartLink = document.querySelector(".cart-link");

  function renderCart() {
    if (!cartLink) return;
    var n = parseInt(localStorage.getItem(CART_KEY) || "0", 10);
    cartLink.textContent = "Cart (" + n + ")";
  }
  renderCart();

  /* ---------- PDP: gallery ---------- */

  var mainImg = document.querySelector(".pdp-gallery__main img");
  var thumbs = document.querySelectorAll(".pdp-gallery__thumbs button");
  thumbs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      thumbs.forEach(function (b) { b.setAttribute("aria-current", "false"); });
      btn.setAttribute("aria-current", "true");
      var img = btn.querySelector("img");
      if (mainImg && img) {
        mainImg.src = img.src;
        mainImg.alt = btn.dataset.fullAlt || img.alt;
      }
    });
  });

  /* ---------- PDP: color + size selection ---------- */

  function wireChoice(groupSelector, labelId) {
    var buttons = document.querySelectorAll(groupSelector);
    var label = labelId ? document.getElementById(labelId) : null;
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        btn.setAttribute("aria-pressed", "true");
        if (label) label.textContent = btn.dataset.value || btn.textContent.trim();
      });
    });
  }
  wireChoice(".swatch", "selected-color");
  wireChoice(".size-btn", "selected-size");

  /* swatch swaps the garment image to the selected color
     (pattern adapted from 21st.dev ProductCard, vanilla-JS port) */
  document.querySelectorAll(".swatch[data-image]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var first = thumbs[0] && thumbs[0].querySelector("img");
      if (first) first.src = btn.dataset.image;
      if (mainImg && thumbs[0] && thumbs[0].getAttribute("aria-current") === "true") {
        mainImg.src = btn.dataset.image;
        mainImg.alt =
          "Funny pickleball shirt — the Rather Be Playing design on a " +
          btn.dataset.value.toLowerCase() + " Comfort Colors tee, laid flat on cream";
      }
    });
  });

  /* variant pricing: flat through 2XL, upcharge for 3XL+ */
  var priceEl = document.getElementById("pdp-price");
  if (priceEl) {
    document.querySelectorAll(".size-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var base = parseFloat(priceEl.dataset.base);
        var up = parseFloat(btn.dataset.upcharge || "0");
        priceEl.textContent = "$" + (base + up).toFixed(2);
      });
    });
  }

  /* ---------- PDP: add to cart ---------- */

  var addBtn = document.getElementById("add-to-cart");
  var cartMsg = document.getElementById("cart-msg");
  if (addBtn) {
    addBtn.addEventListener("click", function () {
      var size = document.querySelector('.size-btn[aria-pressed="true"]');
      if (!size) {
        if (cartMsg) cartMsg.textContent = "Choose a size first — the size guide can help.";
        return;
      }
      var n = parseInt(localStorage.getItem(CART_KEY) || "0", 10) + 1;
      localStorage.setItem(CART_KEY, String(n));
      renderCart();
      var color = document.querySelector('.swatch[aria-pressed="true"]');
      if (cartMsg) {
        cartMsg.textContent =
          "Added to cart — " +
          (color ? color.dataset.value + ", " : "") +
          "size " + (size.dataset.value || size.textContent.trim()) + ".";
      }
    });
  }

  /* ---------- Size guide drawer (opens in place, not a new page) ---------- */

  var drawer = document.getElementById("size-drawer");
  if (drawer) {
    var openers = document.querySelectorAll("[data-open-size-guide]");
    var lastFocus = null;

    function openDrawer() {
      lastFocus = document.activeElement;
      drawer.classList.add("is-open");
      drawer.querySelector(".drawer__close").focus();
      document.addEventListener("keydown", onKey);
    }
    function closeDrawer() {
      drawer.classList.remove("is-open");
      document.removeEventListener("keydown", onKey);
      if (lastFocus) lastFocus.focus();
    }
    function onKey(e) { if (e.key === "Escape") closeDrawer(); }

    openers.forEach(function (b) { b.addEventListener("click", openDrawer); });
    drawer.querySelector(".drawer__scrim").addEventListener("click", closeDrawer);
    drawer.querySelector(".drawer__close").addEventListener("click", closeDrawer);
  }

  /* ---------- Collection: sort dropdown ---------- */

  var sortSelect = document.getElementById("sort");
  var grid = document.querySelector(".product-grid");
  if (sortSelect && grid) {
    sortSelect.addEventListener("change", function () {
      var cards = Array.prototype.slice.call(grid.querySelectorAll(".product-card"));
      var band = grid.querySelector(".editorial-band");
      cards.sort(function (a, b) {
        var pa = parseFloat(a.dataset.price), pb = parseFloat(b.dataset.price);
        switch (sortSelect.value) {
          case "price-asc": return pa - pb;
          case "price-desc": return pb - pa;
          default: return parseInt(a.dataset.order, 10) - parseInt(b.dataset.order, 10);
        }
      });
      cards.forEach(function (c) { grid.appendChild(c); });
      /* keep the editorial band mid-grid after re-sorting */
      if (band && cards.length > 1) grid.insertBefore(band, cards[2] || null);
    });
  }

  /* ---------- Email capture ---------- */

  document.querySelectorAll(".email-form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type="email"]');
      var msg = form.parentElement.querySelector(".email-form__msg");
      if (!input.value) return;
      if (msg) {
        msg.textContent =
          "You're in. Check " + input.value + " for your 10% welcome code.";
      }
      form.reset();
    });
  });
})();
