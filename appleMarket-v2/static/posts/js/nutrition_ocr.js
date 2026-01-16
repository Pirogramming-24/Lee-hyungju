(function () {
  
  const LOG = (...args) => console.log("[NUTRI-OCR]", ...args);

  LOG("js loaded, href=", location.href);

  const form = document.getElementById("postForm");
  LOG("form=", form);
  if (!form) return;

  const statusEl = document.getElementById("ocr_status");
  const setStatus = (msg) => {
    if (statusEl) statusEl.textContent = msg;
    LOG("status:", msg);
  };

  const getCookie = (name) => {
    const v = document.cookie.split("; ").find((row) => row.startsWith(name + "="));
    return v ? decodeURIComponent(v.split("=")[1]) : "";
  };

  // URL: 여기만 맞추면 됨
  const CREATE_URL = "/api/nutrition-ocr/";
  const STATUS_URL = (id) => `/api/nutrition-ocr/${id}/`;
  LOG("CREATE_URL=", CREATE_URL);

  // 파일 input 찾기
  // OCR 트리거는 영양성분 이미지 필드만
  const fileInput = form.querySelector('input[type="file"][name="nutrition_image"]');


  LOG("fileInput=", fileInput, "name=", fileInput?.name, "id=", fileInput?.id);
  if (!fileInput) {
    setStatus("영양성분 이미지 필드(nutrition_image)가 없습니다.");
    return;
  }

  // 채울 input들
  const kcalEl = form.querySelector('[name="kcal"]');
  const carbEl = form.querySelector('[name="carb_g"]');
  const proteinEl = form.querySelector('[name="protein_g"]');
  const fatEl = form.querySelector('[name="fat_g"]');

  if (statusEl && kcalEl) {
    const p = kcalEl.closest("p") || kcalEl.parentElement;
    if (p) p.before(statusEl);
  }
  
  LOG("targets:", {
    kcal: kcalEl?.name, carb: carbEl?.name, protein: proteinEl?.name, fat: fatEl?.name
  });

  function setDisabled(disabled) {
    [kcalEl, carbEl, proteinEl, fatEl].forEach(el => {
      if (!el) return;
      el.disabled = disabled;
      el.style.backgroundColor = disabled ? "#f5f5f5" : "";
    });
  }


  async function safeReadText(res) {
    try { return await res.text(); } catch { return ""; }
  }

  async function startOCR(file) {

    setDisabled(true);
    setStatus("📸 영양성분 인식 중...");

    LOG("startOCR file=", { name: file.name, type: file.type, size: file.size });
    setStatus("OCR 처리 중...");

    const fd = new FormData();
    fd.append("image", file);

    const csrftoken = getCookie("csrftoken");
    LOG("csrftoken exists? ", !!csrftoken);

    let res;
    try {
      res = await fetch(CREATE_URL, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        body: fd,
      });
    } catch (e) {
      LOG("POST network error:", e);
      setStatus("네트워크 에러(POST)");
      return;
    }

    const raw = await safeReadText(res);
    LOG("POST response status=", res.status, "raw=", raw);

    let data;
    try {
      data = JSON.parse(raw);
    } catch {
      setStatus(`POST 응답이 JSON이 아님 (status=${res.status})`);
      return;
    }

    if (!data.ok) {
      setStatus("OCR 시작 실패: " + (data.error || "unknown"));
      return;
    }

    LOG("job created:", data);
    pollJob(data.job_id);
  }

  async function pollJob(jobId) {
    LOG("pollJob start jobId=", jobId);

    const intervalMs = 700;
    const maxTries = 80;

    for (let i = 0; i < maxTries; i++) {
      let res;
      try {
        res = await fetch(STATUS_URL(jobId));
      } catch (e) {
        LOG("GET network error:", e);
        setStatus("네트워크 에러(GET)");
        return;
      }

      const raw = await safeReadText(res);
      LOG(`GET try=${i} status=${res.status} raw=`, raw);

      let data;
      try {
        data = JSON.parse(raw);
      } catch {
        setStatus(`GET 응답이 JSON이 아님 (status=${res.status})`);
        return;
      }

      if (!data.ok) {
        setStatus("OCR 조회 실패: " + (data.error || "unknown"));
        return;
      }

      if (data.status === "SUCCESS") {
        const r = data.result || {};

        if (kcalEl) kcalEl.value = r.kcal ?? "";
        if (carbEl) carbEl.value = r.carb_g ?? "";
        if (proteinEl) proteinEl.value = r.protein_g ?? "";
        if (fatEl) fatEl.value = r.fat_g ?? "";

        setDisabled(false);
        setStatus("영양성분 자동 입력 완료");
        return;
      }

      if (data.status === "FAIL") {
        LOG("FAIL error=", data.error);
        setDisabled(false);
        setStatus("OCR 실패: " + (data.error || "unknown"));
        return;
      }

      setStatus(`OCR 처리 중... (${data.status})`);
      await new Promise((r) => setTimeout(r, intervalMs));
    }
    setDisabled(false);
    setStatus("OCR 시간 초과");
  }

  fileInput.addEventListener("change", (e) => {
    LOG("fileInput change fired");
    const file = e.target.files && e.target.files[0];
    LOG("selected file=", file);
    if (!file) return;
    startOCR(file);
  });

  LOG("listener attached");
})();
