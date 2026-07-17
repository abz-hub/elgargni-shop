function initPageLoader() {
  const loader = document.getElementById("page-loader");
  if (!loader) return;

  const hide = () => {
    if (!document.body.contains(loader)) return;
    if (window.gsap) {
      gsap.to(loader, {
        opacity: 0,
        duration: 0.5,
        onComplete: () => loader.remove(),
      });
    } else {
      loader.style.transition = "opacity 0.5s ease";
      loader.style.opacity = "0";
      window.setTimeout(() => loader.remove(), 550);
    }
  };

  window.addEventListener("load", () => window.setTimeout(hide, 150));
  // Safety net: never leave the loader stuck on screen.
  window.setTimeout(hide, 4000);
}

function initRevealFallback(revealEls) {
  const reveal = (el) => el.classList.add("in-view");

  if (!("IntersectionObserver" in window)) {
    revealEls.forEach(reveal);
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          reveal(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  revealEls.forEach((el) => observer.observe(el));

  // Safety net: never leave content permanently invisible if the
  // observer doesn't fire for some reason.
  window.setTimeout(() => revealEls.forEach(reveal), 1500);
}

function initScrollReveal() {
  const revealEls = document.querySelectorAll(".reveal");
  if (!revealEls.length) return;

  if (!(window.gsap && window.ScrollTrigger)) {
    initRevealFallback(revealEls);
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  document.querySelectorAll(".services-grid, .products-grid").forEach((grid) => {
    const cards = grid.querySelectorAll(".reveal");
    if (!cards.length) return;
    gsap.fromTo(
      cards,
      { opacity: 0, y: 40, scale: 0.94 },
      {
        opacity: 1,
        y: 0,
        scale: 1,
        duration: 0.7,
        ease: "power3.out",
        stagger: 0.1,
        scrollTrigger: { trigger: grid, start: "top 85%" },
      }
    );
  });

  revealEls.forEach((el) => {
    if (el.closest(".services-grid, .products-grid")) return;
    gsap.fromTo(
      el,
      { opacity: 0, y: 32 },
      {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 88%" },
      }
    );
  });
}

function initSmoothScroll() {
  if (!window.Lenis) return;
  const lenis = new Lenis({ duration: 1.1, smoothWheel: true });

  if (window.gsap && window.ScrollTrigger) {
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
  } else {
    const raf = (time) => {
      lenis.raf(time);
      window.requestAnimationFrame(raf);
    };
    window.requestAnimationFrame(raf);
  }
}

function initNavbarScrollShadow() {
  const navbar = document.querySelector(".navbar");
  if (!navbar) return;
  const update = () => navbar.classList.toggle("scrolled", window.scrollY > 20);
  window.addEventListener("scroll", update);
  update();
}

function initHeroParallax() {
  const hero = document.getElementById("hero");
  if (!hero) return;
  const floaters = Array.from(hero.querySelectorAll(".hero-floater")).map((floater) => ({
    el: floater,
    target: floater.querySelector("svg") || floater,
    depth: parseFloat(floater.dataset.depth || "0.3"),
  }));
  if (!floaters.length) return;

  const move = (relX, relY) => {
    floaters.forEach(({ target, depth }) => {
      const x = relX * depth * 60;
      const y = relY * depth * 60;
      if (window.gsap) {
        gsap.to(target, { x, y, duration: 0.6, ease: "power2.out", overwrite: "auto" });
      } else {
        target.style.transform = `translate(${x}px, ${y}px)`;
      }
    });
  };

  hero.addEventListener("mousemove", (e) => {
    const rect = hero.getBoundingClientRect();
    move((e.clientX - rect.left) / rect.width - 0.5, (e.clientY - rect.top) / rect.height - 0.5);
  });

  hero.addEventListener("mouseleave", () => move(0, 0));
}

function initCardTilt(selector) {
  document.querySelectorAll(selector).forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      const rotateY = x * 10;
      const rotateX = -y * 10;
      card.style.transform = `perspective(700px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.03) translateY(-6px)`;
    });
    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
    });
  });
}

function initButtonRipple() {
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn");
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const ripple = document.createElement("span");
    ripple.className = "btn-ripple";
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
    ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
    btn.appendChild(ripple);
    ripple.addEventListener("animationend", () => ripple.remove());
  });
}

