(() => {
  const input = document.getElementById("tr-in");
  const out = document.getElementById("tr-out");
  const runBtn = document.getElementById("tr-run");

  const koenBtn = document.getElementById("btn-ko-en");
  const enkoBtn = document.getElementById("btn-en-ko");
  const dirLabel = document.getElementById("dir-label");
  const outLabel = document.getElementById("out-label");

  const copyBtn = document.getElementById("copy-btn");
  const clearBtn = document.getElementById("clear-btn");

  let direction = "ko_en";
  let sending = false;

  function setDir(dir) {
    direction = dir;
    if (dir === "ko_en") {
      koenBtn.classList.add("active");
      enkoBtn.classList.remove("active");
      dirLabel.textContent = "입력 (한국어)";
      outLabel.textContent = "출력 (영어)";
      input.placeholder = "한국어를 입력하세요";
    } else {
      enkoBtn.classList.add("active");
      koenBtn.classList.remove("active");
      dirLabel.textContent = "입력 (영어)";
      outLabel.textContent = "출력 (한국어)";
      input.placeholder = "Enter English text";
    }
  }

  async function run() {
    if (sending) return;
    const text = (input.value || "").trim();
    if (!text) return;

    sending = true;
    runBtn.disabled = true;
    koenBtn.disabled = true;
    enkoBtn.disabled = true;

    out.textContent = "번역 중...";

    try {
      const res = await fetch("/api/translate/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, direction }),
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        out.textContent = data.error || `에러 (${res.status})`;
        return;
      }
      out.textContent = data.result || "";
    } catch (e) {
      out.textContent = "서버 연결 실패";
    } finally {
      sending = false;
      runBtn.disabled = false;
      koenBtn.disabled = false;
      enkoBtn.disabled = false;
    }
  }

  koenBtn.addEventListener("click", () => setDir("ko_en"));
  enkoBtn.addEventListener("click", () => setDir("en_ko"));
  runBtn.addEventListener("click", run);

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      run();
    }
  });

  copyBtn.addEventListener("click", async () => {
    const t = (out.textContent || "").trim();
    if (!t) return;
    try { await navigator.clipboard.writeText(t); } catch {}
  });

  clearBtn.addEventListener("click", () => {
    input.value = "";
    out.textContent = "";
    input.focus();
  });

  setDir("ko_en");
})();
