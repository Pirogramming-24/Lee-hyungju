function calcScaledHeight(img, targetWidth) {
  if (!img.naturalWidth || !img.naturalHeight) return 0;
  return Math.round(img.naturalHeight * (targetWidth / img.naturalWidth));
}

// static/js/carousel.js
function initCarousel(root) {
  const imgs = Array.from(root.querySelectorAll(".carousel-img"));
  const prevBtn = root.querySelector("[data-prev]");
  const nextBtn = root.querySelector("[data-next]");
  const dotsWrap = root.querySelector("[data-dots]");

  if (imgs.length === 0) return;

  dotsWrap.innerHTML = "";
  const dots = imgs.map((_, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "carousel-dot";
    b.addEventListener("click", () => setIndex(i));
    dotsWrap.appendChild(b);
    return b;
  });

  let index = 0;

  function updateUI() {
    const multi = imgs.length > 1;
    dotsWrap.style.display = multi ? "flex" : "none";
    // 버튼 기본 표시 여부는 setIndex에서 결정
  }

  function setIndex(i) {
    index = (i + imgs.length) % imgs.length;

    imgs.forEach((img, k) => img.classList.toggle("is-active", k === index));
    dots.forEach((d, k) => d.classList.toggle("is-active", k === index));

    // ✅ 경계에서 화살표 숨김
    prevBtn.style.display = index === 0 ? "none" : "inline-flex";
    nextBtn.style.display = index === imgs.length - 1 ? "none" : "inline-flex";
  }

  setIndex(0);
  updateUI();

  prevBtn.addEventListener("click", () => setIndex(index - 1));
  nextBtn.addEventListener("click", () => setIndex(index + 1));
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-carousel]").forEach(initCarousel);
});
