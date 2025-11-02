import { VisionAgent } from "./visionAgent.js";
import { NormalizerAgent } from "./normalizerAgent.js";
import { FormatterAgent } from "./formatterAgent.js";

export async function SupervisorAgent(input, socket) {
  socket?.emit("childAI_msg", "🧠 已收到上传数据，开始进入 Agent Workflow ...");

  socket?.emit("childAI_msg", "📸 第1层：尝试调用 MiniMax Vision Pro ...");
  const layer1 = await VisionAgent(input, socket);
  socket?.emit("childAI_msg", "✅ 第1层完成，已拿到原始八字表格 / 文本。");

  socket?.emit("childAI_msg", "🔧 第2层：开始标准化四柱、藏干、神煞 ...");
  const layer2 = await NormalizerAgent(layer1, socket);
  socket?.emit("childAI_msg", "✅ 第2层完成，已生成 normalized_bazi。");

  socket?.emit("childAI_msg", "📦 第3层：封装输出 ...");
  const final = await FormatterAgent(layer1, layer2, socket);
  socket?.emit("childAI_msg", "🎉 全部完成，可以在下方查看识别结果。");

  return final;
}
