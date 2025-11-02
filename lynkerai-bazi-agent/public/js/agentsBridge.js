const socket = io();

const baziInput = document.getElementById("bazi-upload-input");
const baziTextarea = document.getElementById("bazi-textarea");
const resultBox = document.getElementById("bazi-result-box");
const childBox = document.getElementById("child-ai-box");

if (baziInput) {
  baziInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const base64 = await fileToBase64(file);
    socket.emit("bazi_upload", { image_base64: base64, source: "bazi-upload" });
    addChildMsg("📤 已上传八字命盘图片，正在识别...");
  });
}

if (baziTextarea) {
  const btn = document.getElementById("bazi-text-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      const text = baziTextarea.value.trim();
      if (!text) return;
      socket.emit("bazi_upload", { raw_text: text, source: "bazi-text" });
      addChildMsg("📝 已收到文本命盘，开始识别...");
    });
  }
}

socket.on("childAI_msg", (msg) => {
  addChildMsg(msg);
});

socket.on("bazi_result", (payload) => {
  if (resultBox) {
    resultBox.textContent = JSON.stringify(payload.data, null, 2);
  }
});

socket.on("bazi_error", (err) => {
  addChildMsg("❌ 识别失败：" + err);
});

function addChildMsg(text) {
  if (!childBox) return;
  const div = document.createElement("div");
  div.className = "chat-msg";
  div.textContent = text;
  childBox.appendChild(div);
  childBox.scrollTop = childBox.scrollHeight;
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => {
      const base64 = r.result.split(",")[1];
      resolve(base64);
    };
    r.onerror = reject;
    r.readAsDataURL(file);
  });
}
