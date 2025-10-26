/**
 * 真命盘验证中心 - 前端逻辑
 * 1个 AI 对话框 + 2个上传框 + 2个只读结果展示区
 * 支持3组命盘数据切换
 */

// 全局状态管理
const state = {
    userId: null,
    currentGroupIndex: 0, // 当前显示的组：0/1/2
    chartGroups: [
        // 组1 - 可能出生的时辰1
        {
            baziText: "",
            ziweiText: "",
            baziResult: null,
            ziweiResult: null,
            baziUploaded: false,
            ziweiUploaded: false
        },
        // 组2 - 可能出生的时辰2
        {
            baziText: "",
            ziweiText: "",
            baziResult: null,
            ziweiResult: null,
            baziUploaded: false,
            ziweiUploaded: false
        },
        // 组3 - 可能出生的时辰3
        {
            baziText: "",
            ziweiText: "",
            baziResult: null,
            ziweiResult: null,
            baziUploaded: false,
            ziweiUploaded: false
        }
    ],
    conversationState: 'waiting_bazi' // waiting_bazi | waiting_ziwei | ready_to_save | saved
};

// 获取当前组的数据
function getCurrentGroup() {
    return state.chartGroups[state.currentGroupIndex];
}

// ========== 初始化 ==========
document.addEventListener("DOMContentLoaded", () => {
    // 获取 user_id
    state.userId = document.querySelector("body").dataset.userId;
    
    if (!state.userId) {
        console.error("❌ 未找到 user_id");
        return;
    }
    
    initSidebar();
    initGroupSwitcher(); // 初始化组切换功能
    initDragDrop();
    initFileInputs();
    initTextInputs();
    initChatbox();
    
    // 加载初始数据（组1）
    renderCurrentGroup();
    
    console.log("✅ 真命盘验证中心已初始化，user_id:", state.userId);
});

// ========== 侧边栏展开/收起 ==========
function initSidebar() {
    document.querySelectorAll('.nav-item.expandable').forEach(item => {
        item.addEventListener('click', () => {
            const menuName = item.dataset.menu;
            const submenu = document.querySelector(`.nav-submenu[data-parent="${menuName}"]`);
            
            if (submenu) {
                const isHidden = submenu.classList.contains('hidden');
                submenu.classList.toggle('hidden');
                item.classList.toggle('expanded', isHidden);
            }
        });
    });
}

// ========== 组切换功能 ==========
function initGroupSwitcher() {
    document.querySelectorAll('.group-switch').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const groupIndex = parseInt(item.dataset.groupIndex);
            switchGroup(groupIndex);
        });
    });
}

// 切换到指定组
function switchGroup(groupIndex) {
    if (groupIndex < 0 || groupIndex > 2) return;
    
    // 保存当前组的数据到state
    saveCurrentGroupState();
    
    // 更新当前组索引
    state.currentGroupIndex = groupIndex;
    
    // 更新菜单高亮
    document.querySelectorAll('.group-switch').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`.group-switch[data-group-index="${groupIndex}"]`).classList.add('active');
    
    // 渲染新组的数据
    renderCurrentGroup();
    
    console.log(`✅ 已切换到组 ${groupIndex + 1}`);
}

// 保存当前组的UI状态到state
function saveCurrentGroupState() {
    const currentGroup = getCurrentGroup();
    const baziText = document.getElementById('baziText');
    const ziweiText = document.getElementById('ziweiText');
    
    if (baziText) currentGroup.baziText = baziText.value;
    if (ziweiText) currentGroup.ziweiText = ziweiText.value;
}

