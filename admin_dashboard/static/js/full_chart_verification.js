/**
 * Mode B - 灵伴主导式全盘验证机制
 * Full Chart Verification Mode with Click Prevention
 */

// ========== 全局状态管理 ==========
const state = {
    baziChart: null,
    ziweiChart: null,
    sopTemplate: null,
    analysisStarted: false,
    analysisCompleted: false,
    userId: new URLSearchParams(window.location.search).get('user_id') || '1',
    mode: 'full_chart'
};

// ========== 初始化 ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Mode B] Initializing Full Chart Verification Mode');
    initializeFileInputs();
    initializeSOPSelector();
    checkAnalysisReadiness();
});

// ========== 文件输入初始化 ==========
function initializeFileInputs() {
    const baziInput = document.getElementById('baziFileInput');
    const ziweiInput = document.getElementById('ziweiFileInput');
    const sopInput = document.getElementById('sopFileInput');

    if (baziInput) {
        baziInput.addEventListener('change', (e) => handleChartUpload(e, 'bazi'));
    }

    if (ziweiInput) {
        ziweiInput.addEventListener('change', (e) => handleChartUpload(e, 'ziwei'));
    }

    if (sopInput) {
        sopInput.addEventListener('change', handleSOPUpload);
    }
}

// ========== SOP 选择器初始化 ==========
function initializeSOPSelector() {
    const sopSelect = document.getElementById('sopTemplate');
    if (sopSelect) {
        sopSelect.addEventListener('change', (e) => {
            state.sopTemplate = e.target.value;
            console.log('[SOP] Template selected:', state.sopTemplate);
            checkAnalysisReadiness();
        });
    }

    // 加载可用的 SOP 模板
    loadAvailableSOPTemplates();
}

// ========== 加载可用 SOP 模板 ==========
async function loadAvailableSOPTemplates() {
    try {
        const response = await fetch('/verify/api/sop_templates');
        const data = await response.json();

        if (data.ok && data.templates) {
            const sopSelect = document.getElementById('sopTemplate');
            // 保留第一个默认选项
            const firstOption = sopSelect.options[0];
            sopSelect.innerHTML = '';
            sopSelect.appendChild(firstOption);

            // 添加从服务器加载的模板
            data.templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.id;
                option.textContent = `${template.name} ${template.version}`;
                sopSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('[SOP] Failed to load templates:', error);
    }
}

// ========== 命盘导入 ==========
function importChart(type) {
    const inputId = type === 'bazi' ? 'baziFileInput' : 'ziweiFileInput';
    const input = document.getElementById(inputId);
    if (input) {
        input.click();
    }
}

// ========== 处理命盘上传 ==========
async function handleChartUpload(event, type) {
    const file = event.target.files[0];
    if (!file) return;

    console.log(`[Upload] Processing ${type} chart:`, file.name);

    try {
        const content = await file.text();
        const chartData = JSON.parse(content);

        // 保存到状态
        if (type === 'bazi') {
            state.baziChart = chartData;
        } else {
            state.ziweiChart = chartData;
        }

        // 更新UI状态
        updateImportStatus(type, true);
        checkAnalysisReadiness();

    } catch (error) {
        console.error(`[Upload] Failed to parse ${type} chart:`, error);
        showError(`解析 ${type === 'bazi' ? '八字' : '紫微'} 命盘失败：${error.message}`);
        updateImportStatus(type, false);
    }
}

// ========== 更新导入状态显示 ==========
function updateImportStatus(type, success) {
    const statusId = type === 'bazi' ? 'baziStatus' : 'ziweiStatus';
    const statusCard = document.getElementById(statusId);
    const statusText = statusCard.querySelector('.status-text');

    if (success) {
        statusCard.classList.add('imported');
        statusCard.classList.remove('pending');
        statusText.textContent = '✓ 已导入';
        statusText.style.color = '#00ff9d';
    } else {
        statusCard.classList.remove('imported');
        statusCard.classList.add('pending');
        statusText.textContent = '✗ 导入失败';
        statusText.style.color = '#ff4444';
    }
}

// ========== 上传自定义 SOP ==========
function uploadCustomSOP() {
    const input = document.getElementById('sopFileInput');
    if (input) {
        input.click();
    }
}

// ========== 处理 SOP 上传 ==========
async function handleSOPUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    console.log('[SOP] Uploading custom template:', file.name);

    try {
        const content = await file.text();
        const sopData = JSON.parse(content);

        // 验证 SOP 格式
        if (!sopData.version || !sopData.modules) {
            throw new Error('无效的 SOP 模板格式');
        }

        // 上传到服务器
        const formData = new FormData();
        formData.append('sop_file', file);

        const response = await fetch('/verify/api/upload_sop', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.ok) {
            console.log('[SOP] Upload successful:', result.template_id);
            // 重新加载模板列表
            await loadAvailableSOPTemplates();
            // 自动选中新上传的模板
            document.getElementById('sopTemplate').value = result.template_id;
            state.sopTemplate = result.template_id;
            checkAnalysisReadiness();
            showSuccess('SOP 模板上传成功！');
        } else {
            throw new Error(result.message || '上传失败');
        }

    } catch (error) {
        console.error('[SOP] Upload failed:', error);
        showError(`SOP 模板上传失败：${error.message}`);
    }
}

