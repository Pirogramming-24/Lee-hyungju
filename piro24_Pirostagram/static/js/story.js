// static/js/story.js
document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-story-view]");
  if (!root) return;

  const imgs = Array.from(root.querySelectorAll(".story-img"));
  const bars = Array.from(root.querySelectorAll(".bar-fill"));
  const prevBtn = root.querySelector("[data-prev]");
  const nextBtn = root.querySelector("[data-next]");

  if (imgs.length === 0) return;

  let idx = 0;
  const DURATION = 3000; // 3초
  let timer = null;
  let startAt = 0;

  function show(i) {
    idx = Math.max(0, Math.min(i, imgs.length - 1));
    imgs.forEach((img, k) => img.classList.toggle("is-active", k === idx));

    // bar 상태 초기화
    bars.forEach((b, k) => {
      b.style.transition = "none";
      b.style.width = k < idx ? "100%" : "0%";
    });

    // 현재 bar 재생
    requestAnimationFrame(() => {
      const b = bars[idx];
      b.style.transition = `width ${DURATION}ms linear`;
      b.style.width = "100%";
    });

    prevBtn.style.display = idx === 0 ? "none" : "block";
    nextBtn.style.display = idx === imgs.length - 1 ? "none" : "block";

    restart();
  }

  function restart() {
    clearTimeout(timer);
    startAt = Date.now();
    timer = setTimeout(() => {
      if (idx >= imgs.length - 1) {
        // 마지막이면 닫기(피드로)
        window.location.href = "/";  // posts:feed가 / 라면 OK
      } else {
        show(idx + 1);
      }
    }, DURATION);
  }

  prevBtn.addEventListener("click", () => show(idx - 1));
  nextBtn.addEventListener("click", () => show(idx + 1));

  // 첫 장 즉시 시작
  show(0);
});
