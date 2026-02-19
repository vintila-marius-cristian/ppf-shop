import { SELECTORS } from "./config.js";

export class ReducedMotionFallback {
  constructor({ reducedMotion }) {
    this.reducedMotion = reducedMotion;
  }

  init() {
    if (!this.reducedMotion) {
      return;
    }

    document.documentElement.classList.add("reduced-motion");
    document.body.classList.add("reduced-motion");
    this.revealStatically();
    this.disableCursor();
  }

  revealStatically() {
    document.querySelectorAll(SELECTORS.chapterReveal).forEach((element) => {
      element.classList.add("is-visible");
    });
  }

  disableCursor() {
    const cursor = document.querySelector(SELECTORS.cursor);
    if (cursor) {
      cursor.hidden = true;
    }
  }
}
