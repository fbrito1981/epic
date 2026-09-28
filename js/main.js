const toggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".nav");

toggle.addEventListener("click", () => {
  const open = nav.classList.toggle("is-open");
  toggle.setAttribute("aria-expanded", String(open));
});

nav.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
  });
});

const dialog = document.querySelector(".lightbox");
const shot = dialog.querySelector("img");
const caption = dialog.querySelector("figcaption");

document.querySelectorAll("[data-full]").forEach((button) => {
  button.addEventListener("click", () => {
    shot.src = button.dataset.full;
    shot.alt = button.dataset.alt;
    caption.textContent = button.dataset.caption;
    dialog.showModal();
  });
});

dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});