// 渲染当前组的数据到UI
function renderCurrentGroup() {
    const currentGroup = getCurrentGroup();
    const groupIndex = state.currentGroupIndex;
    
    // 更新时辰标题
    const shichenTitle = document.querySelector('.shichen-title h2');
    if (shichenTitle) {
        shichenTitle.textContent = `可能出生的时辰${groupIndex + 1}`;
    }
    
    // 恢复文本输入框内容
    const baziText = document.getElementById('baziText');
    const ziweiText = document.getElementById('ziweiText');
    if (baziText) baziText.value = currentGroup.baziText || '';
    if (ziweiText) ziweiText.value = currentGroup.ziweiText || '';
    
    // 恢复结果展示区
    renderResult('bazi', currentGroup.baziResult, currentGroup.baziUploaded);
    renderResult('ziwei', currentGroup.ziweiResult, currentGroup.ziweiUploaded);
}

// 渲染单个结果框
function renderResult(type, result, uploaded) {
    const resultBox = document.getElementById(`${type}Result`);
    const statusElem = document.getElementById(`${type}Status`);
    const contentElem = document.getElementById(`${type}ResultContent`);
    
    if (!resultBox || !statusElem || !contentElem) return;
    
    if (result) {
        // 显示验证结果
        statusElem.textContent = '验证完成';
        statusElem.className = 'result-status completed';
        contentElem.innerHTML = formatResultContent(result);
    } else if (uploaded) {
        // 已上传但未验证
        statusElem.textContent = '已上传';
        statusElem.className = 'result-status processing';
        contentElem.innerHTML = '<p class="empty-state">等待验证...</p>';
    } else {
        // 未上传
        statusElem.textContent = '等待上传...';
        statusElem.className = 'result-status';
        const typeName = type === 'bazi' ? '八字' : '紫微';
        contentElem.innerHTML = `<p class="empty-state">上传${typeName}命盘后，验证结果将显示在这里</p>`;
    }
}

// 格式化结果内容（复用现有逻辑）
function formatResultContent(result) {
    if (!result) return '<p class="empty-state">暂无数据</p>';
    
    let html = '';
    if (result.score !== undefined) {
        html += `<div class="score-display">评分: ${result.score}</div>`;
    }
    if (result.parsed) {
        html += `<pre>${JSON.stringify(result.parsed, null, 2)}</pre>`;
    }
    if (result.message) {
        html += `<p>${result.message}</p>`;
    }
    return html || '<p class="empty-state">暂无数据</p>';
}

// ========== Drag & Drop 上传 ==========
function initDragDrop() {
    const baziDropzone = document.getElementById('baziDropzone');
    const ziweiDropzone = document.getElementById('ziweiDropzone');
    
    setupDropzone(baziDropzone, 'bazi');
    setupDropzone(ziweiDropzone, 'ziwei');
}

function setupDropzone(dropzone, type) {
    // 阻止默认行为
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });
    
    // 拖拽时高亮
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.remove('dragover');
        }, false);
    });
    
    // 处理拖拽文件
    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0], type);
        }
    }, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// ========== 文件输入处理 ==========
function initFileInputs() {
    const baziFile = document.getElementById('baziFile');
    const ziweiFile = document.getElementById('ziweiFile');
    
    baziFile.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            handleFileUpload(e.target.files[0], 'bazi');
        }
    });
    
    ziweiFile.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            handleFileUpload(e.target.files[0], 'ziwei');
        }
    });
}

async function handleFileUpload(file, type) {
    const textarea = document.getElementById(`${type}Text`);
    const statusSpan = document.getElementById(`${type}Status`);
    
    statusSpan.textContent = "读取文件中...";
    statusSpan.className = "result-status processing";
    
    try {
        if (file.type.startsWith('image/')) {
            // 图片文件 - 暂时提示用户
            addAIMessage(`检测到图片文件 "${file.name}"，OCR 功能暂未启用。请先使用其他工具提取文本后再粘贴到输入框。`);
            statusSpan.textContent = "等待文本输入...";
            statusSpan.className = "result-status";
        } else {
            // 文本文件
            const text = await file.text();
            textarea.value = text;
            statusSpan.textContent = "文件已加载";
            statusSpan.className = "result-status success";
            
            // 自动触发验证
            await processChartText(text, type);
        }
    } catch (error) {
        console.error("文件读取失败:", error);
        addAIMessage(`抱歉，读取文件 "${file.name}" 时出错了。请检查文件格式后重试。`);
        statusSpan.textContent = "读取失败";
        statusSpan.className = "result-status error";
    }
}

