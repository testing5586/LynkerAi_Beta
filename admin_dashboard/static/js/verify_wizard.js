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
            ziweiUploaded: false,
            baziImageUrl: null, // 存储上传的图片URL
            ziweiImageUrl: null
        },
        // 组2 - 可能出生的时辰2
        {
            baziText: "",
            ziweiText: "",
            baziResult: null,
            ziweiResult: null,
            baziUploaded: false,
            ziweiUploaded: false,
            baziImageUrl: null,
            ziweiImageUrl: null
        },
        // 组3 - 可能出生的时辰3
        {
            baziText: "",
            ziweiText: "",
            baziResult: null,
            ziweiResult: null,
            baziUploaded: false,
            ziweiUploaded: false,
            baziImageUrl: null,
            ziweiImageUrl: null
        }
    ],
    conversationState: 'waiting_bazi', // waiting_bazi | waiting_ziwei | ready_to_save | saved
    conversationHistory: [], // 对话历史记录
    lifeEvents: "" // 用户讲述的人生事件
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

    // 恢复图片预览
    if (currentGroup.baziImageUrl) {
        displayImagePreview('bazi', currentGroup.baziImageUrl);
    } else {
        resetDropzone('bazi');
    }

    if (currentGroup.ziweiImageUrl) {
        displayImagePreview('ziwei', currentGroup.ziweiImageUrl);
    } else {
        resetDropzone('ziwei');
    }

    // 恢复结果展示区
    renderResult('bazi', currentGroup.baziResult, currentGroup.baziUploaded);
    renderResult('ziwei', currentGroup.ziweiResult, currentGroup.ziweiUploaded);
}

// 显示图片预览在上传区域
function displayImagePreview(type, imageUrl) {
    const dropzoneId = type === 'bazi' ? 'baziDropzone' : 'ziweiDropzone';
    const dropzone = document.getElementById(dropzoneId);
    if (!dropzone) return;

    // 添加已有图片的样式类
    dropzone.classList.add('has-image');

    // 清空原有内容并显示图片预览
    dropzone.innerHTML = `
        <div class="dropzone-content">
            <img src="${imageUrl}" class="dropzone-image-preview" alt="命盘图片" onclick="window.open('${imageUrl}', '_blank')" title="点击查看大图">
            <div class="dropzone-upload-prompt">
                <p class="dropzone-text">图片已加载。可拖拽新图片或</p>
                <button class="btn-upload" onclick="event.stopPropagation(); document.getElementById('${type}File').click()">重新选择文件</button>
            </div>
        </div>
        <input type="file" id="${type}File" accept="image/*,.txt" style="display:none;">
    `;

    // 保持拖拽功能
    setupDropzone(dropzone, type);
}

