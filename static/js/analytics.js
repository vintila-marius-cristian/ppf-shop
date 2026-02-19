(function () {
  const endpoint = "/api/track/";

  const getSessionId = () => {
    const key = "pa_session_id";
    let sid = localStorage.getItem(key);
    if (!sid) {
      sid = `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
      localStorage.setItem(key, sid);
    }
    return sid;
  };

  const sendEvent = (eventType, element = "", additionalData = {}) => {
    const payload = {
      event_type: eventType,
      element,
      page: window.location.pathname,
      session_id: getSessionId(),
      additional_data: additionalData,
    };

    const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
    if (!navigator.sendBeacon || !navigator.sendBeacon(endpoint, blob)) {
      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        keepalive: true,
      }).catch(() => null);
    }
  };

  if (document.body?.dataset.trackPage === "true") {
    sendEvent("page_view", "body");
  }

  document.querySelectorAll("[data-track-event]").forEach((target) => {
    const ev = target.dataset.trackEvent;
    const element = target.dataset.trackElement || target.id || target.tagName.toLowerCase();
    target.addEventListener("click", () => sendEvent(ev, element));
  });

  let maxScrollDepth = 0;
  window.addEventListener(
    "scroll",
    () => {
      const scrollTop = window.scrollY;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      if (max <= 0) return;
      const depth = Math.round((scrollTop / max) * 100);
      if (depth > maxScrollDepth) maxScrollDepth = depth;
    },
    { passive: true },
  );

  window.addEventListener("beforeunload", () => {
    sendEvent("scroll_depth", "window", { depth: maxScrollDepth });
  });
})();