// ========== 文本输入处理 ==========
function initTextInputs() {
    const baziText = document.getElementById('baziText');
    const ziweiText = document.getElementById('ziweiText');
    
    // 失焦时自动验证
    baziText.addEventListener('blur', async () => {
        const text = baziText.value.trim();
        const currentGroup = getCurrentGroup();
        if (text && !currentGroup.baziUploaded) {
            await processChartText(text, 'bazi');
        }
    });
    
    ziweiText.addEventListener('blur', async () => {
        const text = ziweiText.value.trim();
        const currentGroup = getCurrentGroup();
        if (text && !currentGroup.ziweiUploaded) {
            await processChartText(text, 'ziwei');
        }
    });
    
    // 粘贴时提示
    [baziText, ziweiText].forEach(textarea => {
        textarea.addEventListener('paste', () => {
            addAIMessage("检测到粘贴内容，请确保完整后点击输入框外部，我会自动为你验证。");
        });
    });
}

// ========== 处理命盘文本 ==========
async function processChartText(text, type) {
    if (!text.trim()) return;
    
    const statusSpan = document.getElementById(`${type}Status`);
    const resultContent = document.getElementById(`${type}ResultContent`);
    
    statusSpan.textContent = "验证中...";
    statusSpan.className = "result-status processing";
    
    try {
        const response = await fetch('/verify/api/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                raw_text: text,
                wizard: {},
                notes: "",
                manual: {}
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            // 更新当前组的状态
            const currentGroup = getCurrentGroup();
            if (type === 'bazi') {
                currentGroup.baziUploaded = true;
                currentGroup.baziResult = data;
                currentGroup.baziText = text;
                state.conversationState = 'waiting_ziwei';
            } else {
                currentGroup.ziweiUploaded = true;
                currentGroup.ziweiResult = data;
                currentGroup.ziweiText = text;
                state.conversationState = 'ready_to_save';
            }
            
            // 显示结果
            displayResult(data, type);
            statusSpan.textContent = "验证完成";
            statusSpan.className = "result-status success";
            
            // AI 引导
            updateAIGuidance();
        } else {
            throw new Error(data.toast || "验证失败");
        }
    } catch (error) {
        console.error("验证失败:", error);
        statusSpan.textContent = "验证失败";
        statusSpan.className = "result-status error";
        resultContent.innerHTML = `<p class="empty-state" style="color: #721c24;">验证失败：${error.message}</p>`;
        addAIMessage(`抱歉，${type === 'bazi' ? '八字' : '紫微'}命盘验证失败了。错误信息：${error.message}`);
    }
}

// ========== 显示验证结果 ==========
function displayResult(data, type) {
    const resultContent = document.getElementById(`${type}ResultContent`);
    
    const html = `
        <div class="score-display">匹配评分：${(data.score * 100).toFixed(1)}%</div>
        
        <div class="detail-item">
            <span class="detail-label">姓名：</span>
            <span>${data.parsed?.name || '未识别'}</span>
        </div>
        
        <div class="detail-item">
            <span class="detail-label">性别：</span>
            <span>${data.parsed?.gender || '未识别'}</span>
        </div>
        
        <div class="detail-item">
            <span class="detail-label">出生时间：</span>
            <span>${data.parsed?.birth_time || '未识别'}</span>
        </div>
        
        ${data.parsed?.main_star ? `
        <div class="detail-item">
            <span class="detail-label">主星：</span>
            <span>${data.parsed.main_star}</span>
        </div>
        ` : ''}
        
        <details style="margin-top: 16px;">
            <summary style="cursor: pointer; font-weight: 600;">查看完整 JSON</summary>
            <pre style="margin-top: 8px;">${JSON.stringify(data.parsed, null, 2)}</pre>
        </details>
    `;
    
    resultContent.innerHTML = html;
}

