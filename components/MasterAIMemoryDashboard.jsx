import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const MasterAIMemoryDashboard = () => {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState(null);
  const [userId, setUserId] = useState('u_demo');
  const [expandedCards, setExpandedCards] = useState(new Set());

  // 加载记忆数据
  const loadMemories = async (isSearch = false) => {
    setLoading(true);
    setError(null);

    try {
      let url;
      if (isSearch && searchQuery.trim()) {
        url = `/api/master-ai/memory/search?q=${encodeURIComponent(searchQuery)}&limit=50`;
      } else {
        url = `/api/master-ai/memory?user_id=${userId}&limit=50`;
        if (selectedTag) {
          url += `&tag=${encodeURIComponent(selectedTag)}`;
        }
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const memoriesData = data.memories || data.results || [];
      setMemories(memoriesData);

      console.log('✅ 已加载记忆数量:', memoriesData.length);
      console.log('📊 平均相似度:', calculateAvgSimilarity(memoriesData));
      console.log('👤 当前用户ID:', userId);
    } catch (err) {
      setError(err.message);
      console.error('⚠️ 加载失败:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemories();
  }, [userId, selectedTag]);

  // 计算平均相似度
  const calculateAvgSimilarity = (data) => {
    if (!data || data.length === 0) return 0;
    const sum = data.reduce((acc, item) => acc + (item.similarity || 0), 0);
    return (sum / data.length).toFixed(2);
  };

  // 获取所有唯一标签
  const getAllTags = () => {
    const tagSet = new Set();
    memories.forEach(mem => {
      if (mem.tags && Array.isArray(mem.tags)) {
        mem.tags.forEach(tag => tagSet.add(tag));
      }
    });
    return Array.from(tagSet);
  };

  // 格式化时间
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 切换卡片展开
  const toggleCard = (id) => {
    const newExpanded = new Set(expandedCards);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedCards(newExpanded);
  };

  // 统计数据
  const stats = {
    total: memories.length,
    avgSimilarity: calculateAvgSimilarity(memories),
    userId: userId
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-purple-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 头部统计栏 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 shadow-xl"
        >
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                🧠 Lynker Master AI Memory Dashboard
              </h1>
              <div className="flex gap-6 text-white/90">
                <div className="flex items-center gap-2">
                  <span className="text-sm">📊 记忆总数:</span>
                  <span className="font-bold text-lg">{stats.total}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm">⭐ 平均相似度:</span>
                  <span className="font-bold text-lg">{stats.avgSimilarity}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm">👤 用户:</span>
                  <span className="font-mono text-sm">{stats.userId}</span>
                </div>
              </div>
            </div>
            <a
              href="/upload"
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-6 py-3 rounded-xl font-bold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
            >
              📤 上传到 Vault
            </a>
          </div>
        </motion.div>

        {/* 搜索与筛选栏 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 shadow-xl"
        >
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && loadMemories(true)}
              placeholder="🔍 搜索记忆内容..."
              className="flex-1 px-4 py-3 rounded-xl bg-white/20 text-white placeholder-white/60 border-2 border-white/30 focus:border-white/60 focus:outline-none"
            />
            <button
              onClick={() => loadMemories(true)}
              className="px-6 py-3 bg-white/20 hover:bg-white/30 text-white rounded-xl font-bold transition-all duration-300"
            >
              搜索
            </button>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedTag(null);
                loadMemories(false);
              }}
              className="px-6 py-3 bg-white/20 hover:bg-white/30 text-white rounded-xl font-bold transition-all duration-300"
            >
              重置
            </button>
          </div>

          {/* 标签筛选 */}
          <div className="flex flex-wrap gap-2">
            <span className="text-white/80 text-sm mr-2 self-center">🏷️ 标签筛选:</span>
            {getAllTags().map(tag => (
              <button
                key={tag}
                onClick={() => setSelectedTag(selectedTag === tag ? null : tag)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                  selectedTag === tag
                    ? 'bg-white text-purple-700 shadow-lg'
                    : 'bg-white/20 text-white hover:bg-white/30'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </motion.div>

        {/* 加载状态 */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-white mb-4"></div>
            <p className="text-white text-xl">🧠 正在加载记忆...</p>
          </div>
        )}

        {/* 错误状态 */}
        {error && !loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-500/20 backdrop-blur-lg border-2 border-red-500 rounded-2xl p-6 text-white text-center"
          >
            <p className="text-xl">⚠️ 无法连接到 Master AI Memory API</p>
            <p className="text-sm mt-2 opacity-80">{error}</p>
          </motion.div>
        )}

        {/* 空数据状态 */}
        {!loading && !error && memories.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-12 text-white text-center"
          >
            <p className="text-2xl mb-4">📭 暂无记忆记录</p>
            <p className="text-white/70">尝试上传一些文档到 Vault，系统会自动生成记忆。</p>
          </motion.div>
        )}

        {/* 记忆卡片列表 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AnimatePresence>
            {!loading && !error && memories.map((memory, index) => {
              const isExpanded = expandedCards.has(memory.id || index);
              const summary = memory.summary || '无摘要';
              const shortSummary = summary.length > 100 ? summary.substring(0, 100) + '...' : summary;

              return (
                <motion.div
                  key={memory.id || index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ scale: 1.03 }}
                  className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-300"
                >
                  {/* 卡片顶部 */}
                  <div className="mb-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-white font-bold text-lg flex-1 break-words">
                        {memory.partner_id || 'Unknown'}
                      </h3>
                      <span className="text-white/90 font-mono text-sm ml-2 whitespace-nowrap">
                        {(memory.similarity * 100).toFixed(0)}%
                      </span>
                    </div>
                    {/* 相似度进度条 */}
                    <div className="w-full bg-white/20 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${(memory.similarity || 0) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* 摘要 */}
                  <div className="mb-4">
                    <p className="text-white/90 text-sm leading-relaxed">
                      {isExpanded ? summary : shortSummary}
                    </p>
                    {summary.length > 100 && (
                      <button
                        onClick={() => toggleCard(memory.id || index)}
                        className="text-blue-300 hover:text-blue-200 text-sm mt-2 underline"
                      >
                        {isExpanded ? '收起' : '展开更多'}
                      </button>
                    )}
                  </div>

                  {/* 底部标签与时间 */}
                  <div className="flex justify-between items-center flex-wrap gap-2">
                    <div className="flex flex-wrap gap-2">
                      {memory.tags && memory.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-white/20 text-white text-xs rounded-full font-medium"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <span className="text-white/60 text-xs">
                      🕒 {formatDate(memory.last_interaction)}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default MasterAIMemoryDashboard;