function initCounters() {
  const counters = document.querySelectorAll("[data-count-to]");
  const bars = document.querySelectorAll("[data-fill-to]");
  if (!counters.length && !bars.length) return;

  const animateCounter = (el) => {
    const target = parseInt(el.dataset.countTo, 10);
    if (window.gsap) {
      gsap.to(el, {
        innerText: target,
        duration: 1.4,
        ease: "power2.out",
        snap: { innerText: 1 },
      });
    } else {
      el.textContent = target;
    }
  };

  const animateBar = (el) => {
    window.requestAnimationFrame(() => {
      el.style.width = `${el.dataset.fillTo}%`;
    });
  };

  const targets = [...counters, ...bars];
  const trigger = (el) => {
    if (el.hasAttribute("data-count-to")) animateCounter(el);
    if (el.hasAttribute("data-fill-to")) animateBar(el);
  };

  if (!("IntersectionObserver" in window)) {
    targets.forEach(trigger);
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          trigger(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );
  targets.forEach((el) => observer.observe(el));

  // Safety net: guarantee counters/bars settle even if the observer never fires.
  window.setTimeout(() => targets.forEach(trigger), 2500);
}

function initQuickView() {
  const modal = document.getElementById("quick-view-modal");
  if (!modal) return;

  const panel = modal.querySelector(".quick-view-panel");
  const media = document.getElementById("quick-view-media");
  const nameEl = document.getElementById("quick-view-name");
  const flavorEl = document.getElementById("quick-view-flavor");
  const sizeEl = document.getElementById("quick-view-size");
  const priceEl = document.getElementById("quick-view-price");
  const form = document.getElementById("quick-view-form");

  const categoryIcons = {
    "protein-recovery":
      '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="1" y="10" width="3" height="4" rx="1"/><rect x="20" y="10" width="3" height="4" rx="1"/><rect x="4" y="8" width="2.5" height="8" rx="1"/><rect x="17.5" y="8" width="2.5" height="8" rx="1"/><rect x="6.5" y="11" width="11" height="2"/></svg>',
    "pre-workout-energy":
      '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="13,2 4,14 11,14 10,22 20,10 13,10"/></svg>',
    "vitamins-wellness":
      '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C7 6 4 10.5 4 14a8 8 0 0 0 16 0c0-3.5-3-8-8-12z"/></svg>',
    shakers:
      '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 2h8l1 3h-1l1.7 15.1A1.7 1.7 0 0 1 16 22H8a1.7 1.7 0 0 1-1.7-1.9L8 5H7l1-3Zm1.5 5-1.4 13h7.8L14.5 7h-5Z"/></svg>',
  };

  const openModal = (trigger) => {
    const { name, flavor, size, price, image, categorySlug, addUrl } = trigger.dataset;
    nameEl.textContent = name;
    flavorEl.textContent = flavor;
    sizeEl.textContent = size;
    priceEl.textContent = price;
    form.action = addUrl;
    media.innerHTML = image
      ? `<img src="${image}" alt="${name} - ${flavor}">`
      : `<div class="product-thumb quick-view-thumb">${categoryIcons[categorySlug] || ""}</div>`;

    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");

    if (window.gsap) {
      gsap.fromTo(modal, { opacity: 0 }, { opacity: 1, duration: 0.25 });
      gsap.fromTo(panel, { opacity: 0, scale: 0.9, y: 20 }, { opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "power3.out" });
    }
  };

  const closeModal = () => {
    const finish = () => {
      modal.classList.remove("is-open");
      modal.setAttribute("aria-hidden", "true");
      document.body.classList.remove("modal-open");
    };
    if (window.gsap) {
      gsap.to(panel, { opacity: 0, scale: 0.9, y: 20, duration: 0.25, ease: "power2.in" });
      gsap.to(modal, { opacity: 0, duration: 0.25, onComplete: finish });
    } else {
      finish();
    }
  };

  document.querySelectorAll(".quick-view-btn").forEach((btn) => {
    btn.addEventListener("click", () => openModal(btn));
  });

  modal.querySelectorAll("[data-modal-close]").forEach((el) => {
    el.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("is-open")) closeModal();
  });
}

