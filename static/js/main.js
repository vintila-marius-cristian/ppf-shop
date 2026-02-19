(function () {
  const slides = Array.from(document.querySelectorAll("[data-slider] .testimonial-slide"));
  if (slides.length > 1) {
    let current = 0;
    setInterval(() => {
      slides[current].classList.remove("active");
      current = (current + 1) % slides.length;
      slides[current].classList.add("active");
    }, 5000);
  }

  const cookieBanner = document.getElementById("cookieBanner");
  if (cookieBanner && !localStorage.getItem("cookieConsent")) {
    cookieBanner.hidden = false;
  }

  const acceptBtn = document.getElementById("acceptCookies");
  const declineBtn = document.getElementById("declineCookies");

  const setConsent = (value) => {
    localStorage.setItem("cookieConsent", value);
    if (cookieBanner) cookieBanner.hidden = true;
  };

  if (acceptBtn) acceptBtn.addEventListener("click", () => setConsent("accepted"));
  if (declineBtn) declineBtn.addEventListener("click", () => setConsent("declined"));

  const contactForm = document.getElementById("contactForm");
  if (contactForm) {
    contactForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData(contactForm);
      const csrfToken = formData.get("csrfmiddlewaretoken");

      const payload = {
        name: formData.get("name"),
        email: formData.get("email"),
        phone: formData.get("phone"),
        subject: formData.get("subject"),
        message: formData.get("message"),
      };

      try {
        const response = await fetch("/api/contact/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error("Contact API request failed");
        }

        await fetch("/api/track/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            event_type: "contact_submit",
            element: "contact_form",
            page: window.location.pathname,
            additional_data: { source: "contact_api_success" },
            session_id: localStorage.getItem("pa_session_id") || "",
          }),
          keepalive: true,
        }).catch(() => null);

        contactForm.reset();
        alert("Mesaj trimis cu succes. Revenim cu un raspuns in cel mai scurt timp.");
      } catch (_error) {
        alert("Nu am putut trimite mesajul acum. Te rugam sa incerci din nou.");
      }
    });
  }

  const galleryModalEl = document.getElementById("galleryPreviewModal");
  if (galleryModalEl && window.bootstrap) {
    const galleryModal = new bootstrap.Modal(galleryModalEl);
    const previewImage = document.getElementById("galleryPreviewImage");
    const previewVideo = document.getElementById("galleryPreviewVideo");
    const previewTitle = document.getElementById("galleryPreviewLabel");
    const previewCaption = document.getElementById("galleryPreviewCaption");

    const closePreviewVideo = () => {
      if (!previewVideo) return;
      previewVideo.pause();
      previewVideo.removeAttribute("src");
      previewVideo.load();
      previewVideo.hidden = true;
    };

    const openGalleryPreview = (button) => {
      const mediaType = button.dataset.galleryType || "image";
      const mediaSrc = button.dataset.gallerySrc || "";
      const mediaTitle = button.dataset.galleryTitle || "";
      const mediaCaption = button.dataset.galleryCaption || "";

      if (previewTitle) {
        previewTitle.textContent = mediaTitle;
        previewTitle.hidden = !mediaTitle.trim();
      }
      if (previewCaption) previewCaption.textContent = mediaCaption;

      if (mediaType === "video") {
        if (previewImage) {
          previewImage.hidden = true;
          previewImage.removeAttribute("src");
        }
        if (previewVideo) {
          previewVideo.hidden = false;
          previewVideo.src = mediaSrc;
          previewVideo.load();
        }
      } else {
        closePreviewVideo();
        if (previewImage) {
          previewImage.hidden = false;
          previewImage.src = mediaSrc;
          previewImage.alt = mediaTitle;
        }
      }

      galleryModal.show();
    };

    document.querySelectorAll("[data-gallery-open]").forEach((button) => {
      button.addEventListener("click", () => openGalleryPreview(button));
    });

    galleryModalEl.addEventListener("hidden.bs.modal", () => {
      closePreviewVideo();
      if (previewImage) {
        previewImage.hidden = true;
        previewImage.removeAttribute("src");
      }
    });
  }
})();
