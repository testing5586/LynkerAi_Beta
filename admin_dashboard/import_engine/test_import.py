#!/usr/bin/env python3
"""
命盘导入系统测试脚本
Test script for chart import system
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from import_engine.normalize_chart import normalize_from_wenmote, normalize_from_ocr

def test_normalize_wenmote():
    """测试文墨 JSON 规范化"""
    print("\n" + "="*60)
    print("测试 1: 文墨 JSON 规范化")
    print("="*60)
    
    sample_data = {
        "name": "张三",
        "gender": "男",
        "birth_time": "1990-05-20T14:30:00",
        "palaces": {
            "夫妻宫": {"main_star": "天府"},
            "财帛宫": {"main_star": "武曲"}
        },
        "transformations": {
            "hualu": True,
            "huaji": False
        }
    }
    
    result = normalize_from_wenmote(sample_data)
    
    print(f"姓名: {result['name']}")
    print(f"性别: {result['gender']}")
    print(f"出生时间: {result['birth_time']}")
    print(f"夫妻宫主星: {result['birth_data']['marriage_palace_star']}")
    print(f"财帛宫主星: {result['birth_data']['wealth_palace_star']}")
    print(f"化禄: {result['birth_data']['transformations']['hualu']}")
    print(f"化忌: {result['birth_data']['transformations']['huaji']}")
    
    assert result['name'] == "张三"
    assert result['birth_data']['marriage_palace_star'] == "天府"
    assert result['birth_data']['transformations']['hualu'] == True
    
    print("\n✅ 文墨 JSON 规范化测试通过")

def test_normalize_ocr():
    """测试 OCR 规范化"""
    print("\n" + "="*60)
    print("测试 2: OCR 数据规范化")
    print("="*60)
    
    ocr_data = {
        "name": "李四",
        "gender": "女",
        "birth_time": "1995-03-15T10:20:00",
        "marriage_palace_star": "贪狼",
        "wealth_palace_star": "天机",
        "transformations": {
            "hualu": False,
            "huaji": True
        }
    }
    
    result = normalize_from_ocr(ocr_data)
    
    print(f"姓名: {result['name']}")
    print(f"性别: {result['gender']}")
    print(f"出生时间: {result['birth_time']}")
    print(f"夫妻宫主星: {result['birth_data']['marriage_palace_star']}")
    print(f"财帛宫主星: {result['birth_data']['wealth_palace_star']}")
    print(f"化禄: {result['birth_data']['transformations']['hualu']}")
    print(f"化忌: {result['birth_data']['transformations']['huaji']}")
    
    assert result['name'] == "李四"
    assert result['birth_data']['wealth_palace_star'] == "天机"
    assert result['birth_data']['transformations']['huaji'] == True
    
    print("\n✅ OCR 规范化测试通过")

def main():
    print("\n🧪 命盘导入系统测试\n")
    
    try:
        test_normalize_wenmote()
        test_normalize_ocr()
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        print("\n💡 提示：访问 http://localhost:5000/admin/import 使用导入界面")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
