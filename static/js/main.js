document.addEventListener("DOMContentLoaded", () => {
  const revealEls = document.querySelectorAll(".reveal");
  const reveal = (el) => el.classList.add("in-view");

  if (!("IntersectionObserver" in window)) {
    revealEls.forEach(reveal);
  } else {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            reveal(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    revealEls.forEach((el) => observer.observe(el));

    // Safety net: never leave content permanently invisible if the
    // observer doesn't fire for some reason.
    window.setTimeout(() => revealEls.forEach(reveal), 1500);
  }

  const navbar = document.querySelector(".navbar");
  if (navbar) {
    const updateNavbar = () => {
      navbar.classList.toggle("scrolled", window.scrollY > 20);
    };
    window.addEventListener("scroll", updateNavbar);
    updateNavbar();
  }
});
