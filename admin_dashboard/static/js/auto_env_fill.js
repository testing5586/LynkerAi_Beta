/**
 * LynkerAI 智能环境自动补全模块
 * 功能：根据国家和城市自动填充气候带、湿度、纬度、地形标签
 */

(function() {
    'use strict';
    
    // 等待 DOM 加载完成
    document.addEventListener('DOMContentLoaded', function() {
        initAutoEnvFill();
    });
    
    function initAutoEnvFill() {
        const countrySelect = document.getElementById('countrySelect');
        const citySelect = document.getElementById('citySelect');
        
        if (!countrySelect || !citySelect) {
            console.log('[AutoEnvFill] 国家或城市选择器未找到，跳过初始化');
            return;
        }
        
        console.log('[AutoEnvFill] 智能环境补全模块已加载');
        
        // 加载国家列表
        loadCountries();
        
        // 监听国家选择变化
        countrySelect.addEventListener('change', async function() {
            const country = countrySelect.value;
            if (!country) {
                clearCitySelect();
                clearEnvironmentFields();
                return;
            }
            
            console.log(`[AutoEnvFill] 国家已选择: ${country}`);
            await loadCities(country);
        });
        
        // 监听城市选择变化
        citySelect.addEventListener('change', async function() {
            const country = countrySelect.value;
            const city = citySelect.value;
            
            if (!country || !city) {
                clearEnvironmentFields();
                return;
            }
            
            console.log(`[AutoEnvFill] 城市已选择: ${city}`);
            await fillEnvironmentData(country, city);
        });
    }
    
    /**
     * 加载国家列表
     */
    async function loadCountries() {
        try {
            const response = await fetch('/api/location_info/countries');
            const countries = await response.json();
            
            const countrySelect = document.getElementById('countrySelect');
            countrySelect.innerHTML = '<option value="">请选择国家</option>';
            
            countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country.code;
                option.textContent = country.name;
                countrySelect.appendChild(option);
            });
            
            console.log(`[AutoEnvFill] 已加载 ${countries.length} 个国家`);
        } catch (error) {
            console.error('[AutoEnvFill] 加载国家列表失败:', error);
        }
    }
    
    /**
     * 根据国家代码加载城市列表
     */
    async function loadCities(countryCode) {
        try {
            const response = await fetch(`/api/location_info/cities/${countryCode}`);
            const cities = await response.json();
            
            const citySelect = document.getElementById('citySelect');
            citySelect.innerHTML = '<option value="">请选择城市</option>';
            citySelect.disabled = false;
            
            cities.forEach(cityData => {
                const option = document.createElement('option');
                option.value = cityData.city;
                option.textContent = cityData.city;
                citySelect.appendChild(option);
            });
            
            console.log(`[AutoEnvFill] 已加载 ${cities.length} 个城市`);
        } catch (error) {
            console.error('[AutoEnvFill] 加载城市列表失败:', error);
            clearCitySelect();
        }
    }
    
    /**
     * 根据国家和城市自动填充环境数据
     */
    async function fillEnvironmentData(country, city) {
        try {
            const response = await fetch(`/api/location_info?country=${country}&city=${city}`);
            const data = await response.json();
            
            if (data.error) {
                console.error('[AutoEnvFill] 获取位置信息失败:', data.error);
                clearEnvironmentFields();
                return;
            }
            
            // 填充环境字段
            setFieldValue('latitude', data.latitude);
            setFieldValue('longitude', data.longitude);
            setFieldValue('climate_zone', data.climate_zone);
            setFieldValue('humidity_type', data.humidity_type);
            setFieldValue('terrain_type', data.terrain_type);
            
            console.log('[AutoEnvFill] 环境数据已自动填充:', {
                latitude: data.latitude,
                longitude: data.longitude,
                climate_zone: data.climate_zone,
                humidity_type: data.humidity_type,
                terrain_type: data.terrain_type
            });
            
            // 显示成功提示（可选）
            showNotification('✅ 环境数据已自动填充');
            
        } catch (error) {
            console.error('[AutoEnvFill] 自动填充失败:', error);
            clearEnvironmentFields();
        }
    }
    
    /**
     * 设置字段值
     */
    function setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = value || '';
            
            // 触发 change 事件（如果有其他监听器）
            field.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
    
    /**
     * 清空城市选择器
     */
    function clearCitySelect() {
        const citySelect = document.getElementById('citySelect');
        if (citySelect) {
            citySelect.innerHTML = '<option value="">请先选择国家</option>';
            citySelect.disabled = true;
        }
    }
    
    /**
     * 清空环境字段
     */
    function clearEnvironmentFields() {
        setFieldValue('latitude', '');
        setFieldValue('longitude', '');
        setFieldValue('climate_zone', '');
        setFieldValue('humidity_type', '');
        setFieldValue('terrain_type', '');
    }
    
    /**
     * 显示通知消息（可选）
     */
    function showNotification(message) {
        // 如果页面有 addAIMessage 函数，使用它
        if (typeof addAIMessage === 'function') {
            addAIMessage(message);
        } else {
            console.log(message);
        }
    }
    
    // 全局暴露函数（供其他模块调用）
    window.AutoEnvFill = {
        loadCountries,
        loadCities,
        fillEnvironmentData
    };
    
})();
