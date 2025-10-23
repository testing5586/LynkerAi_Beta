#!/bin/bash
# LynkerAI Provider Manager 集成测试脚本

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   🧪 LynkerAI Multi-Provider 集成测试                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

echo "1️⃣ 检查文件结构..."
if [ -f "provider_manager.py" ] && [ -f "provider_test.py" ] && [ -f "templates/performance.html" ]; then
    echo "   ✅ 所有文件存在"
else
    echo "   ❌ 文件缺失"
    exit 1
fi

echo ""
echo "2️⃣ 测试性能报告生成..."
python3 provider_manager.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ 性能报告生成成功"
else
    echo "   ❌ 性能报告生成失败"
    exit 1
fi

echo ""
echo "3️⃣ 检查 API 端点..."
curl -s http://localhost:8008/api/provider/stats > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ API 端点正常"
else
    echo "   ⚠️  API 端点未响应（可能 Upload API 未启动）"
fi

echo ""
echo "4️⃣ 检查统计数据文件..."
if [ -f "provider_stats.json" ]; then
    echo "   ✅ 统计数据文件存在"
else
    echo "   ℹ️  统计数据文件将在首次使用时创建"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   ✅ 集成测试完成                                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "💡 下一步:"
echo "   1. 运行测试: python3 provider_test.py"
echo "   2. 查看面板: http://localhost:8008/provider-dashboard"
echo ""
