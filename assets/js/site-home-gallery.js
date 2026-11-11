(() => {
  const photoDialog = document.querySelector("#tn-photo-dialog");
  const photoImage = photoDialog?.querySelector("[data-photo-current]");
  const photoCaption = photoDialog?.querySelector("[data-photo-caption]");
  const videoDialog = document.querySelector("#tn-video-dialog");
  let photos = [];
  let photoIndex = 0;

  const imagesFor = (setName) => {
    const source = [...document.querySelectorAll(".tn-photo-source[data-photo-set]")]
      .find((node) => node.dataset.photoSet === setName);
    return source ? [...source.querySelectorAll("img")].map((img) => ({ src: img.src, alt: img.alt })) : [];
  };

  const showPhoto = (index) => {
    if (!photoDialog || !photoImage || !photos.length) return;
    photoIndex = (index + photos.length) % photos.length;
    const photo = photos[photoIndex];
    photoImage.src = photo.src;
    photoImage.alt = photo.alt;
    if (photoCaption) photoCaption.textContent = `${photo.alt} · ${photoIndex + 1}/${photos.length}`;
    if (!photoDialog.open) photoDialog.showModal();
  };

  document.querySelectorAll("[data-open-photo-gallery]").forEach((button) => {
    button.addEventListener("click", () => {
      photos = imagesFor(button.dataset.openPhotoGallery);
      showPhoto(0);
    });
  });

  const complexGallery = document.querySelector(".tn-photo-grid[data-photo-set='complejo']");
  complexGallery?.querySelectorAll("[data-photo-index]").forEach((button) => {
    button.addEventListener("click", () => {
      photos = imagesFor("complejo");
      showPhoto(Number(button.dataset.photoIndex) || 0);
    });
  });

  photoDialog?.querySelector("[data-close-photo]")?.addEventListener("click", () => photoDialog.close());
  photoDialog?.querySelector("[data-photo-prev]")?.addEventListener("click", () => showPhoto(photoIndex - 1));
  photoDialog?.querySelector("[data-photo-next]")?.addEventListener("click", () => showPhoto(photoIndex + 1));
  photoDialog?.addEventListener("click", (event) => {
    if (event.target === photoDialog) photoDialog.close();
  });

  const closeVideo = () => {
    const video = videoDialog?.querySelector("video");
    video?.pause();
    if (video) video.currentTime = 0;
    if (videoDialog?.open) videoDialog.close();
  };
  document.querySelectorAll("[data-open-video]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (!videoDialog) return;
      videoDialog.showModal();
      try { await videoDialog.querySelector("video")?.play(); } catch { /* El usuario puede iniciar el video con el control nativo. */ }
    });
  });
  videoDialog?.querySelector("[data-close-video]")?.addEventListener("click", closeVideo);
  videoDialog?.addEventListener("click", (event) => {
    if (event.target === videoDialog) closeVideo();
  });
  videoDialog?.addEventListener("close", () => videoDialog.querySelector("video")?.pause());

  photoDialog?.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") showPhoto(photoIndex - 1);
    if (event.key === "ArrowRight") showPhoto(photoIndex + 1);
  });
})();
