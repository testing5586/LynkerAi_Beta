import { VisionAgent } from "./visionAgent.js";
import { NormalizerAgent } from "./normalizerAgent.js";
import { FormatterAgent } from "./formatterAgent.js";

export async function SupervisorAgent(input, socket) {
  socket?.emit("agent:progress", { agent: "supervisor", message: "已收到上传数据，开始进入 Agent Workflow", step: 1, total: 4 });

  socket?.emit("agent:progress", { agent: "vision", message: "尝试调用 MiniMax Vision Pro", step: 2, total: 4 });
  const layer1 = await VisionAgent(input, socket);
  socket?.emit("agent:progress", { agent: "vision", message: "第1层完成，已拿到原始八字表格 / 文本", step: 2, total: 4 });

  socket?.emit("agent:progress", { agent: "normalizer", message: "开始标准化四柱、藏干、神煞", step: 3, total: 4 });
  const layer2 = await NormalizerAgent(layer1, socket);
  socket?.emit("agent:progress", { agent: "normalizer", message: "第2层完成，已生成 normalized_bazi", step: 3, total: 4 });

  socket?.emit("agent:progress", { agent: "formatter", message: "封装输出", step: 4, total: 4 });
  const final = await FormatterAgent(layer1, layer2, socket);
  socket?.emit("agent:progress", { agent: "formatter", message: "全部完成，可以在下方查看识别结果", step: 4, total: 4 });

  return final;
}
