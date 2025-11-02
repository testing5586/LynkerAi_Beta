export async function NormalizerAgent(layer1, socket) {
  const detected = layer1.detected_elements || { columns: [], rows: {} };
  const rows = detected.rows || {};

  const meta = extractMeta(layer1.raw_text || "");

  const pillars = {};
  const colMap = ["year", "month", "day", "hour"];

  for (let i = 0; i < 4; i++) {
    const key = colMap[i];
    pillars[key] = {
      stem: rows["天干"]?.[i] || "",
      branch: rows["地支"]?.[i] || "",
      hidden_stems: rows["藏干"]?.[i] ? rows["藏干"][i].split(/\s+/).filter(Boolean) : [],
      main_star: rows["主星"]?.[i] || "",
      sub_star: rows["副星"]?.[i] ? rows["副星"][i].split(/\s+/).filter(Boolean) : [],
      fortune_phase: rows["星运"]?.[i] || "",
      self_seat: rows["自坐"]?.[i] || "",
      void: rows["空亡"]?.[i] || "",
      nayin: rows["纳音"]?.[i] || "",
      shen_sha: rows["神煞"]?.[i]
        ? (Array.isArray(rows["神煞"]) ? rows["神煞"][i] : rows["神煞"][i]).toString().split(/\s+/).filter(Boolean)
        : []
    };
  }

  const element_balance = calcFiveElements(pillars);

  return {
    layer: "layer2",
    success: true,
    version: "LynkerAI-L2-2025.11",
    normalized_bazi: {
      meta,
      pillars,
      element_balance
    }
  };
}

function extractMeta(text) {
  return {
    calendar_solar: text.match(/阳历[:：]\s*([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}[日号]?(?:\s*[0-9]{1,2}:[0-9]{2})?)/)?.[1] || null,
    calendar_lunar: text.match(/阴历[:：]\s*([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}[日号]?)/)?.[1] || null,
    gender: text.includes("乾造") ? "乾造" : text.includes("坤造") ? "坤造" : null,
    source: "minimax-vision-pro"
  };
}

const ELEMENT_MAP = {
  "木": ["甲", "乙", "寅", "卯"],
  "火": ["丙", "丁", "巳", "午"],
  "土": ["戊", "己", "辰", "戌", "丑", "未"],
  "金": ["庚", "辛", "申", "酉"],
  "水": ["壬", "癸", "亥", "子"]
};

function charToElementKey(ch) {
  for (const [e, arr] of Object.entries(ELEMENT_MAP)) {
    if (arr.includes(ch)) {
      return { "木": "wood", "火": "fire", "土": "earth", "金": "metal", "水": "water" }[e];
    }
  }
  return null;
}

function calcFiveElements(pillars) {
  const count = { wood: 0, fire: 0, earth: 0, metal: 0, water: 0 };

  Object.values(pillars).forEach((p) => {
    if (p.stem) {
      const e = charToElementKey(p.stem[0]);
      if (e) count[e]++;
    }
    if (p.branch) {
      const e = charToElementKey(p.branch[0]);
      if (e) count[e]++;
    }
    (p.hidden_stems || []).forEach((hs) => {
      const e = charToElementKey(hs[0]);
      if (e) count[e]++;
    });
  });

  let maxKey = "wood", minKey = "wood";
  Object.entries(count).forEach(([k, v]) => {
    if (v > count[maxKey]) maxKey = k;
    if (v < count[minKey]) minKey = k;
  });

  return {
    ...count,
    dominant: keyToZh(maxKey),
    weakened: keyToZh(minKey),
    favorable_elements: ["wood", "fire", "earth", "metal", "water"]
      .filter((k) => count[k] === count[minKey])
      .map(keyToZh),
    unfavorable_elements: [keyToZh(maxKey)]
  };
}

function keyToZh(k) {
  return { wood: "木", fire: "火", earth: "土", metal: "金", water: "水" }[k] || k;
}
