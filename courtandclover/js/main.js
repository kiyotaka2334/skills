/* Court & Clover — storefront behavior.
   Self-contained store: catalog-driven PDP, localStorage cart, demo checkout
   (no real payment is taken — see checkout.html). */

(function () {
  "use strict";

  var PRODUCTS = window.CC_PRODUCTS || {};
  var COLORS = window.CC_COLORS || [];
  var img = window.CC_IMG || function () { return ""; };

  /* ---------- Cart storage ---------- */

  var CART_KEY = "cc-cart";

  function readCart() {
    try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
    catch (e) { return []; }
  }
  function writeCart(items) {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
    renderCartCount();
  }
  function cartCount() {
    return readCart().reduce(function (n, it) { return n + it.qty; }, 0);
  }
  function money(n) { return "$" + n.toFixed(2); }

  var cartLink = document.querySelector(".cart-link");
  function renderCartCount() {
    if (cartLink) cartLink.textContent = "Cart (" + cartCount() + ")";
  }
  renderCartCount();

  /* ---------- Mobile nav ---------- */

  var navToggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- PDP: hydrate from catalog (?id=...) ---------- */

  var pdpEl = document.querySelector(".pdp");
  var productId = "rather";
  var product = null;

  if (pdpEl) {
    var param = new URLSearchParams(location.search).get("id");
    if (param && PRODUCTS[param]) productId = param;
    product = PRODUCTS[productId];
    hydratePdp(product);
  }

  function altFor(p, colorName) {
    return p.name + " — the design printed in pine green on a " +
      colorName.toLowerCase() + " Comfort Colors tee, studio flat lay";
  }

  function hydratePdp(p) {
    document.title = p.seoTitle;

    var crumb = document.querySelector(".breadcrumb [aria-current='page']");
    if (crumb) crumb.textContent = p.name;

    var title = document.querySelector(".pdp__title");
    if (title) title.textContent = p.name;

    var price = document.getElementById("pdp-price");
    if (price) {
      price.dataset.base = String(p.price);
      price.textContent = money(p.price);
    }

    /* gallery: color view + any extra views (print detail, flat lay) */
    var mainImg = document.querySelector(".pdp-gallery__main img");
    if (mainImg) {
      mainImg.src = img(p.designSlug, p.defaultColor);
      mainImg.alt = altFor(p, p.defaultColor);
    }
    var thumbList = document.querySelector(".pdp-gallery__thumbs");
    if (thumbList) {
      var views = [{ src: img(p.designSlug, p.defaultColor), label: "View: full tee", alt: altFor(p, p.defaultColor) }]
        .concat(p.extraViews);
      thumbList.innerHTML = views.map(function (v, i) {
        return '<li><button type="button" aria-current="' + (i === 0 ? "true" : "false") +
          '" data-full-alt="' + v.alt + '">' +
          '<img src="' + v.src + '" alt="' + v.label + '" width="160" height="200"></button></li>';
      }).join("");
    }

    /* swatches */
    var swatchRow = document.querySelector(".swatch-row");
    if (swatchRow) {
      swatchRow.innerHTML = COLORS.map(function (c) {
        var active = c.name === p.defaultColor;
        return '<button class="swatch" type="button" aria-pressed="' + active +
          '" data-value="' + c.name + '" data-image="' + img(p.designSlug, c.name) + '">' +
          '<span class="swatch__dot" style="background:' + c.hex + '"></span> ' + c.name + "</button>";
      }).join("");
    }
    var colorLabel = document.getElementById("selected-color");
    if (colorLabel) colorLabel.textContent = p.defaultColor;

    /* description */
    var desc = document.getElementById("pdp-desc");
    if (desc) {
      desc.innerHTML = p.description.map(function (t) { return "<p>" + t + "</p>"; }).join("");
    }
  }

  /* ---------- PDP: gallery ---------- */

  var mainImg = document.querySelector(".pdp-gallery__main img");

  function wireThumbs() {
    var thumbs = document.querySelectorAll(".pdp-gallery__thumbs button");
    thumbs.forEach(function (btn) {
      btn.addEventListener("click", function () {
        thumbs.forEach(function (b) { b.setAttribute("aria-current", "false"); });
        btn.setAttribute("aria-current", "true");
        var im = btn.querySelector("img");
        if (mainImg && im) {
          mainImg.src = im.src;
          mainImg.alt = btn.dataset.fullAlt || im.alt;
        }
      });
    });
    return thumbs;
  }
  var thumbs = wireThumbs();

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

  /* variant pricing: flat through 2XL, upcharge for 3XL+ */
  var priceEl = document.getElementById("pdp-price");
  if (priceEl) {
    document.querySelectorAll(".size-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var base = parseFloat(priceEl.dataset.base);
        var up = parseFloat(btn.dataset.upcharge || "0");
        priceEl.textContent = money(base + up);
      });
    });
  }

  /* swatch swaps the garment image to the selected color
     (pattern adapted from 21st.dev ProductCard, vanilla-JS port) */
  document.querySelectorAll(".swatch[data-image]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var first = thumbs[0] && thumbs[0].querySelector("img");
      if (first) first.src = btn.dataset.image;
      if (mainImg && thumbs[0] && thumbs[0].getAttribute("aria-current") === "true") {
        mainImg.src = btn.dataset.image;
        if (product) mainImg.alt = altFor(product, btn.dataset.value);
      }
    });
  });

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
      var color = document.querySelector('.swatch[aria-pressed="true"]');
      var item = {
        id: productId,
        name: product ? product.name : "Tee",
        color: color ? color.dataset.value : "White",
        size: size.dataset.value,
        price: (product ? product.price : 32) + parseFloat(size.dataset.upcharge || "0"),
        qty: 1
      };
      var cart = readCart();
      var existing = cart.find(function (it) {
        return it.id === item.id && it.color === item.color && it.size === item.size;
      });
      if (existing) existing.qty += 1; else cart.push(item);
      writeCart(cart);
      if (cartMsg) {
        cartMsg.innerHTML = "Added to cart — " + item.color + ", size " + item.size +
          '. <a href="cart.html">View cart</a>';
      }
    });
  }

  /* ---------- Size guide drawer ---------- */

  var drawer = document.getElementById("size-drawer");
  if (drawer) {
    var openers = document.querySelectorAll("[data-open-size-guide]");
    var lastFocus = null;

    var onKey = function (e) { if (e.key === "Escape") closeDrawer(); };
    var openDrawer = function () {
      lastFocus = document.activeElement;
      drawer.classList.add("is-open");
      drawer.querySelector(".drawer__close").focus();
      document.addEventListener("keydown", onKey);
    };
    var closeDrawer = function () {
      drawer.classList.remove("is-open");
      document.removeEventListener("keydown", onKey);
      if (lastFocus) lastFocus.focus();
    };

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
      cards.sort(function (a, b) {
        var pa = parseFloat(a.dataset.price), pb = parseFloat(b.dataset.price);
        switch (sortSelect.value) {
          case "price-asc": return pa - pb;
          case "price-desc": return pb - pa;
          default: return parseInt(a.dataset.order, 10) - parseInt(b.dataset.order, 10);
        }
      });
      /* the editorial band keeps its slot via CSS order; cards re-place by DOM position */
      var band = grid.querySelector(".editorial-band");
      cards.forEach(function (c) { grid.insertBefore(c, band); });
    });
  }

  /* ---------- Cart page ---------- */

  var cartRoot = document.getElementById("cart-root");
  if (cartRoot) renderCartPage();

  function renderCartPage() {
    var cart = readCart();
    if (!cart.length) {
      cartRoot.innerHTML =
        '<div class="cart-empty">' +
        "<p>Your cart is empty — the collection is an easy fix.</p>" +
        '<a class="btn" href="collection.html">Shop the collection</a></div>';
      return;
    }
    var subtotal = cart.reduce(function (n, it) { return n + it.price * it.qty; }, 0);
    cartRoot.innerHTML =
      '<ul class="cart-lines">' +
      cart.map(function (it, i) {
        var p = PRODUCTS[it.id];
        var src = p ? img(p.designSlug, it.color) : "";
        return '<li class="cart-line">' +
          '<a href="product.html?id=' + it.id + '" class="cart-line__media"><img src="' + src + '" alt="" width="120" height="150"></a>' +
          '<div class="cart-line__body">' +
          '<p class="cart-line__name"><a href="product.html?id=' + it.id + '">' + it.name + "</a></p>" +
          '<p class="cart-line__meta">' + it.color + " · size " + it.size + "</p>" +
          '<div class="qty-stepper" role="group" aria-label="Quantity for ' + it.name + '">' +
          '<button type="button" data-qty="-1" data-line="' + i + '" aria-label="Decrease quantity">−</button>' +
          '<span aria-live="polite">' + it.qty + "</span>" +
          '<button type="button" data-qty="1" data-line="' + i + '" aria-label="Increase quantity">+</button>' +
          "</div>" +
          "</div>" +
          '<div class="cart-line__end">' +
          '<p class="cart-line__price">' + money(it.price * it.qty) + "</p>" +
          '<button type="button" class="cart-line__remove" data-remove="' + i + '">Remove</button>' +
          "</div></li>";
      }).join("") +
      "</ul>" +
      '<div class="cart-summary">' +
      "<dl>" +
      "<div><dt>Subtotal</dt><dd>" + money(subtotal) + "</dd></div>" +
      "<div><dt>US shipping</dt><dd>Free — included in the price</dd></div>" +
      '<div class="cart-summary__total"><dt>Total</dt><dd>' + money(subtotal) + "</dd></div>" +
      "</dl>" +
      '<a class="btn btn--full" href="checkout.html">Continue to checkout</a>' +
      '<p class="cart-summary__note">Printed to order: 2–5 business days to print, 5–9 business days door to door.</p>' +
      "</div>";

    cartRoot.querySelectorAll("[data-qty]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var cart = readCart();
        var line = cart[parseInt(btn.dataset.line, 10)];
        if (!line) return;
        line.qty = Math.max(1, line.qty + parseInt(btn.dataset.qty, 10));
        writeCart(cart);
        renderCartPage();
      });
    });
    cartRoot.querySelectorAll("[data-remove]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var cart = readCart();
        cart.splice(parseInt(btn.dataset.remove, 10), 1);
        writeCart(cart);
        renderCartPage();
      });
    });
  }

  /* ---------- Checkout page ---------- */

  var checkoutRoot = document.getElementById("checkout-summary");
  var checkoutForm = document.getElementById("checkout-form");
  if (checkoutRoot) {
    var cart = readCart();
    if (!cart.length) {
      checkoutRoot.innerHTML = '<p>Your cart is empty. <a href="collection.html">Back to the collection</a>.</p>';
      if (checkoutForm) checkoutForm.style.display = "none";
    } else {
      var subtotal = cart.reduce(function (n, it) { return n + it.price * it.qty; }, 0);
      checkoutRoot.innerHTML =
        '<ul class="checkout-lines">' +
        cart.map(function (it) {
          return "<li><span>" + it.qty + " × " + it.name + " (" + it.color + ", " + it.size + ")</span><span>" +
            money(it.price * it.qty) + "</span></li>";
        }).join("") +
        "</ul>" +
        '<p class="checkout-total"><span>Total, free US shipping</span><span>' + money(subtotal) + "</span></p>";
    }
  }
  if (checkoutForm) {
    checkoutForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!checkoutForm.reportValidity()) return;
      var order = "CC-" + String(Math.floor(1000 + Math.random() * 9000));
      writeCart([]);
      var confirm = document.getElementById("order-confirmation");
      document.getElementById("checkout-main").hidden = true;
      confirm.hidden = false;
      document.getElementById("order-number").textContent = order;
      confirm.focus();
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
        msg.textContent = "You're in. Check " + input.value + " for your 10% welcome code.";
      }
      form.reset();
    });
  });
})();
