import { EASING, SELECTORS, TIMING } from "./config.js";

export class ScrollChapters {
  constructor({ reducedMotion }) {
    this.reducedMotion = reducedMotion;
    this.chapters = [];
  }

  init() {
    this.chapters = Array.from(document.querySelectorAll(SELECTORS.chapter));
    if (!this.chapters.length) {
      return;
    }

    if (this.reducedMotion) {
      this.revealStatically();
      return;
    }

    if (window.gsap && window.ScrollTrigger) {
      window.gsap.registerPlugin(window.ScrollTrigger);
      this.setupGsapChapters();
      return;
    }

    this.setupObserverFallback();
  }

  revealStatically() {
    this.chapters.forEach((chapter) => {
      chapter.classList.add("is-visible");
      chapter.querySelectorAll(SELECTORS.chapterReveal).forEach((item) => item.classList.add("is-visible"));
    });
  }

  setupGsapChapters() {
    this.chapters.forEach((chapter) => {
      const revealTargets = Array.from(chapter.querySelectorAll(SELECTORS.chapterReveal));
      if (revealTargets.length) {
        window.gsap.set(revealTargets, { autoAlpha: 0, y: 16, filter: "blur(8px)" });
        window.gsap.to(revealTargets, {
          autoAlpha: 1,
          y: 0,
          filter: "blur(0px)",
          duration: TIMING.reveal.section,
          stagger: TIMING.reveal.stagger,
          ease: EASING.softOut,
          scrollTrigger: {
            trigger: chapter,
            start: "top 80%",
            once: true,
          },
        });
      }

      this.animateChapterMicroEffects(chapter);

      window.ScrollTrigger.create({
        trigger: chapter,
        start: "top 72%",
        end: "bottom 30%",
        onEnter: () => chapter.classList.add("is-visible"),
        onLeave: () => chapter.classList.remove("is-visible"),
        onEnterBack: () => chapter.classList.add("is-visible"),
        onLeaveBack: () => chapter.classList.remove("is-visible"),
      });

      window.ScrollTrigger.create({
        trigger: chapter,
        start: "top bottom",
        end: "bottom top",
        onUpdate: (self) => {
          chapter.style.setProperty("--chapter-progress", self.progress.toFixed(4));
        },
      });
    });
  }

  animateChapterMicroEffects(chapter) {
    const effect = chapter.dataset.chapterEffect || "";
    const rule = chapter.querySelector(".chapter-rule");
    const corner = chapter.querySelector(".chapter-corner");

    if (rule) {
      window.gsap.set(rule, { scaleX: 0, transformOrigin: "left center" });
    }
    if (corner) {
      window.gsap.set(corner, { autoAlpha: 0, y: -6 });
    }

    if (effect === "rule-draw" && rule) {
      window.gsap.to(rule, {
        scaleX: 1,
        duration: 1.12,
        ease: EASING.smoothOut,
        scrollTrigger: {
          trigger: chapter,
          start: "top 78%",
          once: true,
        },
      });
    }

    if (effect === "corner-fold" && corner) {
      window.gsap.to(corner, {
        autoAlpha: 1,
        y: 0,
        duration: 0.88,
        ease: EASING.softOut,
        scrollTrigger: {
          trigger: chapter,
          start: "top 82%",
          once: true,
        },
      });
    }
  }

  setupObserverFallback() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            return;
          }
          entry.target.classList.add("is-visible");
          entry.target.querySelectorAll(SELECTORS.chapterReveal).forEach((item) => item.classList.add("is-visible"));
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.18 },
    );

    this.chapters.forEach((chapter) => observer.observe(chapter));
  }
}
