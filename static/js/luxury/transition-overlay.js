import { EASING, SELECTORS, TIMING } from "./config.js";

const PAGE_SCROLL_KEY = "pa-scroll-position:";
const PREFETCHED_KEY = "pa-prefetched:";

export class TransitionOverlay {
  constructor({ reducedMotion }) {
    this.reducedMotion = reducedMotion;
    this.overlay = null;
    this.line = null;
    this.accent = null;
    this.loader = null;
    this.loaderLine = null;
    this.loaderLogo = null;
    this.isTransitioning = false;
    this.prefetched = new Set();
  }

  init() {
    this.overlay = document.querySelector(SELECTORS.transitionOverlay);
    this.line = document.querySelector(SELECTORS.transitionLine);
    this.accent = document.querySelector(SELECTORS.transitionAccent);
    this.loader = document.querySelector(SELECTORS.entryLoader);
    this.loaderLine = this.loader?.querySelector(".entry-loader__line");
    this.loaderLogo = this.loader?.querySelector(".entry-loader__logo");

    this.setupScrollRestoration();
    this.bindPrefetch();
    this.bindInternalLinks();
    this.playEntryLoader();
  }

  setupScrollRestoration() {
    if ("scrollRestoration" in history) {
      history.scrollRestoration = "manual";
    }

    const navigationEntry = performance.getEntriesByType("navigation")[0];
    const shouldRestore = navigationEntry?.type === "back_forward";
    if (shouldRestore) {
      const stored = sessionStorage.getItem(this.getPageScrollStorageKey(window.location.href));
      if (stored !== null) {
        const y = Number.parseInt(stored, 10);
        if (Number.isFinite(y)) {
          window.scrollTo({ top: y, behavior: "auto" });
        }
      }
    }

    const saveScroll = () => {
      sessionStorage.setItem(this.getPageScrollStorageKey(window.location.href), String(window.scrollY));
    };
    window.addEventListener("pagehide", saveScroll, { passive: true });
    window.addEventListener("beforeunload", saveScroll, { passive: true });
  }

  bindPrefetch() {
    const links = document.querySelectorAll("a[href]");
    links.forEach((anchor) => {
      const prefetch = () => {
        const url = this.getInternalUrl(anchor);
        if (!url) {
          return;
        }
        const prefetchKey = `${PREFETCHED_KEY}${url.href}`;
        if (this.prefetched.has(prefetchKey)) {
          return;
        }
        this.prefetched.add(prefetchKey);
        const hint = document.createElement("link");
        hint.rel = "prefetch";
        hint.href = url.href;
        document.head.appendChild(hint);
      };
      anchor.addEventListener("mouseenter", prefetch, { passive: true });
      anchor.addEventListener("focus", prefetch, { passive: true });
    });
  }

  bindInternalLinks() {
    const links = document.querySelectorAll("a[href]");
    links.forEach((anchor) => {
      anchor.addEventListener("click", (event) => {
        const url = this.getInternalUrl(anchor);
        if (!this.shouldHandleTransition(event, anchor, url)) {
          return;
        }
        event.preventDefault();
        sessionStorage.setItem(this.getPageScrollStorageKey(window.location.href), String(window.scrollY));
        this.animateToNextPage(url.href);
      });
    });
  }

  shouldHandleTransition(event, anchor, url) {
    if (!url || !this.overlay || !this.line || !this.accent) {
      return false;
    }
    if (this.reducedMotion || this.isTransitioning) {
      return false;
    }
    if (event.defaultPrevented || event.button !== 0) {
      return false;
    }
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return false;
    }
    if (anchor.hasAttribute("download")) {
      return false;
    }
    if (anchor.target && anchor.target !== "_self") {
      return false;
    }
    if (anchor.dataset.noTransition === "true") {
      return false;
    }
    if (url.origin !== window.location.origin) {
      return false;
    }
    if (url.pathname === window.location.pathname && url.search === window.location.search) {
      return false;
    }
    return true;
  }

  getInternalUrl(anchor) {
    const raw = anchor.getAttribute("href");
    if (!raw || raw.startsWith("#") || raw.startsWith("mailto:") || raw.startsWith("tel:")) {
      return null;
    }
    try {
      return new URL(anchor.href, window.location.origin);
    } catch (_error) {
      return null;
    }
  }

  animateToNextPage(href) {
    this.isTransitioning = true;
    document.documentElement.classList.add("is-transitioning");

    if (!window.gsap) {
      this.overlay.classList.add("is-active");
      window.setTimeout(() => {
        window.location.assign(href);
      }, 280);
      return;
    }

    window.gsap.set(this.overlay, { autoAlpha: 0, pointerEvents: "none", filter: "blur(10px)" });
    window.gsap.set(this.line, { scaleX: 0, transformOrigin: "left center" });
    window.gsap.set(this.accent, { xPercent: -110 });

    window.gsap
      .timeline({
        defaults: { ease: EASING.softOut },
        onComplete: () => {
          window.location.assign(href);
        },
      })
      .set(this.overlay, { pointerEvents: "auto" })
      .to(this.overlay, { autoAlpha: 1, filter: "blur(0px)", duration: 0.34 }, 0)
      .to(this.line, { scaleX: 1, duration: TIMING.transition.reveal, ease: EASING.smoothOut }, 0.06)
      .to(this.accent, { xPercent: 115, duration: TIMING.transition.enter, ease: EASING.softInOut }, 0.1);
  }

  playEntryLoader() {
    if (!this.loader) {
      return;
    }

    if (this.reducedMotion || !window.gsap) {
      this.loader.classList.add("is-hidden");
      window.setTimeout(() => this.loader?.remove(), 280);
      return;
    }

    window.gsap
      .timeline({ defaults: { ease: EASING.softOut } })
      .fromTo(this.loaderLogo, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.42 })
      .fromTo(this.loaderLine, { scaleX: 0, transformOrigin: "left center" }, { scaleX: 1, duration: TIMING.loader.line, ease: EASING.smoothOut }, 0.08)
      .to(this.loader, {
        autoAlpha: 0,
        duration: 0.32,
        delay: 0.08,
        onComplete: () => {
          this.loader.remove();
        },
      });
  }

  getPageScrollStorageKey(href) {
    return `${PAGE_SCROLL_KEY}${href}`;
  }
}
