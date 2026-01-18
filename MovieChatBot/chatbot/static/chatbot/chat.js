const chatLog = document.getElementById("chatLog");
const msg = document.getElementById("msg");
const send = document.getElementById("send");

function addBubble(role, text) {
  const div = document.createElement("div");
  div.className = "bubble " + (role === "me" ? "me" : "bot");
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
  return div;
}

function addIntro() {
  addBubble(
    "bot",
    "안녕하세요! 저는 당신의 영화 리뷰/컬렉션을 바탕으로 영화를 추천해드리는 AI입니다.\n어떤 영화를 찾고 계신가요?"
  );
}

async function sendMessage(text) {
  const t = (text || "").trim();
  if (!t) return;

  addBubble("me", t);
  msg.value = "";
  send.disabled = true;

  const loadingBubble = addBubble("bot", "생성 중...");

  try {
    const res = await fetch(CHAT_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": CSRF_TOKEN,
      },
      body: JSON.stringify({ message: t }),
    });

    const data = await res.json();
    loadingBubble.textContent = data.answer || "(응답 없음)";
  } catch (e) {
    loadingBubble.textContent = "오류가 났습니다. 잠시 후 다시 시도해 주세요.";
  } finally {
    send.disabled = false;
    msg.focus();
  }
}

// 이벤트
msg.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendMessage(msg.value);
  }
});

send.addEventListener("click", () => sendMessage(msg.value));

document.querySelectorAll(".chip").forEach(btn => {
  btn.addEventListener("click", () => sendMessage(btn.dataset.chip));
});

addIntro();
