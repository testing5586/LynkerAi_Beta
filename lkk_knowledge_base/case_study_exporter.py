"""
案例导出器 - 从 user_verification_results 表导出脱敏案例
定期执行，将验证结果导出到 case_study/ 目录
"""
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class CaseStudyExporter:
    """
    案例导出器
    从 Supabase user_verification_results 表导出，去标识化后保存到 case_study/
    """
    
    def __init__(self, output_dir: str = "lkk_knowledge_base/case_study"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 Supabase 客户端
        self.sp = self._init_supabase()
    
    def _init_supabase(self):
        """初始化 Supabase 客户端"""
        try:
            from supabase import create_client
            SUPABASE_URL = os.getenv("SUPABASE_URL")
            SUPABASE_KEY = os.getenv("SUPABASE_KEY")
            
            if not SUPABASE_URL or not SUPABASE_KEY:
                print("⚠️ Supabase 未配置，案例导出功能不可用")
                return None
            
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"❌ Supabase 初始化失败: {e}")
            return None
    
    def export_cases(
        self, 
        limit: int = 100, 
        min_score: float = 0.7,
        min_events: int = 3
    ) -> int:
        """
        导出验证案例
        
        Args:
            limit: 最多导出数量
            min_score: 最低匹配分数（八字或紫微任一 ≥ min_score）
            min_events: 最少人生事件数
            
        Returns:
            导出的案例数量
        """
        if not self.sp:
            print("❌ Supabase 客户端未初始化")
            return 0
        
        try:
            # 查询高质量验证结果
            response = self.sp.table("user_verification_results") \
                .select("*") \
                .gte("life_events_count", min_events) \
                .limit(limit) \
                .execute()
            
            if not response.data:
                print("ℹ️ 没有符合条件的验证结果")
                return 0
            
            exported_count = 0
            
            for record in response.data:
                # 过滤：至少有一个评分达标
                bazi_score = record.get("bazi_score", 0)
                ziwei_score = record.get("ziwei_score", 0)
                
                if max(bazi_score, ziwei_score) < min_score:
                    continue
                
                # 脱敏并导出
                case = self._anonymize_case(record)
                filename = self._generate_filename(record)
                filepath = self.output_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(case, f, ensure_ascii=False, indent=2)
                
                exported_count += 1
                print(f"✅ 导出案例: {filename}")
            
            print(f"\n📊 总计导出 {exported_count} 个案例")
            return exported_count
            
        except Exception as e:
            print(f"❌ 导出案例失败: {e}")
            return 0
    
    def _anonymize_case(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        去标识化案例数据
        移除 user_id、个人信息等敏感字段
        """
        # 生成匿名ID（基于原user_id的哈希）
        user_id = record.get("user_id", "unknown")
        anonymous_id = hashlib.sha256(str(user_id).encode()).hexdigest()[:12]
        
        return {
            "case_id": anonymous_id,
            "created_at": record.get("created_at", ""),
            "group_index": record.get("group_index", 0),
            
            # 八字验证结果
            "bazi_verification": {
                "score": record.get("bazi_score", 0),
                "matches": record.get("bazi_matches", []),
                "mismatches": record.get("bazi_mismatches", []),
                "summary": record.get("bazi_summary", "")
            },
            
            # 紫微验证结果
            "ziwei_verification": {
                "score": record.get("ziwei_score", 0),
                "matches": record.get("ziwei_matches", []),
                "mismatches": record.get("ziwei_mismatches", []),
                "summary": record.get("ziwei_summary", "")
            },
            
            # 人生事件数量（不包含具体内容，保护隐私）
            "life_events_count": record.get("life_events_count", 0),
            
            # 元数据
            "export_date": datetime.now().isoformat(),
            "data_source": "user_verification_results",
            "anonymized": True
        }
    
    def _generate_filename(self, record: Dict[str, Any]) -> str:
        """
        生成案例文件名
        格式：YYYY_case_XXXXX.json
        """
        created_at = record.get("created_at", "")
        year = created_at[:4] if created_at else datetime.now().year
        
        # 使用记录ID或生成随机编号
        record_id = record.get("id", 0)
        case_number = str(record_id).zfill(6)
        
        return f"{year}_case_{case_number}.json"
    
    def get_export_stats(self) -> Dict[str, Any]:
        """
        获取导出统计信息
        """
        if not self.output_dir.exists():
            return {"total_cases": 0, "latest_export": None}
        
        case_files = list(self.output_dir.glob("*.json"))
        
        latest_file = None
        latest_time = None
        
        for file in case_files:
            mtime = file.stat().st_mtime
            if latest_time is None or mtime > latest_time:
                latest_time = mtime
                latest_file = file.name
        
        return {
            "total_cases": len(case_files),
            "latest_export": latest_file,
            "export_directory": str(self.output_dir)
        }


# CLI 入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="导出验证案例到知识库")
    parser.add_argument("--limit", type=int, default=100, help="最多导出数量")
    parser.add_argument("--min-score", type=float, default=0.7, help="最低匹配分数")
    parser.add_argument("--min-events", type=int, default=3, help="最少人生事件数")
    
    args = parser.parse_args()
    
    exporter = CaseStudyExporter()
    
    print("=" * 60)
    print("LKK Knowledge Base - 案例导出工具")
    print("=" * 60)
    print(f"导出参数: limit={args.limit}, min_score={args.min_score}, min_events={args.min_events}")
    print()
    
    # 执行导出
    count = exporter.export_cases(
        limit=args.limit,
        min_score=args.min_score,
        min_events=args.min_events
    )
    
    # 显示统计
    stats = exporter.get_export_stats()
    print()
    print("=" * 60)
    print("导出统计")
    print("=" * 60)
    print(f"知识库总案例数: {stats['total_cases']}")
    print(f"最新导出文件: {stats['latest_export']}")
    print(f"导出目录: {stats['export_directory']}")