function initNavMenu() {
  const toggle = document.getElementById("nav-toggle");
  const menu = document.getElementById("site-menu");
  const overlay = document.getElementById("menu-overlay");
  if (!toggle || !menu || !overlay) return;

  const links = Array.from(menu.querySelectorAll("a"));
  const focusables = () => [toggle, ...links];
  let lastFocused = null;

  const setState = (open) => {
    toggle.classList.toggle("is-active", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute(
      "aria-label",
      open ? toggle.dataset.labelClose : toggle.dataset.labelOpen
    );
    menu.classList.toggle("is-open", open);
    menu.setAttribute("aria-hidden", String(!open));
    overlay.classList.toggle("is-open", open);
    document.body.classList.toggle("nav-open", open);
  };

  const openMenu = () => {
    lastFocused = document.activeElement;
    setState(true);
    window.setTimeout(() => links[0] && links[0].focus(), 360);
  };
  const closeMenu = () => {
    setState(false);
    if (lastFocused && typeof lastFocused.focus === "function") lastFocused.focus();
  };

  toggle.addEventListener("click", () =>
    menu.classList.contains("is-open") ? closeMenu() : openMenu()
  );
  overlay.addEventListener("click", closeMenu);
  links.forEach((link) => link.addEventListener("click", closeMenu));

  document.addEventListener("keydown", (e) => {
    if (!menu.classList.contains("is-open")) return;
    if (e.key === "Escape") {
      closeMenu();
      return;
    }
    if (e.key === "Tab") {
      const items = focusables();
      const first = items[0];
      const last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
}

function initCartDrawer() {
  const button = document.getElementById("cart-button");
  const drawer = document.getElementById("cart-drawer");
  const overlay = document.getElementById("cart-overlay");
  const body = document.getElementById("cart-drawer-body");
  const badge = document.getElementById("cart-count-badge");
  if (!drawer || !overlay || !body) return;

  const navMenu = document.getElementById("site-menu");
  const navToggle = document.getElementById("nav-toggle");
  const navOverlay = document.getElementById("menu-overlay");

  const closeNav = () => {
    if (navMenu) navMenu.classList.remove("is-open"), navMenu.setAttribute("aria-hidden", "true");
    if (navToggle) navToggle.classList.remove("is-active"), navToggle.setAttribute("aria-expanded", "false");
    if (navOverlay) navOverlay.classList.remove("is-open");
    document.body.classList.remove("nav-open");
  };

  const openCart = () => {
    closeNav();
    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
    overlay.classList.add("is-open");
    document.body.classList.add("cart-open");
    if (button) button.setAttribute("aria-expanded", "true");
  };
  const closeCart = () => {
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    overlay.classList.remove("is-open");
    document.body.classList.remove("cart-open");
    if (button) button.setAttribute("aria-expanded", "false");
  };

  const updateCart = (data) => {
    if (badge) {
      badge.textContent = data.count;
      if (data.count > 0) badge.removeAttribute("hidden");
      else badge.setAttribute("hidden", "");
    }
    body.innerHTML = data.drawer_html;
  };

  const pulse = () => {
    if (!button) return;
    button.classList.remove("pulse");
    void button.offsetWidth;
    button.classList.add("pulse");
  };

  const closeQuickView = () => {
    const qv = document.getElementById("quick-view-modal");
    if (qv && qv.classList.contains("is-open")) {
      const closer = qv.querySelector("[data-modal-close]");
      if (closer) closer.click();
    }
  };

  const submitCart = async (form) => {
    try {
      const res = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-Cart-Ajax": "1" },
        credentials: "same-origin",
      });
      if (!res.ok) throw new Error("bad response");
      return await res.json();
    } catch (err) {
      return null;
    }
  };

  // Cart button opens the drawer (falls back to /cart link without JS)
  if (button) {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      drawer.classList.contains("is-open") ? closeCart() : openCart();
    });
  }
  overlay.addEventListener("click", closeCart);
  if (navToggle) navToggle.addEventListener("click", closeCart);

  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-cart-close]")) closeCart();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && drawer.classList.contains("is-open")) closeCart();
  });

  // Intercept add-to-cart and remove forms for instant, no-reload updates
  document.addEventListener("submit", async (e) => {
    const addForm = e.target.closest(".add-to-cart-form");
    const removeForm = e.target.closest(".cart-remove-form");
    if (!addForm && !removeForm) return;
    e.preventDefault();
    const form = addForm || removeForm;
    const data = await submitCart(form);
    if (!data) {
      form.submit();
      return;
    }
    updateCart(data);
    if (addForm) {
      closeQuickView();
      pulse();
      openCart();
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initPageLoader();
  initSmoothScroll();
  initScrollReveal();
  initNavbarScrollShadow();
  initNavMenu();
  initCartDrawer();
  initHeroParallax();
  initCardTilt(".product-card, .service-card");
  initButtonRipple();
  initCounters();
  initQuickView();
});
