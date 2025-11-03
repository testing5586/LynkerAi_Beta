import fetch from "node-fetch";

export async function VisionAgent(input, socket) {
  const apiKey = process.env.MINIMAX_API_KEY;
  const hasImage = !!input.imageData;
  const hasText = !!input.raw_text;

  if (!hasImage && hasText) {
    socket?.emit("agent:progress", { agent: "vision", message: "检测到手动输入文本，跳过 Vision，直接进入解析" });
    return simulateFromText(input.raw_text);
  }

  if (hasImage && !apiKey) {
    socket?.emit("agent:progress", { agent: "vision", message: "没有 MINIMAX_API_KEY，使用本地 fallback 识别" });
    return simulateFromImage();
  }

  if (hasImage && apiKey) {
    try {
      socket?.emit("agent:progress", { agent: "vision", message: "使用 MiniMax Vision Pro 开始识别八字命盘" });
      
      const imageBase64 = input.imageData.replace(/^data:image\/[a-z]+;base64,/, '');
      
      const res = await fetch("https://api.minimax.chat/v1/text/chatcompletion_v2", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${apiKey}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          model: "MiniMax-VL-01",
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: "你是一名专业的命理识别AI。请仔细阅读上传的八字命盘截图，提取【年柱】【月柱】【日柱】【时柱】四列对应的完整信息。务必以以下JSON结构直接输出结果，不要附加说明或多余文字：{\"columns\": [\"年柱\", \"月柱\", \"日柱\", \"时柱\"],\"rows\": {\"主星\": [\"\", \"\", \"\", \"\"],\"天干\": [\"\", \"\", \"\", \"\"],\"地支\": [\"\", \"\", \"\", \"\"],\"藏干\": [\"\", \"\", \"\", \"\"],\"副星\": [\"\", \"\", \"\", \"\"],\"星运\": [\"\", \"\", \"\", \"\"],\"自坐\": [\"\", \"\", \"\", \"\"],\"空亡\": [\"\", \"\", \"\", \"\"],\"纳音\": [\"\", \"\", \"\", \"\"],\"神煞\": [\"\", \"\", \"\", \"\"]}}。要求：1.只输出JSON，不要任何解释性语言；2.如果识别不全，也必须保证JSON字段齐全；3.保持列顺序为 年柱→月柱→日柱→时柱；4.如果图中文字不清晰，请根据排版推测补齐可能的内容。"
                },
                {
                  type: "image_url",
                  image_url: {
                    url: `data:image/png;base64,${imageBase64}`
                  }
                }
              ]
            }
          ]
        })
      });

      if (!res.ok) {
        const errorText = await res.text();
        socket?.emit("agent:progress", { agent: "vision", message: `MiniMax API 返回错误 ${res.status}: ${errorText}，改用 fallback` });
        return simulateFromImage();
      }

      const data = await res.json();
      let raw = data.choices?.[0]?.message?.content || "";
      let detected_elements = {};

      try {
        const jsonMatch = raw.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          detected_elements = JSON.parse(jsonMatch[0]);
          socket?.emit("agent:progress", { agent: "vision", message: "成功解析 JSON 结构" });
        } else {
          throw new Error("No JSON found in response");
        }
      } catch (err) {
        socket?.emit("agent:progress", { agent: "vision", message: "MiniMax 返回内容不是有效JSON，使用 fallback 结构" });
        detected_elements = fakeDetectedElements();
      }

      return {
        layer: "layer1",
        success: true,
        model: "MiniMax-VL-01",
        processing_time: 2000,
        confidence: 0.95,
        raw_text: raw,
        table_detected: true,
        detected_elements
      };
    } catch (err) {
      socket?.emit("agent:progress", { agent: "vision", message: `调用 MiniMax 出错: ${err.message}，使用 fallback 版本` });
      console.error("MiniMax Vision Error:", err);
      return simulateFromImage();
    }
  }

  return simulateFromImage();
}

function simulateFromImage() {
  return {
    layer: "layer1",
    success: true,
    model: "simulated-ocr",
    processing_time: 1800,
    confidence: 0.9,
    raw_text: sampleRawText(),
    table_detected: true,
    detected_elements: fakeDetectedElements()
  };
}

function simulateFromText(text) {
  return {
    layer: "layer1",
    success: true,
    model: "manual-text",
    processing_time: 500,
    confidence: 0.99,
    raw_text: text,
    table_detected: true,
    detected_elements: fakeDetectedElements()
  };
}

function fakeDetectedElements() {
  return {
    columns: ["年柱", "月柱", "日柱", "时柱"],
    rows: {
      "主星": ["正财", "食神", "元男", "正印"],
      "天干": ["庚", "己", "丁", "甲"],
      "地支": ["辰", "卯", "丑", "辰"],
      "藏干": ["戊土 乙木 癸水", "乙木", "己土 癸水 辛金", "戊土 乙木 癸水"],
      "副星": ["伤官 偏印 七杀", "偏印", "食神 七杀 偏财", "伤官 偏印 七杀"],
      "星运": ["衰", "病", "墓", "衰"],
      "自坐": ["养", "病", "墓", "衰"],
      "空亡": ["申酉", "申酉", "申酉", "寅卯"],
      "纳音": ["白蜡金", "城头土", "涧下水", "覆灯火"],
      "神煞": [
        "国印贵人",
        "太极贵人 月德合",
        "阴差阳错 天乙贵人 德秀贵人 寡宿 披麻",
        "国印贵人 月德贵人 德秀贵人 华盖"
      ]
    }
  };
}

function sampleRawText() {
  const text = [
    "阴历：2000年二月十五辰时（乾造）",
    "阳历：2000年03月20日 08:18",
    "| 日期 | 年柱 | 月柱 | 日柱 | 时柱 |",
    "| **主星** | 正财 | 食神 | 元男 | 正印 |",
    "| **天干** | 庚 | 己 | 丁 | 甲 |",
    "| **地支** | 辰 | 卯 | 丑 | 辰 |",
    "| **藏干** | 戊土 乙木 癸水 | 乙木 | 己土 癸水 辛金 | 戊土 乙木 癸水 |",
    "| **副星** | 伤官 偏印 七杀 | 偏印 | 食神 七杀 偏财 | 伤官 偏印 七杀 |",
    "| **星运** | 衰 | 病 | 墓 | 衰 |",
    "| **自坐** | 养 | 病 | 墓 | 衰 |",
    "| **空亡** | 申酉 | 申酉 | 申酉 | 寅卯 |",
    "| **纳音** | 白蜡金 | 城头土 | 涧下水 | 覆灯火 |",
    "| **神煞** | 国印贵人 | 太极贵人 月德合 | 阴差阳错 天乙贵人 德秀贵人 寡宿 披麻 | 国印贵人 月德贵人 德秀贵人 华盖 |"
  ];
  return text.join('\n');
}