// ========== 检查分析准备状态（核心点准机制）==========
function checkAnalysisReadiness() {
    const btn = document.getElementById('startAnalysisBtn');
    const aiMessageBox = document.getElementById('aiMessageBox');

    // 检查所有必要条件
    const hasBazi = !!state.baziChart;
    const hasZiwei = !!state.ziweiChart;
    const hasSOP = !!state.sopTemplate;
    const notStarted = !state.analysisStarted;

    const isReady = hasBazi && hasZiwei && hasSOP && notStarted;

    if (btn) {
        btn.disabled = !isReady;

        if (!hasBazi || !hasZiwei) {
            btn.textContent = '请先导入八字与紫微命盘';
        } else if (!hasSOP) {
            btn.textContent = '请选择 SOP 分析模板';
        } else if (state.analysisStarted) {
            btn.innerHTML = '<span class="loading-spinner"></span> 分析中...';
        } else {
            btn.textContent = '开始分析';
            btn.style.background = 'linear-gradient(135deg, #00ff9d 0%, #00d4aa 100%)';
        }
    }

    // 显示/隐藏灵伴提示
    if (aiMessageBox) {
        aiMessageBox.style.display = (hasBazi && hasZiwei && hasSOP && notStarted) ? 'block' : 'none';
    }

    console.log('[Ready Check]', {
        hasBazi,
        hasZiwei,
        hasSOP,
        notStarted,
        isReady
    });
}

