export const TIMING = {
  loader: {
    total: 0.95,
    line: 0.72,
  },
  transition: {
    enter: 1.12,
    reveal: 1.04,
  },
  micro: {
    fast: 0.52,
    standard: 0.74,
  },
  reveal: {
    section: 1.16,
    stagger: 0.095,
  },
};

export const EASING = {
  smoothOut: "expo.out",
  softOut: "power3.out",
  softInOut: "power2.inOut",
};

export const SELECTORS = {
  entryLoader: "#entryLoader",
  transitionOverlay: "#transitionOverlay",
  transitionLine: ".transition-overlay__line",
  transitionAccent: ".transition-overlay__accent",
  hero: ".hero-section",
  heroHeading: "[data-hero-heading]",
  heroMotionTarget: "[data-hero-depth]",
  heroCta: "[data-hero-cta]",
  chapter: "[data-chapter]",
  chapterReveal: "[data-luxury-reveal]",
  webglMedia: "[data-webgl-media]",
  cursor: "#luxuryCursor",
  webglCanvas: "#webglEnhancerCanvas",
};

export const WEBGL = {
  maxMediaPlanes: 14,
  baseOpacity: 0.2,
  maxHoverOpacity: 0.34,
  waveAmplitude: 0.003,
};