// ========== AI 引导对话 ==========
function updateAIGuidance() {
    if (state.conversationState === 'waiting_ziwei') {
        addAIMessage("很好！八字命盘已经验证完成。接下来，请上传你的<strong>紫微斗数命盘</strong>。");
    } else if (state.conversationState === 'ready_to_save') {
        addAIMessage("太棒了！两份命盘都已验证完成。请确认以上信息无误后，在聊天框中输入 <strong>\"确认保存\"</strong>，我会帮你保存到数据库。");
    }
}

// ========== 聊天框逻辑 ==========
function initChatbox() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSendBtn');
    
    sendBtn.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // 显示用户消息
    addUserMessage(message);
    chatInput.value = '';
    
    // 处理用户输入
    if (message.includes('确认保存') || message.includes('保存')) {
        if (state.conversationState === 'ready_to_save') {
            await saveToDatabase();
        } else if (!state.baziUploaded) {
            addAIMessage("抱歉，你还没有上传八字命盘呢。请先上传左侧的八字命盘。");
        } else if (!state.ziweiUploaded) {
            addAIMessage("抱歉，你还没有上传紫微斗数命盘呢。请先上传右侧的紫微命盘。");
        } else {
            addAIMessage("系统状态异常，请刷新页面重试。");
        }
    } else if (message.includes('帮助') || message.includes('怎么') || message.includes('如何')) {
        addAIMessage(`
            <p>我来帮你！使用步骤如下：</p>
            <p>1️⃣ <strong>上传八字命盘</strong>：拖拽图片或粘贴文本到左侧上传框</p>
            <p>2️⃣ <strong>上传紫微命盘</strong>：拖拽图片或粘贴文本到右侧上传框</p>
            <p>3️⃣ <strong>确认保存</strong>：两份命盘都验证完成后，输入"确认保存"</p>
        `);
    } else {
        // 简单的回复
        addAIMessage("我收到你的消息了。如果需要帮助，请输入\"帮助\"。如果已经上传两份命盘，请输入\"确认保存\"。");
    }
}

function addUserMessage(text) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageEl = document.createElement('div');
    messageEl.className = 'message user-message';
    messageEl.innerHTML = `
        <div class="message-avatar">👤</div>
        <div class="message-content">
            <p>${text}</p>
        </div>
    `;
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addAIMessage(html) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageEl = document.createElement('div');
    messageEl.className = 'message ai-message';
    messageEl.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            ${html}
        </div>
    `;
    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ========== 保存到数据库 ==========
async function saveToDatabase() {
    if (!state.baziResult || !state.ziweiResult) {
        addAIMessage("抱歉，需要两份命盘都验证完成后才能保存。");
        return;
    }
    
    addAIMessage("正在保存你的真命盘验证记录...");
    
    try {
        // 合并两份命盘的数据
        const combinedText = `【八字命盘】\n${document.getElementById('baziText').value}\n\n【紫微斗数命盘】\n${document.getElementById('ziweiText').value}`;
        
        const response = await fetch('/verify/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.userId,
                raw_text: combinedText,
                wizard: {},
                notes: `八字评分: ${(state.baziResult.score * 100).toFixed(1)}%, 紫微评分: ${(state.ziweiResult.score * 100).toFixed(1)}%`,
                manual: {
                    name: state.baziResult.parsed?.name || state.ziweiResult.parsed?.name,
                    gender: state.baziResult.parsed?.gender || state.ziweiResult.parsed?.gender
                }
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            state.conversationState = 'saved';
            addAIMessage(`
                <p>✅ <strong>保存成功！</strong></p>
                <p>记录ID：${data.record_id}</p>
                <p>综合评分：${(data.score * 100).toFixed(1)}%</p>
                <p>你可以随时回到这个页面查看你的真命盘记录。</p>
            `);
        } else {
            throw new Error(data.toast || "保存失败");
        }
    } catch (error) {
        console.error("保存失败:", error);
        addAIMessage(`抱歉，保存时出错了：${error.message}。请稍后重试。`);
    }
}
