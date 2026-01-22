// static/js/like.js
function getCookie(name) {
  const v = document.cookie.split("; ").find((row) => row.startsWith(name + "="));
  return v ? decodeURIComponent(v.split("=")[1]) : null;
}

document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-like-btn]");
  if (!btn) return;

  const postId = btn.dataset.postId;
  const url = `/posts/${postId}/like/`;
  const csrftoken = getCookie("csrftoken");

  const res = await fetch(url, {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
  });

  if (!res.ok) return;

  const data = await res.json();
  btn.classList.toggle("liked", data.liked);

  const wrap = btn.closest("[data-post]") || document;
  const cnt = wrap.querySelector("[data-like-count]");
  if (cnt) cnt.textContent = data.like_count;
});
