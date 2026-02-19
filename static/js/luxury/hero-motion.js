import { EASING, SELECTORS, TIMING } from "./config.js";

export class HeroMotion {
  constructor({ reducedMotion }) {
    this.reducedMotion = reducedMotion;
    this.hero = null;
    this.pointerX = 0;
    this.pointerY = 0;
  }

  init() {
    this.hero = document.querySelector(SELECTORS.hero);
    if (!this.hero) {
      return;
    }

    this.prepareHeading();
    this.playIntro();
    this.bindParallax();
  }

  prepareHeading() {
    const heading = this.hero.querySelector(SELECTORS.heroHeading);
    if (!heading || heading.dataset.splitReady === "true") {
      return;
    }

    const words = heading.textContent.trim().split(/\s+/);
    heading.innerHTML = words.map((word) => `<span class="hero-word">${word}</span>`).join(" ");
    heading.dataset.splitReady = "true";
  }

  playIntro() {
    const headingWords = this.hero.querySelectorAll(".hero-word");
    const revealTargets = this.hero.querySelectorAll(SELECTORS.chapterReveal);
    const ctas = this.hero.querySelectorAll(SELECTORS.heroCta);

    if (this.reducedMotion || !window.gsap) {
      revealTargets.forEach((item) => item.classList.add("is-visible"));
      ctas.forEach((button) => button.classList.add("is-visible"));
      return;
    }

    window.gsap.set(revealTargets, { autoAlpha: 0, y: 18, filter: "blur(8px)" });
    window.gsap.set(ctas, { autoAlpha: 0, y: 16 });
    window.gsap.set(headingWords, { autoAlpha: 0, yPercent: 40 });

    window.gsap
      .timeline({ defaults: { ease: EASING.softOut } })
      .to(headingWords, {
        autoAlpha: 1,
        yPercent: 0,
        duration: TIMING.reveal.section,
        stagger: 0.055,
      })
      .to(
        revealTargets,
        {
          autoAlpha: 1,
          y: 0,
          filter: "blur(0px)",
          duration: 0.96,
          stagger: 0.12,
        },
        0.2,
      )
      .to(
        ctas,
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.82,
          stagger: 0.12,
          ease: EASING.smoothOut,
        },
        0.62,
      );
  }

  bindParallax() {
    if (this.reducedMotion) {
      return;
    }

    this.hero.addEventListener("pointermove", (event) => {
      const rect = this.hero.getBoundingClientRect();
      const normalizedX = (event.clientX - rect.left) / rect.width - 0.5;
      const normalizedY = (event.clientY - rect.top) / rect.height - 0.5;
      this.pointerX = normalizedX;
      this.pointerY = normalizedY;
      this.hero.style.setProperty("--hero-pointer-x", `${normalizedX.toFixed(4)}`);
      this.hero.style.setProperty("--hero-pointer-y", `${normalizedY.toFixed(4)}`);
    });

    this.hero.addEventListener("pointerleave", () => {
      this.pointerX = 0;
      this.pointerY = 0;
      this.hero.style.setProperty("--hero-pointer-x", "0");
      this.hero.style.setProperty("--hero-pointer-y", "0");
    });
  }
}
