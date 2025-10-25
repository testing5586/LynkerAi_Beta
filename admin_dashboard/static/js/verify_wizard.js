/**
 * 真命盘验证中心 - 前端逻辑
 * Wizard 7步问答 + 命盘导入 + 手动字段锁定
 */

// 状态管理
const state = {
    currentStep: 1,
    totalSteps: 7,
    wizard: {},
    notes: "",
    manual: {
        name: "",
        gender: "",
        name_locked: true
    },
    rawText: {
        bazi: "",
        ziwei: ""
    },
    currentTab: "bazi",
    userId: null
};

// 初始化
document.addEventListener("DOMContentLoaded", () => {
    // 从URL或DOM获取user_id
    const urlParams = new URLSearchParams(window.location.search);
    state.userId = urlParams.get("user_id") || document.querySelector("body").dataset.userId;
    
    initWizardNav();
    initTabSwitch();
    initFileUpload();
    initPasteButtons();
    initManualFields();
    initPreviewButton();
    initSaveButton();
    initOCRButton();
});

// === Wizard 导航 ===
function initWizardNav() {
    const btnPrev = document.getElementById("btnPrev");
    const btnNext = document.getElementById("btnNext");
    
    btnPrev.addEventListener("click", () => {
        if (state.currentStep > 1) {
            saveCurrentStep();
            state.currentStep--;
            updateWizardUI();
        }
    });
    
    btnNext.addEventListener("click", () => {
        if (state.currentStep < state.totalSteps) {
            saveCurrentStep();
            state.currentStep++;
            updateWizardUI();
        }
    });
    
    updateWizardUI();
}

function saveCurrentStep() {
    const stepMap = {
        1: "family",
        2: "education",
        3: "career",
        4: "marriage",
        5: "finance",
        6: "health",
        7: "major_events"
    };
    
    const fieldId = `wizard_${stepMap[state.currentStep]}`;
    const value = document.getElementById(fieldId).value.trim();
    state.wizard[stepMap[state.currentStep]] = value;
}

function updateWizardUI() {
    // 更新步骤显示
    document.querySelectorAll(".wizard-step").forEach((el, idx) => {
        el.classList.toggle("active", idx + 1 === state.currentStep);
    });
    
    // 更新进度条
    const progress = (state.currentStep / state.totalSteps) * 100;
    document.getElementById("progressFill").style.width = `${progress}%`;
    document.getElementById("progressText").textContent = `步骤 ${state.currentStep}/${state.totalSteps}`;
    
    // 更新按钮状态
    document.getElementById("btnPrev").disabled = state.currentStep === 1;
    document.getElementById("btnNext").textContent = state.currentStep === state.totalSteps ? "完成问答" : "下一步";
}

// === Tab 切换 ===
function initTabSwitch() {
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const tab = btn.dataset.tab;
            state.currentTab = tab;
            
            // 更新 Tab 按钮
            document.querySelectorAll(".tab-btn").forEach(b => {
                b.classList.toggle("active", b.dataset.tab === tab);
            });
            
            // 更新 Tab 内容
            document.querySelectorAll(".tab-content").forEach(content => {
                content.classList.toggle("active", content.id === `tab_${tab}`);
            });
        });
    });
}

// === 文件上传 ===
function initFileUpload() {
    const fileBazi = document.getElementById("file_bazi");
    const fileZiwei = document.getElementById("file_ziwei");
    
    fileBazi.addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (file) {
            const text = await file.text();
            document.getElementById("raw_bazi").value = text;
            state.rawText.bazi = text;
            showToast(`✅ 已加载文件：${file.name}`);
        }
    });
    
    fileZiwei.addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (file) {
            const text = await file.text();
            document.getElementById("raw_ziwei").value = text;
            state.rawText.ziwei = text;
            showToast(`✅ 已加载文件：${file.name}`);
        }
    });
}

// === 粘贴按钮 ===
function initPasteButtons() {
    document.getElementById("btnPasteBazi").addEventListener("click", async () => {
        try {
            const text = await navigator.clipboard.readText();
            document.getElementById("raw_bazi").value = text;
            state.rawText.bazi = text;
            showToast("✅ 已从剪贴板粘贴八字文本");
        } catch (e) {
            showToast("❌ 无法读取剪贴板，请使用 Ctrl+V 粘贴");
        }
    });
    
    document.getElementById("btnPasteZiwei").addEventListener("click", async () => {
        try {
            const text = await navigator.clipboard.readText();
            document.getElementById("raw_ziwei").value = text;
            state.rawText.ziwei = text;
            showToast("✅ 已从剪贴板粘贴紫微文本");
        } catch (e) {
            showToast("❌ 无法读取剪贴板，请使用 Ctrl+V 粘贴");
        }
    });
}

