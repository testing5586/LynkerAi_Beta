import express from "express";
import cors from "cors";
import { createServer } from "http";
import { Server } from "socket.io";
import dotenv from "dotenv";

import { SupervisorAgent } from "./agents/supervisorAgent.js";

dotenv.config();

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*"
  }
});

const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json({ limit: "20mb" }));
app.use(express.static("public"));

app.get("/health", (req, res) => {
  res.json({ ok: true, ts: Date.now() });
});

io.on("connection", (socket) => {
  console.log("✅ client connected:", socket.id);

  socket.on("analyze:bazi", async (payload) => {
    try {
      console.log("📥 Received analyze:bazi request");
      const result = await SupervisorAgent(payload, socket);
      socket.emit("agent:result", { success: true, result });
    } catch (err) {
      console.error("❌ supervisor error:", err);
      socket.emit("agent:error", { message: err.message || "unknown error" });
    }
  });

  socket.on("disconnect", () => {
    console.log("❌ client disconnected:", socket.id);
  });
});

httpServer.listen(PORT, () => {
  console.log(`🚀 LynkerAI Bazi Agent server running at http://localhost:${PORT}`);
});
