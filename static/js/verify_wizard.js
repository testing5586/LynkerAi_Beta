/**
 * LynkerAI 真命盘验证向导 - 前端交互逻辑
 * 包含延迟点准机制的实现
 */

// 全局状态管理
const AppState = {
    userId: null,
    currentGroupIndex: 0,
    chartLocked: false,
    currentChartId: null,
    baziUploaded: false,
    ziweiUploaded: false,
    conversationHistory: [],
    lifeEvents: "",
    parsedChart: {}
};

// DOM 元素引用
const Elements = {
    chatMessages: document.getElementById('chatMessages'),
    chatInput: document.getElementById('chatInput'),
    chatSendBtn: document.getElementById('chatSendBtn'),
    baziText: document.getElementById('baziText'),
    ziweiText: document.getElementById('ziweiText'),
    baziFile: document.getElementById('baziFile'),
    ziweiFile: document.getElementById('ziweiFile'),
    baziResult: document.getElementById('baziResultContent'),
    ziweiResult: document.getElementById('ziweiResultContent'),
    baziStatus: document.getElementById('baziStatus'),
    ziweiStatus: document.getElementById('ziweiStatus')
};

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // 从 URL 获取用户 ID
    const urlParams = new URLSearchParams(window.location.search);
    AppState.userId = urlParams.get('user_id') || '1';
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 发送初始欢迎消息
    addSystemMessage("系统已就绪，请上传您的命盘开始验证。");
}

function bindEventListeners() {
    // 聊天发送按钮
    Elements.chatSendBtn.addEventListener('click', sendMessage);
    
    // 聊天输入框回车发送
    Elements.chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 文件上传监听
    Elements.baziFile.addEventListener('change', handleFileUpload('bazi'));
    Elements.ziweiFile.addEventListener('change', handleFileUpload('ziwei'));
    
    // 文本输入监听
    Elements.baziText.addEventListener('input', handleTextInput('bazi'));
    Elements.ziweiText.addEventListener('input', handleTextInput('ziwei'));
    
    // 组切换监听
    document.querySelectorAll('.group-switch').forEach(switchEl => {
        switchEl.addEventListener('click', function() {
            switchGroup(parseInt(this.dataset.groupIndex));
        });
    });
}

// 发送消息到 AI
async function sendMessage() {
    const message = Elements.chatInput.value.trim();
    if (!message) return;
    
    // 添加用户消息到界面
    addUserMessage(message);
    Elements.chatInput.value = '';
    
    // 检查是否是验证按钮点击
    if (message.startsWith('#yes-') || message.startsWith('#no-')) {
        await handleValidationClick(message);
        return;
    }
    
    // 检查是否是确认真命盘命令
    if (message.includes('确认') || message.includes('锁定')) {
        await confirmTrueChart();
        return;
    }
    
    // 发送到 AI
    await sendToAI(message);
}

// 处理验证按钮点击
async function handleValidationClick(clickData) {
    try {
        const response = await fetch('/verify/api/validation_log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: AppState.userId,
                chart_id: AppState.currentChartId,
                click_data: clickData,
                ai_statement: extractStatementFromClick(clickData),
                source_ai: 'Primary'
            })
        });
        
        const result = await response.json();
        
        if (result.ok) {
            addSystemMessage(`验证结果已记录 ${result.ai_verification ? '并完成AI验证' : ''}`);
            
            // 如果有AI验证结果，显示在右侧卡片
            if (result.ai_verification) {
                updateZiweiValidationResult(result.ai_verification);
            }
        } else {
            addSystemMessage(`记录验证结果失败：${result.toast}`);
        }
    } catch (error) {
        console.error('验证点击处理失败:', error);
        addSystemMessage('验证记录失败，请稍后重试');
    }
}

// 确认真命盘
async function confirmTrueChart() {
    if (!AppState.baziUploaded || !AppState.ziweiUploaded) {
        addSystemMessage('请先上传八字命盘和紫微命盘');
        return;
    }
    
    try {
        const response = await fetch('/verify/api/confirm_true_chart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: AppState.userId,
                chart_id: AppState.currentChartId
            })
        });
        
        const result = await response.json();
        
        if (result.ok) {
            AppState.chartLocked = true;
            addSystemMessage('真命盘已确认！现在可以对AI的断语进行验证了。');
            
            // 触发AI发送总结性问题
            await sendToAI("请总结我的命盘特征并提出验证性问题");
        } else {
            addSystemMessage(`确认真命盘失败：${result.toast}`);
        }
    } catch (error) {
        console.error('确认真命盘失败:', error);
        addSystemMessage('确认真命盘失败，请稍后重试');
    }
}