// ========== 开始全盘分析（核心点准入口）==========
async function startFullChartAnalysis() {
    // ⚠️ 核心防护：多重检查
    if (state.analysisStarted) {
        console.warn('[Analysis] Already started, preventing duplicate call');
        return;
    }

    if (!state.baziChart || !state.ziweiChart) {
        showError('请先导入八字与紫微命盘');
        return;
    }

    if (!state.sopTemplate) {
        showError('请选择 SOP 分析模板');
        return;
    }

    // 立即标记为已开始（防止重复点击）
    state.analysisStarted = true;
    console.log('[Analysis] Starting full chart analysis...');

    // 更新按钮状态
    const btn = document.getElementById('startAnalysisBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span> 分析中...';
    btn.style.background = '#444';

    // 显示结果区域
    const resultsDiv = document.getElementById('analysisResults');
    resultsDiv.classList.add('visible');

    // 重置结果显示
    resetResultsDisplay();

    try {
        // 调用后端 API
        const response = await fetch('/verify/api/run_full_chart_ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mode: 'full_chart',
                sop_template_id: state.sopTemplate,
                bazi_chart: state.baziChart,
                ziwei_chart: state.ziweiChart,
                user_id: state.userId,
                lang: 'zh'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('[Analysis] Result received:', result);

        if (result.ok) {
            // 渲染分析结果
            renderAnalysisResults(result.data);
            state.analysisCompleted = true;
            showSuccess('分析完成！');
        } else {
            throw new Error(result.message || '分析失败');
        }

    } catch (error) {
        console.error('[Analysis] Failed:', error);
        showError(`分析失败：${error.message}<br>请检查网络连接后重试。`);

        // 恢复按钮状态（允许重试）
        state.analysisStarted = false;
        btn.disabled = false;
        btn.textContent = '开始分析';
        btn.style.background = 'linear-gradient(135deg, #00ff9d 0%, #00d4aa 100%)';
    }
}

// ========== 重置结果显示 ==========
function resetResultsDisplay() {
    const baziResults = document.getElementById('baziResults');
    const ziweiResults = document.getElementById('ziweiResults');

    baziResults.innerHTML = `
        <h3>八字 AI 分析</h3>
        <div class="loading" style="text-align: center; padding: 40px; color: #888;">
            <div class="loading-spinner"></div>
            分析中...
        </div>
    `;

    ziweiResults.innerHTML = `
        <h3>紫微 AI 分析</h3>
        <div class="loading" style="text-align: center; padding: 40px; color: #888;">
            <div class="loading-spinner"></div>
            分析中...
        </div>
    `;

    document.getElementById('comparisonBody').innerHTML = '';
    document.getElementById('aiSummary').style.display = 'none';
}

// ========== 渲染分析结果 ==========
function renderAnalysisResults(data) {
    const { bazi_analysis, ziwei_analysis, primary_ai_summary, consistency_score } = data;

    // 渲染八字分析
    renderAIAnalysis('baziResults', bazi_analysis, '八字 AI 分析');

    // 渲染紫微分析
    renderAIAnalysis('ziweiResults', ziwei_analysis, '紫微 AI 分析');

    // 渲染对比表格
    renderComparisonTable(bazi_analysis, ziwei_analysis);

    // 渲染灵伴总结
    renderPrimaryAISummary(primary_ai_summary, consistency_score);
}

// ========== 渲染单个 AI 分析结果 ==========
function renderAIAnalysis(containerId, analysis, title) {
    const container = document.getElementById(containerId);

    let html = `<h3>${title}</h3>`;

    if (analysis && analysis.modules) {
        analysis.modules.forEach(module => {
            const confidenceClass = getConfidenceClass(module.confidence);

            html += `
                <div class="module-result">
                    <h4>${module.aspect || module.module_name}</h4>
                    <div class="summary">${module.summary || ''}</div>
                    <div>
                        <span class="confidence-badge ${confidenceClass}">
                            ${module.confidence || '中'}
                        </span>
                    </div>
                    ${module.key_supporting_evidence && module.key_supporting_evidence.length > 0 ? `
                        <ul class="evidence-list">
                            ${module.key_supporting_evidence.map(e => `<li>${e}</li>`).join('')}
                        </ul>
                    ` : ''}
                    ${module.key_conflicts && module.key_conflicts.length > 0 ? `
                        <div style="margin-top: 8px; font-size: 13px; color: #ffa500;">
                            冲突点：${module.key_conflicts.join('、')}
                        </div>
                    ` : ''}
                </div>
            `;
        });
    } else {
        html += '<p style="color: #888; text-align: center; padding: 40px;">暂无分析结果</p>';
    }

    container.innerHTML = html;
}

// ========== 获取置信度样式类 ==========
function getConfidenceClass(confidence) {
    if (!confidence) return 'confidence-medium';

    const conf = confidence.toLowerCase();
    if (conf.includes('高') || conf.includes('high')) return 'confidence-high';
    if (conf.includes('低') || conf.includes('low')) return 'confidence-low';
    return 'confidence-medium';
}

// ========== 渲染对比表格 ==========
function renderComparisonTable(baziAnalysis, ziweiAnalysis) {
    const tbody = document.getElementById('comparisonBody');

    if (!baziAnalysis || !baziAnalysis.modules || !ziweiAnalysis || !ziweiAnalysis.modules) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #888;">暂无对比数据</td></tr>';
        return;
    }

    const baziModules = baziAnalysis.modules;
    const ziweiModules = ziweiAnalysis.modules;

    let html = '';

    // 假设模块顺序一致
    const maxLength = Math.max(baziModules.length, ziweiModules.length);

    for (let i = 0; i < maxLength; i++) {
        const baziMod = baziModules[i];
        const ziweiMod = ziweiModules[i];

        const moduleName = (baziMod?.aspect || baziMod?.module_name) ||
                          (ziweiMod?.aspect || ziweiMod?.module_name) ||
                          `模块 ${i + 1}`;

        const baziSummary = baziMod?.summary || '-';
        const ziweiSummary = ziweiMod?.summary || '-';

        // 简单一致度计算（可改进为更复杂的算法）
        const consistency = calculateConsistency(baziSummary, ziweiSummary);

        html += `
            <tr>
                <td><strong>${moduleName}</strong></td>
                <td>${truncate(baziSummary, 80)}</td>
                <td>${truncate(ziweiSummary, 80)}</td>
                <td>
                    <span class="confidence-badge ${getConsistencyClass(consistency)}">
                        ${consistency}%
                    </span>
                </td>
            </tr>
        `;
    }

    tbody.innerHTML = html;
}

// ========== 计算一致度（简化版）==========
function calculateConsistency(text1, text2) {
    // 简化算法：基于文本相似度
    if (text1 === text2) return 100;
    if (!text1 || !text2 || text1 === '-' || text2 === '-') return 0;

    // 简单的词汇重叠率
    const words1 = new Set(text1.split(''));
    const words2 = new Set(text2.split(''));

    const intersection = new Set([...words1].filter(x => words2.has(x)));
    const union = new Set([...words1, ...words2]);

    return Math.round((intersection.size / union.size) * 100);
}

// ========== 获取一致度样式 ==========
function getConsistencyClass(score) {
    if (score >= 70) return 'confidence-high';
    if (score >= 40) return 'confidence-medium';
    return 'confidence-low';
}

// ========== 渲染灵伴总结 ==========
function renderPrimaryAISummary(summary, consistencyScore) {
    const summaryDiv = document.getElementById('aiSummary');
    const contentDiv = document.getElementById('summaryContent');

    if (summary) {
        contentDiv.innerHTML = `
            <p style="line-height: 1.8; font-size: 16px;">${summary}</p>
            ${consistencyScore ? `
                <div style="margin-top: 16px; padding: 16px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                    <strong>整体一致度评分：</strong>
                    <span class="confidence-badge ${getConsistencyClass(consistencyScore)}" style="font-size: 16px;">
                        ${consistencyScore}%
                    </span>
                </div>
            ` : ''}
        `;
        summaryDiv.style.display = 'block';
    }
}

// ========== 工具函数：截断文本 ==========
function truncate(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// ========== 显示错误消息 ==========
function showError(message) {
    // 创建错误提示
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = message;

    // 插入到页面顶部
    const container = document.querySelector('.mode-b-container');
    container.insertBefore(errorDiv, container.firstChild);

    // 3秒后自动消失
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// ========== 显示成功消息 ==========
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.style.cssText = `
        background: rgba(0, 255, 157, 0.1);
        border-left: 4px solid #00ff9d;
        padding: 16px;
        border-radius: 8px;
        color: #00ff9d;
        margin: 16px 0;
    `;
    successDiv.textContent = message;

    const container = document.querySelector('.mode-b-container');
    container.insertBefore(successDiv, container.firstChild);

    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// ========== 导出全局函数供 HTML onclick 使用 ==========
window.importChart = importChart;
window.uploadCustomSOP = uploadCustomSOP;
window.startFullChartAnalysis = startFullChartAnalysis;
