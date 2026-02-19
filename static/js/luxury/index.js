import { HeroMotion } from "./hero-motion.js";
import { ReducedMotionFallback } from "./reduced-motion-fallback.js";
import { ScrollChapters } from "./scroll-chapters.js";
import { SELECTORS } from "./config.js";
import { TransitionOverlay } from "./transition-overlay.js";
import { WebGLEnhancer } from "./webgl-enhancer.js";

const interactiveSelector = "a, button, .btn, input, select, textarea, [role='button']";

function initLuxuryExperience() {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.documentElement.classList.add("luxury-motion-ready");

  const reducedMotionFallback = new ReducedMotionFallback({ reducedMotion });
  reducedMotionFallback.init();

  const transitionOverlay = new TransitionOverlay({ reducedMotion });
  transitionOverlay.init();

  const heroMotion = new HeroMotion({ reducedMotion });
  heroMotion.init();

  const scrollChapters = new ScrollChapters({ reducedMotion });
  scrollChapters.init();

  const webglEnhancer = new WebGLEnhancer({ reducedMotion });
  webglEnhancer.init();

  setupCursor({ reducedMotion });
  enhanceLinkStyles();
}

function enhanceLinkStyles() {
  document.querySelectorAll("a").forEach((link) => {
    link.classList.add("luxury-link");
  });
}

function setupCursor({ reducedMotion }) {
  const cursor = document.querySelector(SELECTORS.cursor);
  if (!cursor || reducedMotion || window.matchMedia("(pointer: coarse)").matches) {
    if (cursor) {
      cursor.hidden = true;
    }
    return;
  }

  let pointerX = window.innerWidth / 2;
  let pointerY = window.innerHeight / 2;
  let currentX = pointerX;
  let currentY = pointerY;

  cursor.hidden = false;
  document.body.classList.add("luxury-cursor-enabled");

  window.addEventListener(
    "pointermove",
    (event) => {
      pointerX = event.clientX;
      pointerY = event.clientY;
    },
    { passive: true },
  );

  document.querySelectorAll(interactiveSelector).forEach((element) => {
    element.addEventListener("mouseenter", () => cursor.classList.add("is-active"));
    element.addEventListener("mouseleave", () => cursor.classList.remove("is-active"));
    element.addEventListener("focus", () => cursor.classList.add("is-active"));
    element.addEventListener("blur", () => cursor.classList.remove("is-active"));
  });

  const tick = () => {
    currentX += (pointerX - currentX) * 0.2;
    currentY += (pointerY - currentY) * 0.2;
    const halfW = cursor.offsetWidth / 2;
    const halfH = cursor.offsetHeight / 2;
    cursor.style.transform = `translate3d(${currentX - halfW}px, ${currentY - halfH}px, 0)`;
    window.requestAnimationFrame(tick);
  };
  tick();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initLuxuryExperience, { once: true });
} else {
  initLuxuryExperience();
}