// 发送消息到 AI
async function sendToAI(message) {
    try {
        const response = await fetch('/verify/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: AppState.userId,
                message: message,
                history: AppState.conversationHistory,
                chart_uploaded: AppState.baziUploaded && AppState.ziweiUploaded,
                group_index: AppState.currentGroupIndex,
                life_events: AppState.lifeEvents,
                parsed_chart: AppState.parsedChart,
                chart_locked: AppState.chartLocked
            })
        });
        
        const result = await response.json();
        
        if (result.ok) {
            // 添加AI回复到界面
            addAIMessage(result.message, result.ai_name);
            
            // 如果触发了验证，显示验证结果
            if (result.verification_triggered) {
                if (result.bazi_verification) {
                    updateBaziResult(result.bazi_verification);
                }
                if (result.ziwei_verification) {
                    updateZiweiResult(result.ziwei_verification);
                }
            }
        } else {
            addSystemMessage(`AI回复失败：${result.toast}`);
        }
    } catch (error) {
        console.error('发送消息到AI失败:', error);
        addSystemMessage('AI回复失败，请稍后重试');
    }
}

// 处理文件上传
function handleFileUpload(type) {
    return async function(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = async function(e) {
            const content = e.target.result;
            
            if (type === 'bazi') {
                Elements.baziText.value = content;
                await uploadChart(content, 'bazi');
            } else {
                Elements.ziweiText.value = content;
                await uploadChart(content, 'ziwei');
            }
        };
        reader.readAsText(file);
    };
}

// 处理文本输入
function handleTextInput(type) {
    return debounce(async function() {
        const text = type === 'bazi' ? Elements.baziText.value : Elements.ziweiText.value;
        if (text.trim()) {
            await uploadChart(text, type);
        }
    }, 1000);
}

// 上传命盘
async function uploadChart(content, type) {
    try {
        const response = await fetch('/verify/api/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: AppState.userId,
                raw_text: content,
                chart_type: type,
                group_index: AppState.currentGroupIndex,
                use_ai: false
            })
        });
        
        const result = await response.json();
        
        if (result.ok) {
            if (type === 'bazi') {
                AppState.baziUploaded = true;
                Elements.baziStatus.textContent = '已上传';
                Elements.baziStatus.className = 'result-status uploaded';
                updateBaziResult(result);
            } else {
                AppState.ziweiUploaded = true;
                Elements.ziweiStatus.textContent = '已上传';
                Elements.ziweiStatus.className = 'result-status uploaded';
                updateZiweiResult(result);
            }
            
            // 保存解析后的命盘数据
            AppState.parsedChart = result.parsed;
            
            addSystemMessage(`${type === 'bazi' ? '八字' : '紫微'}命盘上传成功！`);
        } else {
            addSystemMessage(`${type === 'bazi' ? '八字' : '紫微'}命盘上传失败：${result.toast}`);
        }
    } catch (error) {
        console.error('上传命盘失败:', error);
        addSystemMessage('上传失败，请稍后重试');
    }
}

// 切换组
function switchGroup(groupIndex) {
    AppState.currentGroupIndex = groupIndex;
    
    // 更新UI状态
    document.querySelectorAll('.group-switch').forEach(el => {
        el.classList.remove('active');
    });
    document.querySelector(`[data-group-index="${groupIndex}"]`).classList.add('active');
    
    // 清空当前组的数据
    Elements.baziText.value = '';
    Elements.ziweiText.value = '';
    Elements.baziResult.innerHTML = '<p class="empty-state">上传八字命盘后，验证结果将显示在这里</p>';
    Elements.ziweiResult.innerHTML = '<p class="empty-state">上传紫微命盘后，验证结果将显示在这里</p>';
    Elements.baziStatus.textContent = '等待上传...';
    Elements.ziweiStatus.textContent = '等待上传...';
    
    AppState.baziUploaded = false;
    AppState.ziweiUploaded = false;
    AppState.chartLocked = false;
}

