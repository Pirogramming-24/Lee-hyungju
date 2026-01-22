const input = document.getElementById("sum-in");
  const out = document.getElementById("sum-out");
  const runBtn = document.getElementById("sum-run");

  const clearInBtn = document.getElementById("clear-in-btn");
  const copyOutBtn = document.getElementById("copy-out-btn");
  const clearOutBtn = document.getElementById("clear-out-btn");

  const outTitle = document.getElementById("out-title");
  const btnOutEn = document.getElementById("btn-out-en");
  const btnOutKo = document.getElementById("btn-out-ko");

  let outputLang = "en"; // "en" | "ko"
  let sending = false;

  function setOutLang(lang){
    outputLang = lang;
    if(lang === "en"){
      btnOutEn.classList.add("active");
      btnOutKo.classList.remove("active");
      outTitle.textContent = "출력 (영어 요약)";
    } else {
      btnOutKo.classList.add("active");
      btnOutEn.classList.remove("active");
      outTitle.textContent = "출력 (한국어 요약)";
    }
  }

  async function run(){
    if(sending) return;
    const text = (input.value || "").trim();
    if(!text) return;

    sending = true;
    runBtn.disabled = true;
    out.textContent = "요약 중...";

    try{
      const res = await fetch("/api/summarize/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, output_lang: outputLang }),
      });
      const data = await res.json().catch(()=>({}));
      if(!res.ok){
        out.textContent = data.error || `에러 (${res.status})`;
        return;
      }
      out.textContent = data.result || "";
    }catch(e){
      out.textContent = "서버 연결 실패";
    }finally{
      sending = false;
      runBtn.disabled = false;
    }
  }

  runBtn.onclick = run;
  btnOutEn.onclick = () => setOutLang("en");
  btnOutKo.onclick = () => setOutLang("ko");

  input.addEventListener("keydown", (e) => {
    if(e.key === "Enter" && (e.ctrlKey || e.metaKey)){
      e.preventDefault();
      run();
    }
  });

  clearInBtn.onclick = () => { input.value = ""; input.focus(); };
  copyOutBtn.onclick = async () => {
    const t = (out.textContent || "").trim();
    if(!t) return;
    try { await navigator.clipboard.writeText(t); } catch(e) {}
  };
  clearOutBtn.onclick = () => { out.textContent = ""; };

  setOutLang("en");