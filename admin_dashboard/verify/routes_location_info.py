# -*- coding: utf-8 -*-
"""
LynkerAI 智能环境自动补全模块 - 位置信息 API
提供国家、城市到环境标签的映射服务
"""

from flask import Blueprint, request, jsonify
import json
import os

bp = Blueprint("location_info", __name__)


@bp.route("/api/location_info")
def get_location_info():
    """
    根据国家代码和城市名称返回环境信息
    
    参数:
        country: 国家代码 (如 CN, MY, JP)
        city: 城市名称 (如 北京, 吉隆坡)
    
    返回:
        {
            "country_code": "CN",
            "country_name": "中国",
            "city": "北京",
            "latitude": 39.904,
            "longitude": 116.407,
            "climate_zone": "温带",
            "humidity_type": "干燥",
            "terrain_type": "内陆"
        }
    """
    country = request.args.get("country")
    city = request.args.get("city")
    
    if not country or not city:
        return jsonify({"error": "Missing country or city parameter"}), 400
    
    # 读取环境数据库
    db_path = os.path.join("config", "environment_template.json")
    
    if not os.path.exists(db_path):
        return jsonify({"error": "Environment database not found"}), 500
    
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            locations = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Failed to load environment database: {str(e)}"}), 500
    
    # 查找匹配的位置信息
    for loc in locations:
        if loc["country_code"] == country and loc["city"] == city:
            return jsonify(loc)
    
    return jsonify({"error": "Location not found"}), 404


@bp.route("/api/location_info/countries")
def get_countries():
    """
    获取所有可用的国家列表
    
    返回:
        [
            {"code": "CN", "name": "中国"},
            {"code": "MY", "name": "马来西亚"},
            ...
        ]
    """
    db_path = os.path.join("config", "environment_template.json")
    
    if not os.path.exists(db_path):
        return jsonify({"error": "Environment database not found"}), 500
    
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            locations = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Failed to load environment database: {str(e)}"}), 500
    
    # 去重获取国家列表
    countries = {}
    for loc in locations:
        code = loc["country_code"]
        if code not in countries:
            countries[code] = {
                "code": code,
                "name": loc["country_name"]
            }
    
    return jsonify(list(countries.values()))


@bp.route("/api/location_info/cities/<country_code>")
def get_cities(country_code):
    """
    根据国家代码获取该国家的所有城市
    
    参数:
        country_code: 国家代码 (如 CN, MY)
    
    返回:
        [
            {"city": "北京", "latitude": 39.904, "longitude": 116.407},
            {"city": "上海", "latitude": 31.230, "longitude": 121.474},
            ...
        ]
    """
    db_path = os.path.join("config", "environment_template.json")
    
    if not os.path.exists(db_path):
        return jsonify({"error": "Environment database not found"}), 500
    
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            locations = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Failed to load environment database: {str(e)}"}), 500
    
    # 筛选该国家的所有城市
    cities = []
    for loc in locations:
        if loc["country_code"] == country_code:
            cities.append({
                "city": loc["city"],
                "latitude": loc["latitude"],
                "longitude": loc["longitude"]
            })
    
    if not cities:
        return jsonify({"error": f"No cities found for country {country_code}"}), 404
    
    return jsonify(cities)