// 更新八字结果
function updateBaziResult(data) {
    const html = `
        <div class="result-content">
            <h5>解析结果</h5>
            <pre>${JSON.stringify(data.parsed || {}, null, 2)}</pre>
            <p>匹配评分: <strong>${data.score || 0}</strong></p>
        </div>
    `;
    Elements.baziResult.innerHTML = html;
}

// 更新紫微结果
function updateZiweiResult(data) {
    const html = `
        <div class="result-content">
            <h5>解析结果</h5>
            <pre>${JSON.stringify(data.parsed || {}, null, 2)}</pre>
            <p>匹配评分: <strong>${data.score || 0}</strong></p>
        </div>
    `;
    Elements.ziweiResult.innerHTML = html;
}

// 更新紫微验证结果
function updateZiweiValidationResult(data) {
    const html = `
        <div class="validation-result">
            <h6>【紫微验证结果】</h6>
            <p>${data.summary || '验证完成'}</p>
            <p>置信度: <strong>${data.birth_time_confidence || '未知'}</strong></p>
            <div class="validation-status ${data.score > 0.7 ? 'success' : 'warning'}">
                ${data.score > 0.7 ? '✅ 验证通过' : '⚠️ 需要进一步验证'}
            </div>
        </div>
    `;
    
    // 添加到紫微结果区域
    Elements.ziweiResult.innerHTML += html;
}

// 添加用户消息
function addUserMessage(message) {
    const messageEl = createMessageElement('user', message);
    Elements.chatMessages.appendChild(messageEl);
    Elements.chatMessages.scrollTop = Elements.chatMessages.scrollHeight;
    
    // 添加到历史记录
    AppState.conversationHistory.push({
        role: 'user',
        content: message
    });
}

// 添加AI消息
function addAIMessage(message, aiName = '灵伴') {
    // 处理验证按钮
    const processedMessage = processValidationButtons(message);
    
    const messageEl = createMessageElement('ai', processedMessage, aiName);
    Elements.chatMessages.appendChild(messageEl);
    Elements.chatMessages.scrollTop = Elements.chatMessages.scrollHeight;
    
    // 添加到历史记录
    AppState.conversationHistory.push({
        role: 'assistant',
        content: message
    });
}

// 添加系统消息
function addSystemMessage(message) {
    const messageEl = createMessageElement('system', message);
    Elements.chatMessages.appendChild(messageEl);
    Elements.chatMessages.scrollTop = Elements.chatMessages.scrollHeight;
}

// 创建消息元素
function createMessageElement(type, content, aiName = null) {
    const div = document.createElement('div');
    div.className = `message ${type}-message`;
    
    if (type === 'user') {
        div.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">${content}</div>
        `;
    } else if (type === 'ai') {
        div.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                ${aiName ? `<div class="ai-name">${aiName}</div>` : ''}
                <div class="ai-text">${content}</div>
            </div>
        `;
    } else if (type === 'system') {
        div.innerHTML = `
            <div class="system-message">${content}</div>
        `;
    }
    
    return div;
}

// 处理验证按钮
function processValidationButtons(message) {
    if (!AppState.chartLocked) {
        return message;
    }
    
    // 将验证按钮转换为可点击的链接
    return message.replace(
        /\[✅ 准\]\(#yes-([^)]+)\)/g,
        '<button class="validation-btn yes-btn" onclick="handleValidationButtonClick(\'#yes-$1\')">✅ 准</button>'
    ).replace(
        /\[❌ 不准\]\(#no-([^)]+)\)/g,
        '<button class="validation-btn no-btn" onclick="handleValidationButtonClick(\'#no-$1\')">❌ 不准</button>'
    );
}

// 处理验证按钮点击（全局函数）
window.handleValidationButtonClick = function(clickData) {
    Elements.chatInput.value = clickData;
    sendMessage();
};

// 从点击数据中提取断语
function extractStatementFromClick(clickData) {
    // 这里应该从消息历史中找到对应的断语文本
    // 简化处理，返回默认值
    return "命理断语";
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}