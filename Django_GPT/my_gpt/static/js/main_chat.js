let conversationId = window.CONVERSATION_ID;

const chatBox = document.getElementById("chat-box");
const input = document.querySelector(".composer-input");
const btn = document.querySelector(".composer-btn");

function append(role, text) {
  const row = document.createElement("div");
  row.className = `msg ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  row.appendChild(bubble);
  chatBox.appendChild(row);

  // 항상 맨 아래로
  chatBox.scrollTop = chatBox.scrollHeight;

  return { row, bubble };
}

let sending = false;

async function send() {
  if (sending) return;

  const message = (input.value || "").trim();
  if (!message) return;

  sending = true;
  btn.disabled = true;
  input.disabled = true;

  append("user", message);
  input.value = "";

  // 로딩 표시(나중에 bubble만 바꿀거라 참조 저장)
  const { bubble: loadingBubble } = append("assistant", "생성 중...");

  try {
    const res = await fetch("/api/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      loadingBubble.textContent = data.error || `에러 (${res.status})`;
      return;
    }

    loadingBubble.textContent = data.reply ?? "";

    if (data.conversation_id) {
      window.CONVERSATION_ID = data.conversation_id;
      conversationId = data.conversation_id;
    }
  } catch (e) {
    loadingBubble.textContent = "서버 연결 실패";
  } finally {
    sending = false;
    btn.disabled = false;
    input.disabled = false;
    input.focus();
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

btn?.addEventListener("click", (e) => {
  e.preventDefault();
  send();
});

input?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});