// === 手动字段 ===
function initManualFields() {
    const inputName = document.getElementById("manual_name");
    const inputGender = document.getElementById("manual_gender");
    const lockCheckbox = document.getElementById("name_locked");
    
    inputName.addEventListener("input", (e) => {
        state.manual.name = e.target.value.trim();
    });
    
    inputGender.addEventListener("change", (e) => {
        state.manual.gender = e.target.value;
    });
    
    lockCheckbox.addEventListener("change", (e) => {
        state.manual.name_locked = e.target.checked;
    });
}

// === 预览按钮 ===
function initPreviewButton() {
    document.getElementById("btnPreview").addEventListener("click", async () => {
        saveCurrentStep();
        
        // 获取当前 Tab 的命盘文本
        const rawText = state.currentTab === "bazi" 
            ? document.getElementById("raw_bazi").value.trim()
            : document.getElementById("raw_ziwei").value.trim();
        
        if (!rawText) {
            showToast("❌ 请先输入或上传命盘文本");
            return;
        }
        
        // 收集手写补充
        state.notes = document.getElementById("notes").value.trim();
        
        showToast("⏳ 正在识别和评分...");
        
        try {
            const response = await fetch("/verify/api/preview", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    wizard: state.wizard,
                    notes: state.notes,
                    raw_text: rawText,
                    manual: state.manual
                })
            });
            
            const result = await response.json();
            
            if (!result.ok) {
                showToast(result.toast || "❌ 预览失败");
                return;
            }
            
            // 更新预览JSON
            document.getElementById("previewJSON").textContent = JSON.stringify({
                parsed: result.parsed,
                score: result.score,
                signals: result.signals,
                candidates: result.candidates
            }, null, 2);
            
            // 渲染候选命盘
            renderCandidates(result.candidates);
            
            showToast(result.toast || `✅ 识别成功！评分：${result.score.toFixed(2)}`);
        } catch (e) {
            showToast(`❌ 网络错误：${e.message}`);
        }
    });
}

// === 保存按钮 ===
function initSaveButton() {
    document.getElementById("btnSave").addEventListener("click", async () => {
        if (!state.userId) {
            showToast("❌ 请先登录后再保存");
            return;
        }
        
        saveCurrentStep();
        
        // 获取当前 Tab 的命盘文本
        const rawText = state.currentTab === "bazi" 
            ? document.getElementById("raw_bazi").value.trim()
            : document.getElementById("raw_ziwei").value.trim();
        
        if (!rawText) {
            showToast("❌ 请先输入或上传命盘文本");
            return;
        }
        
        if (!confirm("确认保存为你的真命盘吗？")) {
            return;
        }
        
        showToast("⏳ 正在保存...");
        
        try {
            const response = await fetch("/verify/api/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: state.userId,
                    wizard: state.wizard,
                    notes: document.getElementById("notes").value.trim(),
                    raw_text: rawText,
                    manual: state.manual
                })
            });
            
            const result = await response.json();
            
            if (!result.ok) {
                showToast(result.toast || "❌ 保存失败");
                return;
            }
            
            // 渲染候选命盘
            if (result.candidates) {
                renderCandidates(result.candidates, result.record_id);
            }
            
            showToast(result.toast || "✅ 保存成功！");
        } catch (e) {
            showToast(`❌ 网络错误：${e.message}`);
        }
    });
}

// === OCR 按钮 ===
function initOCRButton() {
    document.getElementById("btnOCR").addEventListener("click", async () => {
        showToast("⚠️ 暂不启用 OCR 识别，请优先粘贴文本或上传 TXT 文件");
    });
}

// === 复制 JSON ===
document.getElementById("btnCopyJSON").addEventListener("click", async () => {
    const json = document.getElementById("previewJSON").textContent;
    try {
        await navigator.clipboard.writeText(json);
        showToast("✅ 已复制到剪贴板");
    } catch (e) {
        showToast("❌ 复制失败，请手动复制");
    }
});

// === 渲染候选命盘 ===
function renderCandidates(candidates, recordId = null) {
    const grid = document.getElementById("candidatesGrid");
    
    if (!candidates || candidates.length === 0) {
        grid.innerHTML = '<div class="candidate-card placeholder"><p>暂无候选命盘</p></div>';
        return;
    }
    
    grid.innerHTML = candidates.map((c, idx) => `
        <div class="candidate-card">
            <h3>候选 ${idx + 1}：${c.label}</h3>
            <div class="score">${(c.score * 100).toFixed(1)}%</div>
            <div class="explain">${c.explain}</div>
            ${recordId ? `<button class="btn btn-primary" onclick="confirmCandidate(${recordId}, ${c.id})">✅ 已验证</button>` : ''}
        </div>
    `).join("");
}

// === 确认候选 ===
window.confirmCandidate = async function(recordId, chosenId) {
    try {
        const response = await fetch("/verify/api/confirm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ record_id: recordId, chosen_id: chosenId })
        });
        
        const result = await response.json();
        showToast(result.toast || (result.ok ? "✅ 确认成功" : "❌ 确认失败"));
    } catch (e) {
        showToast(`❌ 网络错误：${e.message}`);
    }
};

// === Toast 提示 ===
function showToast(message) {
    alert(message);
}
