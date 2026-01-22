// static/js/story.js
document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-story-view]");
  if (!root) return;

  const imgs = Array.from(root.querySelectorAll(".story-img"));
  const bars = Array.from(root.querySelectorAll(".bar-fill"));
  const prevBtn = root.querySelector("[data-prev]");
  const nextBtn = root.querySelector("[data-next]");
  const pauseBtn = root.querySelector("[data-pause]");
  const delForm = root.querySelector("[data-delete-form]");
  const nextStoryUrl = root.dataset.nextStoryUrl || null;

  
  let paused = false;

  if (imgs.length === 0) return;

  let idx = 0;
  const DURATION = 5000; // 5초
  let timer = null;
  let startAt = 0;

  function pause() {
    if (paused) return;
    paused = true;
    clearTimeout(timer);

    // 진행 중이던 bar 멈춤
    const b = bars[idx];
    const elapsed = Date.now() - startAt;
    const percent = Math.min(100, (elapsed / DURATION) * 100);
    b.style.transition = "none";
    b.style.width = percent + "%";

    pauseBtn.textContent = "▶";
  }

  function resume() {
    if (!paused) return;
    paused = false;

    const b = bars[idx];
    const currentWidth = parseFloat(b.style.width) || 0;
    const remain = DURATION * (1 - currentWidth / 100);

    startAt = Date.now() - (DURATION - remain);
    requestAnimationFrame(() => {
      b.style.transition = `width ${remain}ms linear`;
      b.style.width = "100%";
    });

    timer = setTimeout(() => {
      if (idx >= imgs.length - 1) {
        window.location.href = "/";
      } else {
        show(idx + 1);
      }
    }, remain);

    pauseBtn.textContent = "⏸";
  }

  function show(i) {
    idx = Math.max(0, Math.min(i, imgs.length - 1));
    imgs.forEach((img, k) => img.classList.toggle("is-active", k === idx));

    // bar 상태 초기화
    bars.forEach((b, k) => {
      b.style.transition = "none";
      b.style.width = k < idx ? "100%" : "0%";
    });

    prevBtn.style.display = idx === 0 ? "none" : "block";
    // nextBtn.style.display = "block";

    // paused면 재생 시작 금지(타이머/애니메이션 X)
    if (paused) {
      clearTimeout(timer);
      const b = bars[idx];
      b.style.transition = "none";
      b.style.width = "0%";   // 정지 상태에서 새 슬라이드면 0에서 멈춰있게
      return;
    }

    // 재생 상태일 때만 bar + timer 시작
    requestAnimationFrame(() => {
      const b = bars[idx];
      b.style.transition = `width ${DURATION}ms linear`;
      b.style.width = "100%";
    });

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
  nextBtn.addEventListener("click", () => {
    if (idx >= imgs.length - 1) {
      if (nextStoryUrl) {
        window.location.href = nextStoryUrl;
      } else {
        window.location.href = "/";
      }
    } else {
      show(idx + 1);
    }
  });

  pauseBtn.addEventListener("click", () => {
    paused ? resume() : pause();
  });
  

  // 첫 장 즉시 시작
  show(0);
  
});