// 重置上传区域到初始状态
function resetDropzone(type) {
    const dropzoneId = type === 'bazi' ? 'baziDropzone' : 'ziweiDropzone';
    const dropzone = document.getElementById(dropzoneId);
    if (!dropzone) return;

    // 移除已有图片的样式类
    dropzone.classList.remove('has-image');

    // 恢复原始上传提示
    dropzone.innerHTML = `
        <div class="dropzone-icon">☁️</div>
        <p class="dropzone-text">拖拽图片到这里 或</p>
        <button class="btn-upload" onclick="event.stopPropagation(); document.getElementById('${type}File').click()">选择文件</button>
        <input type="file" id="${type}File" accept="image/*,.txt" style="display:none;">
        <p class="dropzone-hint">也可以直接粘贴命盘文本</p>
    `;

    // 重新初始化拖拽功能
    setupDropzone(dropzone, type);
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

// 格式化结果内容（已废弃，使用 displayResult 代替）
function formatResultContent(result) {
    if (!result) return '<p class="empty-state">⏳ 等待用户完成七步问卷以生成初步验证结果</p>';
    
    let html = '';
    if (result.parsed) {
        html += `<pre style="font-size: 12px;">${JSON.stringify(result.parsed, null, 2)}</pre>`;
    }
    if (result.message) {
        html += `<p>${result.message}</p>`;
    }
    return html || '<p class="empty-state">⏳ 等待用户完成七步问卷以生成初步验证结果</p>';
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
    // Use event delegation on document to handle dynamically created file inputs
    document.addEventListener('change', (e) => {
        if (e.target.id === 'baziFile' && e.target.files[0]) {
            handleFileUpload(e.target.files[0], 'bazi');
        } else if (e.target.id === 'ziweiFile' && e.target.files[0]) {
            handleFileUpload(e.target.files[0], 'ziwei');
        }
    });
}

async function handleFileUpload(file, type) {
    const textarea = document.getElementById(`${type}Text`);
    const statusSpan = document.getElementById(`${type}Status`);
    const currentGroup = getCurrentGroup();

    statusSpan.textContent = "读取文件中...";
    statusSpan.className = "result-status processing";

    try {
        if (file.type.startsWith('image/')) {
            // 保存图片的 Data URL 用于预览
            const reader = new FileReader();
            reader.onload = (e) => {
                if (type === 'bazi') {
                    currentGroup.baziImageUrl = e.target.result;
                } else {
                    currentGroup.ziweiImageUrl = e.target.result;
                }
                // 立即显示图片预览
                displayImagePreview(type, e.target.result);
            };
            reader.readAsDataURL(file);

            // 图片文件 - 使用OCR识别
            addAIMessage(`检测到图片文件 "${file.name}"，正在使用 OCR 识别文本...`);
            statusSpan.textContent = "OCR 识别中...";
            statusSpan.className = "result-status processing";

            // 调用OCR API
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/verify/api/ocr', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`OCR API returned status ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[OCR Response]', data);

            if (data.ok) {
                // OCR识别成功
                textarea.value = data.raw_text;
                statusSpan.textContent = "OCR 识别完成";
                statusSpan.className = "result-status success";

                addAIMessage(`✅ OCR 识别完成！已提取文本内容。请检查识别结果，如有错误可以手动修改，然后点击输入框外部完成验证。`);

                // 自动触发验证
                await processChartText(data.raw_text, type);
            } else {
                // OCR识别失败
                addAIMessage(`❌ OCR 识别失败：${data.toast}${data.raw_text ? '<br>识别到的部分文本已填入输入框，请检查和补充。' : ''}`);
                if (data.raw_text) {
                    textarea.value = data.raw_text;
                }
                statusSpan.textContent = "OCR 识别失败";
                statusSpan.className = "result-status error";
            }
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
        addAIMessage(`抱歉，读取文件 "${file.name}" 时出错了。<br>错误信息：${error.message}`);
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
        // 如果有人生事件描述，使用AI验证
        const useAI = state.lifeEvents.trim().length > 0;
        
        const response = await fetch('/verify/api/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                raw_text: text,
                wizard: {},
                notes: "",
                manual: {},
                use_ai: useAI,
                chart_type: type,
                life_events: state.lifeEvents,
                user_id: state.userId,
                group_index: state.currentGroupIndex
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            const currentGroup = getCurrentGroup();
            
            // 检测是否为自动AI验证（同时返回八字和紫微结果）
            if (data.auto_verified && data.bazi_verification && data.ziwei_verification) {
                // 自动验证：只标记当前上传的命盘，不预填另一个命盘
                if (type === 'bazi') {
                    currentGroup.baziUploaded = true;
                    currentGroup.baziText = text;
                    state.conversationState = 'waiting_ziwei';
                } else {
                    currentGroup.ziweiUploaded = true;
                    currentGroup.ziweiText = text;
                    state.conversationState = 'waiting_bazi';
                }
                
                // 存储AI验证结果（两个都存）
                currentGroup.baziResult = {
                    ...data,
                    ai_verification: data.bazi_verification
                };
                currentGroup.ziweiResult = {
                    ...data,
                    ai_verification: data.ziwei_verification
                };
                
                // 显示八字结果到 Secondary Box #1
                displayResult(currentGroup.baziResult, 'bazi');
                document.getElementById('baziStatus').textContent = "AI预测验证";
                document.getElementById('baziStatus').className = "result-status success";
                
                // 显示紫微结果到 Secondary Box #2
                displayResult(currentGroup.ziweiResult, 'ziwei');
                document.getElementById('ziweiStatus').textContent = "AI预测验证";
                document.getElementById('ziweiStatus').className = "result-status success";
                
                // 格式化置信度显示
                const formatConfidence = (verification) => {
                    const confidence = verification.birth_time_confidence || verification.score;
                    if (typeof confidence === 'string') return confidence;
                    // 兼容旧格式：数值转文字
                    if (confidence >= 0.8) return '高';
                    if (confidence >= 0.65) return '中高';
                    if (confidence >= 0.4) return '中';
                    if (confidence >= 0.2) return '偏低';
                    return '低';
                };
                
                addAIMessage(`太棒了！基于你的人生经历，我已经推测出你的命盘特征：<br>
                    八字出生时辰可信度：<strong>${formatConfidence(data.bazi_verification)}</strong><br>
                    紫微出生时辰可信度：<strong>${formatConfidence(data.ziwei_verification)}</strong><br><br>
                    💡 这是基于你的人生经历的AI推测。你现在可以上传${type === 'bazi' ? '紫微' : '八字'}命盘进行实际验证。`);

                // ⚠️ Mode B Integration: Check if both charts are ready (auto-verified case)
                checkModeBActivation();
                checkModeBReadiness();
            } else {
                // 单个验证：只更新当前类型的结果
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

                // 自动触发 Primary AI 问卷
                triggerQuestionnaireStart();

                // ⚠️ Mode B Integration: Check if both charts are ready
                checkModeBActivation();
                checkModeBReadiness();
            }
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

    // 保存现有的图片预览（如果有）
    const existingImagePreview = resultContent.querySelector('.image-preview-container');
    const imagePreviewHTML = existingImagePreview ? existingImagePreview.outerHTML : '';

    let html = '';
    
    // 如果有AI验证结果，优先显示AI结果
    if (data.ai_verification) {
        const aiResult = data.ai_verification;
        const confidence = aiResult.birth_time_confidence || aiResult.score; // 兼容旧字段
        
        // 如果是旧的数值格式，转换为置信度等级
        let confidenceLevel = confidence;
        let confidenceColor = '#6c757d';
        
        if (typeof confidence === 'number') {
            // 旧格式：数值转为文字
            if (confidence >= 0.8) {
                confidenceLevel = '高';
                confidenceColor = '#28a745';
            } else if (confidence >= 0.65) {
                confidenceLevel = '中高';
                confidenceColor = '#5cb85c';
            } else if (confidence >= 0.4) {
                confidenceLevel = '中';
                confidenceColor = '#ffc107';
            } else if (confidence >= 0.2) {
                confidenceLevel = '偏低';
                confidenceColor = '#ff8c00';
            } else {
                confidenceLevel = '低';
                confidenceColor = '#dc3545';
            }
        } else {
            // 新格式：直接使用置信度等级
            if (confidence === '高') confidenceColor = '#28a745';
            else if (confidence === '中高') confidenceColor = '#5cb85c';
            else if (confidence === '中') confidenceColor = '#ffc107';
            else if (confidence === '偏低') confidenceColor = '#ff8c00';
            else confidenceColor = '#dc3545';
        }
        
        // 检查是否有人生事件数据（判断是否完成问卷）
        const hasLifeEvents = state.lifeEvents && state.lifeEvents.trim().length > 0;
        
        html = `
            <div class="ai-verification-result">
                ${!hasLifeEvents ? `
                <div class="detail-section" style="padding: 12px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px; margin-bottom: 12px;">
                    <p style="margin: 0; font-size: 13px; color: #856404;">
                        ⏳ 等待用户完成问卷以生成完整初步批命结果
                    </p>
                </div>
                ` : ''}
                
                <div class="score-display" style="color: ${confidenceColor}; font-weight: 600; font-size: 16px;">
                    出生时辰可信度：<span style="font-size: 20px;">${confidenceLevel}</span>
                </div>
                
                ${(aiResult.key_supporting_evidence || aiResult.key_matches)?.length > 0 ? `
                <div class="detail-section" style="margin-top: 12px;">
                    <strong style="color: #28a745;">✓ 关键吻合点：</strong>
                    <ul style="margin: 8px 0; padding-left: 20px; font-size: 13px; line-height: 1.6;">
                        ${(aiResult.key_supporting_evidence || aiResult.key_matches).map(m => `<li>${m}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                ${(aiResult.key_conflicts || aiResult.key_mismatches)?.length > 0 ? `
                <div class="detail-section" style="margin-top: 12px;">
                    <strong style="color: #dc3545;">✗ 关键冲突点：</strong>
                    <ul style="margin: 8px 0; padding-left: 20px; font-size: 13px; line-height: 1.6;">
                        ${(aiResult.key_conflicts || aiResult.key_mismatches).map(m => `<li>${m}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                ${(aiResult.summary || aiResult.notes) ? `
                <div class="detail-section" style="margin-top: 12px; padding: 10px; background: #f8f9fa; border-radius: 4px; border-left: 3px solid #667eea;">
                    <strong style="color: #495057;">AI 总结：</strong>
                    <p style="margin: 6px 0 0 0; font-size: 13px; line-height: 1.6; color: #212529;">${aiResult.summary || aiResult.notes}</p>
                </div>
                ` : ''}
                
                ${aiResult.fallback ? `
                <p style="font-size: 12px; color: #6c757d; margin-top: 8px;">（使用规则验证）</p>
                ` : ''}
            </div>
        `;
    } else {
        // 降级到传统显示（无AI验证结果时）
        const typeName = type === 'bazi' ? '八字' : '紫微';
        html = `
            <div class="detail-section" style="padding: 12px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px; margin-bottom: 12px;">
                <p style="margin: 0; font-size: 13px; color: #856404;">
                    ⏳ 等待用户完成七步问卷以生成${typeName}初步验证结果
                </p>
            </div>
            
            ${data.parsed?.name ? `
            <div class="detail-item">
                <span class="detail-label">姓名：</span>
                <span>${data.parsed.name}</span>
            </div>
            ` : ''}
            
            ${data.parsed?.gender ? `
            <div class="detail-item">
                <span class="detail-label">性别：</span>
                <span>${data.parsed.gender}</span>
            </div>
            ` : ''}
            
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
        `;
    }
    
    html += `
        <details style="margin-top: 16px;">
            <summary style="cursor: pointer; font-weight: 600;">查看完整 JSON</summary>
            <pre style="margin-top: 8px;">${JSON.stringify(data.parsed, null, 2)}</pre>
        </details>
    `;

    // 先设置HTML内容，然后在前面插入图片预览
    resultContent.innerHTML = html;

    // 如果之前有图片预览，重新插入到顶部
    if (imagePreviewHTML) {
        resultContent.insertAdjacentHTML('afterbegin', imagePreviewHTML);
    } else {
        // 检查是否有新的图片需要显示
        const currentGroup = getCurrentGroup();
        const imageUrl = type === 'bazi' ? currentGroup.baziImageUrl : currentGroup.ziweiImageUrl;
        if (imageUrl) {
            displayImagePreview(type, imageUrl);
        }
    }
}

// ========== AI 引导对话 ==========
function updateAIGuidance() {
    if (state.conversationState === 'waiting_ziwei') {
        addAIMessage("很好！八字命盘已经验证完成。接下来，请上传你的<strong>紫微斗数命盘</strong>。");
    } else if (state.conversationState === 'ready_to_save') {
        // 不再自动提示保存，改为由问卷完成后触发
        console.log('两份命盘已验证完成，等待问卷触发');
    }
}

// ========== 自动触发问卷 ==========
async function triggerQuestionnaireStart() {
    try {
        const response = await fetch('/verify/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.userId,
                message: "__SYSTEM_TRIGGER_START_QUESTIONNAIRE__",
                history: state.conversationHistory,
                chart_uploaded: true,
                group_index: state.currentGroupIndex,
                life_events: state.lifeEvents,
                parsed_chart: {}
            })
        });
        
        const data = await response.json();
        
        if (data.ok && data.message) {
            // 显示 Primary AI 的问卷第一句话
            addAIMessage(`<p>${data.message}</p>`);
            
            // 更新对话历史
            state.conversationHistory.push({
                role: 'system',
                content: 'Questionnaire started'
            });
            state.conversationHistory.push({
                role: 'assistant',
                content: data.message
            });
        }
    } catch (error) {
        console.error('触发问卷失败:', error);
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
    
    // 记录用户人生事件描述（累积）
    state.lifeEvents += message + "\n";
    
    // 调用Primary AI聊天API
    try {
        addAIMessage('<p class="thinking">正在思考...</p>');
        
        // 检查是否已上传命盘
        const currentGroup = getCurrentGroup();
        const chartUploaded = currentGroup.baziUploaded || currentGroup.ziweiUploaded;
        const parsedChart = currentGroup.baziResult?.parsed || currentGroup.ziweiResult?.parsed || {};
        
        const response = await fetch('/verify/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.userId,
                message: message,
                history: state.conversationHistory,
                chart_uploaded: chartUploaded,
                group_index: state.currentGroupIndex,
                life_events: state.lifeEvents,
                parsed_chart: parsedChart
            })
        });
        
        const data = await response.json();
        
        // 移除"正在思考"消息
        const messagesContainer = document.getElementById('chatMessages');
        const thinkingMsg = messagesContainer.querySelector('.thinking');
        if (thinkingMsg) {
            thinkingMsg.closest('.message').remove();
        }
        
        if (data.ok) {
            // 显示AI回复
            addAIMessage(`<p>${data.message}</p>`);
            
            // 更新对话历史
            state.conversationHistory.push({role: 'user', content: message});
            state.conversationHistory.push({role: 'assistant', content: data.message});
            
            // 保持历史在合理长度（最近20条）
            if (state.conversationHistory.length > 20) {
                state.conversationHistory = state.conversationHistory.slice(-20);
            }
            
            // 检测是否触发了验证
            if (data.verification_triggered && data.bazi_verification && data.ziwei_verification) {
                const currentGroup = getCurrentGroup();
                
                // 保留每个命盘自己的parsed数据，只添加AI验证结果
                // 如果之前没有result，则创建新的
                if (!currentGroup.baziResult) {
                    currentGroup.baziResult = { parsed: {} };
                }
                if (!currentGroup.ziweiResult) {
                    currentGroup.ziweiResult = { parsed: {} };
                }
                
                // 添加AI验证结果，保留原有parsed数据
                currentGroup.baziResult = {
                    ...currentGroup.baziResult,
                    ai_verification: data.bazi_verification
                };
                currentGroup.ziweiResult = {
                    ...currentGroup.ziweiResult,
                    ai_verification: data.ziwei_verification
                };
                
                // 显示八字结果
                displayResult(currentGroup.baziResult, 'bazi');
                document.getElementById('baziStatus').textContent = "AI验证完成";
                document.getElementById('baziStatus').className = "result-status success";
                
                // 显示紫微结果
                displayResult(currentGroup.ziweiResult, 'ziwei');
                document.getElementById('ziweiStatus').textContent = "AI验证完成";
                document.getElementById('ziweiStatus').className = "result-status success";
                
                // 格式化置信度显示
                const formatConfidence = (verification) => {
                    const confidence = verification.birth_time_confidence || verification.score;
                    if (typeof confidence === 'string') return confidence;
                    // 兼容旧格式：数值转文字
                    if (confidence >= 0.8) return '高';
                    if (confidence >= 0.65) return '中高';
                    if (confidence >= 0.4) return '中';
                    if (confidence >= 0.2) return '偏低';
                    return '低';
                };
                
                const baziConfidence = formatConfidence(data.bazi_verification);
                const ziweiConfidence = formatConfidence(data.ziwei_verification);
                
                // 根据置信度设置颜色
                const getConfidenceColor = (conf) => {
                    if (conf === '高') return '#a8e6cf';
                    if (conf === '中高') return '#dcedc1';
                    if (conf === '中') return '#ffd3b6';
                    if (conf === '偏低') return '#ffaaa5';
                    return '#ff8b94';
                };
                
                // 显示验证结果摘要
                addAIMessage(`
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; color: white; margin-top: 10px;">
                        <h4 style="margin: 0 0 10px 0; font-size: 16px;">✨ 验证完成</h4>
                        <p style="margin: 5px 0;"><strong>八字出生时辰可信度：</strong><span style="background: ${getConfidenceColor(baziConfidence)}; color: #333; padding: 2px 8px; border-radius: 4px; font-weight: 600;">${baziConfidence}</span></p>
                        <p style="margin: 5px 0;"><strong>紫微出生时辰可信度：</strong><span style="background: ${getConfidenceColor(ziweiConfidence)}; color: #333; padding: 2px 8px; border-radius: 4px; font-weight: 600;">${ziweiConfidence}</span></p>
                    </div>
                `);
                
                console.log('✅ 验证结果已更新到UI');
            }
        } else {
            addAIMessage(`<p style="color: #721c24;">抱歉，我现在有些不舒服。${data.message || ''}</p>`);
        }
    } catch (error) {
        console.error("聊天失败:", error);
        addAIMessage('<p style="color: #721c24;">抱歉，连接出现了问题，请稍后再试。</p>');
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

    // Scroll to bottom with smooth behavior
    setTimeout(() => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
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

    // Scroll to bottom with smooth behavior
    setTimeout(() => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
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
        
        // 格式化置信度显示
        const formatConfidence = (result) => {
            const aiResult = result?.ai_verification;
            if (!aiResult) return '未验证';
            const confidence = aiResult.birth_time_confidence || aiResult.score;
            if (typeof confidence === 'string') return confidence;
            // 兼容旧格式：数值转文字
            if (confidence >= 0.8) return '高';
            if (confidence >= 0.65) return '中高';
            if (confidence >= 0.4) return '中';
            if (confidence >= 0.2) return '偏低';
            return '低';
        };
        
        const baziConfidence = formatConfidence(state.baziResult);
        const ziweiConfidence = formatConfidence(state.ziweiResult);
        
        const response = await fetch('/verify/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.userId,
                raw_text: combinedText,
                wizard: {},
                notes: `八字出生时辰可信度: ${baziConfidence}, 紫微出生时辰可信度: ${ziweiConfidence}`,
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
                <p>八字可信度：${baziConfidence} | 紫微可信度：${ziweiConfidence}</p>
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

// ==================== Mode B Integration ====================
// Show Mode B section when both charts are uploaded
// This replaces the one-by-one verification flow with parallel AI analysis

// Mode B state (separate from main wizard state)
const modeBState = {
    sopTemplate: null,
    analysisStarted: false,
    analysisCompleted: false
};

// Check if Mode B should be activated
function checkModeBActivation() {
    const currentGroup = getCurrentGroup();
    const bothChartsUploaded = currentGroup.baziUploaded && currentGroup.ziweiUploaded;

    console.log('[Mode B] Checking activation:', {
        baziUploaded: currentGroup.baziUploaded,
        ziweiUploaded: currentGroup.ziweiUploaded,
        bothReady: bothChartsUploaded
    });

    const modeBSection = document.getElementById('modeBSection');

    if (bothChartsUploaded && modeBSection) {
        // Show Mode B section with fade-in effect
        modeBSection.style.display = 'block';
        modeBSection.style.opacity = '0';
        setTimeout(() => {
            modeBSection.style.transition = 'opacity 0.5s ease-in';
            modeBSection.style.opacity = '1';
        }, 10);

        console.log('[Mode B] ✅ Activated - Both charts uploaded!');

        // Add AI message to guide user
        addAIMessage(`
            <p>🎉 <strong>两份命盘已上传完成！</strong></p>
            <p>现在可以使用 Mode B 进行全盘验证分析。</p>
            <p>请在下方选择 SOP 分析模板，然后点击"开始分析"按钮。</p>
        `);
    } else if (modeBSection) {
        // Hide Mode B section
        modeBSection.style.display = 'none';
    }
}

// Initialize Mode B SOP selector
function initModeBSOPSelector() {
    const sopSelect = document.getElementById('sopTemplate');
    if (sopSelect) {
        sopSelect.addEventListener('change', (e) => {
            modeBState.sopTemplate = e.target.value;
            console.log('[Mode B] SOP selected:', modeBState.sopTemplate);
            checkModeBReadiness();
        });
    }
}

// Check if Mode B analysis can start
function checkModeBReadiness() {
    const btn = document.getElementById('startAnalysisBtn');
    if (!btn) return;

    const currentGroup = getCurrentGroup();
    const hasBothCharts = currentGroup.baziUploaded && currentGroup.ziweiUploaded;
    const hasSOP = !!modeBState.sopTemplate;
    const notStarted = !modeBState.analysisStarted;

    const isReady = hasBothCharts && hasSOP && notStarted;

    btn.disabled = !isReady;

    if (!hasBothCharts) {
        btn.textContent = '请先上传两份命盘';
    } else if (!hasSOP) {
        btn.textContent = '请选择 SOP 分析模板';
    } else if (modeBState.analysisStarted) {
        btn.innerHTML = '<span class="loading-spinner"></span> 分析中...';
    } else {
        btn.textContent = '开始分析';
    }
}

// Upload custom SOP template
function uploadCustomSOP() {
    const input = document.getElementById('sopFileInput');
    if (input) {
        input.click();
    }
}

// Handle SOP file upload
document.addEventListener('DOMContentLoaded', () => {
    const sopInput = document.getElementById('sopFileInput');
    if (sopInput) {
        sopInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/verify/api/upload_sop', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.ok) {
                    // Reload templates and select the new one
                    const sopSelect = document.getElementById('sopTemplate');
                    const option = document.createElement('option');
                    option.value = result.template_id;
                    option.textContent = result.template_id;
                    option.selected = true;
                    sopSelect.appendChild(option);

                    modeBState.sopTemplate = result.template_id;
                    checkModeBReadiness();
                    addAIMessage(`✅ SOP 模板上传成功！`);
                } else {
                    throw new Error(result.toast || '上传失败');
                }
            } catch (error) {
                console.error('[Mode B] SOP upload failed:', error);
                addAIMessage(`❌ SOP 模板上传失败：${error.message}`);
            }
        });
    }

    // Initialize Mode B
    initModeBSOPSelector();
});

// Start full chart analysis (Mode B)
async function startFullChartAnalysis() {
    // ⚠️ Click prevention check
    if (modeBState.analysisStarted) {
        console.warn('[Mode B] Analysis already started');
        return;
    }

    const currentGroup = getCurrentGroup();

    if (!currentGroup.baziResult || !currentGroup.ziweiResult) {
        addAIMessage('请先验证两份命盘后再进行全盘分析');
        return;
    }

    if (!modeBState.sopTemplate) {
        addAIMessage('请选择 SOP 分析模板');
        return;
    }

    // Mark as started immediately
    modeBState.analysisStarted = true;
    console.log('[Mode B] Starting full chart analysis...');

    // Update button
    const btn = document.getElementById('startAnalysisBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span> 分析中...';

    // Show results section
    const resultsDiv = document.getElementById('analysisResults');
    if (resultsDiv) {
        resultsDiv.classList.add('visible');
    }

    try {
        // Call backend API
        const response = await fetch('/verify/api/run_full_chart_ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mode: 'full_chart',
                sop_template_id: modeBState.sopTemplate,
                bazi_chart: currentGroup.baziResult.parsed,
                ziwei_chart: currentGroup.ziweiResult.parsed,
                user_id: state.userId,
                lang: 'zh'
            })
        });

        const result = await response.json();

        if (result.ok) {
            console.log('[Mode B] Analysis completed successfully');
            modeBState.analysisCompleted = true;

            // Render results
            renderModeBResults(result.data);

            // Update AI message
            addAIMessage(`
                <p>✅ <strong>全盘验证分析完成！</strong></p>
                <p>一致性评分：${result.data.consistency_score}/100</p>
                <p>请查看下方的详细分析结果。</p>
            `);

            // Update button
            btn.textContent = '分析完成';
            btn.style.background = '#00ff9d';

        } else {
            throw new Error(result.toast || '分析失败');
        }

    } catch (error) {
        console.error('[Mode B] Analysis failed:', error);
        addAIMessage(`❌ 全盘分析失败：${error.message}`);

        // Allow retry
        modeBState.analysisStarted = false;
        btn.disabled = false;
        btn.textContent = '重新分析';
        btn.style.background = 'linear-gradient(135deg, #00ff9d 0%, #00d4aa 100%)';
    }
}

// Render Mode B analysis results
function renderModeBResults(data) {
    const { bazi_analysis, ziwei_analysis, primary_ai_summary, consistency_score } = data;

    // Render Bazi results
    renderAIColumn('baziAnalysisResults', bazi_analysis, '八字');

    // Render Ziwei results
    renderAIColumn('ziweiAnalysisResults', ziwei_analysis, '紫微');

    // Render comparison table
    renderComparisonTable(bazi_analysis, ziwei_analysis);

    // Render AI summary
    renderAISummary(primary_ai_summary, consistency_score);
}

// Render AI column (Bazi or Ziwei)
function renderAIColumn(elementId, analysis, typeName) {
    const column = document.getElementById(elementId);
    if (!column) return;

    let html = `<h3>${typeName} AI 分析</h3>`;

    if (analysis.modules && analysis.modules.length > 0) {
        analysis.modules.forEach(module => {
            const confidenceClass = module.confidence === '高' ? 'confidence-high' :
                                   module.confidence === '中' ? 'confidence-medium' :
                                   'confidence-low';

            html += `
                <div class="module-result">
                    <h4>${module.module_name}</h4>
                    <div class="summary">${module.summary || '无分析内容'}</div>
                    <span class="confidence-badge ${confidenceClass}">${module.confidence}</span>
                    ${module.supporting_evidence && module.supporting_evidence.length > 0 ? `
                        <ul class="evidence-list">
                            ${module.supporting_evidence.map(e => `<li>✓ ${e}</li>`).join('')}
                        </ul>
                    ` : ''}
                    ${module.conflicts && module.conflicts.length > 0 ? `
                        <ul class="evidence-list">
                            ${module.conflicts.map(c => `<li>✗ ${c}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            `;
        });
    } else {
        html += '<p style="color: #888; text-align: center; padding: 40px;">暂无分析结果</p>';
    }

    column.innerHTML = html;
}

// Render comparison table
function renderComparisonTable(baziAnalysis, ziweiAnalysis) {
    const tbody = document.getElementById('comparisonBody');
    if (!tbody) return;

    let html = '';

    const baziModules = baziAnalysis.modules || [];
    const ziweiModules = ziweiAnalysis.modules || [];

    // Match modules by module_id
    const moduleMap = {};
    baziModules.forEach(m => {
        moduleMap[m.module_id] = { bazi: m };
    });
    ziweiModules.forEach(m => {
        if (moduleMap[m.module_id]) {
            moduleMap[m.module_id].ziwei = m;
        } else {
            moduleMap[m.module_id] = { ziwei: m };
        }
    });

    Object.values(moduleMap).forEach(pair => {
        const moduleName = pair.bazi?.module_name || pair.ziwei?.module_name;
        const baziSummary = pair.bazi?.summary || '无';
        const ziweiSummary = pair.ziwei?.summary || '无';

        // Simple consistency check (could be enhanced)
        const consistency = (pair.bazi && pair.ziwei) ? '75%' : '50%';

        html += `
            <tr>
                <td><strong>${moduleName}</strong></td>
                <td>${baziSummary.substring(0, 100)}${baziSummary.length > 100 ? '...' : ''}</td>
                <td>${ziweiSummary.substring(0, 100)}${ziweiSummary.length > 100 ? '...' : ''}</td>
                <td>${consistency}</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

// Render AI summary
function renderAISummary(summary, consistencyScore) {
    const summarySection = document.getElementById('aiSummarySection');
    const summaryContent = document.getElementById('summaryContent');

    if (!summarySection || !summaryContent) return;

    let html = `
        <div style="margin-bottom: 20px;">
            <h4 style="margin-bottom: 12px;">一致性评分</h4>
            <div style="font-size: 32px; font-weight: bold; color: #fff;">
                ${consistencyScore}/100
            </div>
        </div>
    `;

    if (summary.consistent_points && summary.consistent_points.length > 0) {
        html += `
            <div style="margin-bottom: 16px;">
                <h4 style="margin-bottom: 8px;">✓ 核心一致点</h4>
                <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                    ${summary.consistent_points.map(p => `<li>${p}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (summary.divergent_points && summary.divergent_points.length > 0) {
        html += `
            <div style="margin-bottom: 16px;">
                <h4 style="margin-bottom: 8px;">⚠️ 主要分歧点</h4>
                <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                    ${summary.divergent_points.map(p => `<li>${p}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (summary.summary_text) {
        html += `
            <div style="margin-top: 20px; padding: 16px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                <h4 style="margin-bottom: 8px;">综合评述</h4>
                <p style="margin: 0; line-height: 1.8;">${summary.summary_text}</p>
            </div>
        `;
    }

    summaryContent.innerHTML = html;
    summarySection.style.display = 'block';
}

// Mode B integration is triggered directly from processChartText()
// No need for hooks - activation happens automatically after charts are verified
