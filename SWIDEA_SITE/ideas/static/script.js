const csrftoken = document.getElementById("csrf-token").value;

const filledStar = `
<svg viewBox="0 0 24 24" width="18" height="18">
  <path fill="currentColor" d="M12 17.3l-6.18 3.73 1.64-7.03L2 9.24l7.19-.61L12 2l2.81 6.63 7.19.61-5.46 4.76 1.64 7.03z"/>
</svg>
`;

const emptyStar = `
<svg viewBox="0 0 24 24" width="18" height="18">
  <path fill="none" stroke="currentColor" stroke-width="2"
    d="M12 2l2.81 6.63 7.19.61-5.46 4.76 1.64 7.03L12 17.3l-6.18 3.73 1.64-7.03L2 9.24l7.19-.61z"/>
</svg>
`;

document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".star-btn");
  if (!btn) return;

  e.preventDefault();      // 기본 동작 막기
  e.stopPropagation();     // a 태그로 이벤트 전파 차단


  const url = btn.dataset.url;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    });
    const data = await res.json();
    
    btn.classList.toggle("is-filled", data.starred);
    btn.classList.toggle("is-empty", !data.starred);

    btn.querySelector(".star-icon").innerHTML =
      data.starred ? filledStar : emptyStar;

  } catch {
    alert("찜 처리 실패");
  }
});

document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".interest-btn");
  if (!btn) return;

  e.preventDefault();
  e.stopPropagation();

  const url = btn.dataset.url;
  const action = btn.dataset.action;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
      body: new URLSearchParams({ action }),
    });

    const data = await res.json();
    btn.parentElement.querySelector(".interest-value").textContent = data.interest;

  } catch {
    alert("관심도 처리 실패");
  }
});
