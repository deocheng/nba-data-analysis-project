#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据缓存管理类
"""
import os
import json
import hashlib
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CacheManager:
    """缓存管理类"""

    def __init__(self, cache_dir="nba_data/cache", cache_ttl=24):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            cache_ttl: 缓存有效期（小时）
        """
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_cache_key(self, endpoint, **params):
        """
        生成缓存键
        
        Args:
            endpoint: API端点名称
            **params: API参数
            
        Returns:
            缓存键字符串
        """
        # 排序参数以确保相同参数生成相同的键
        sorted_params = sorted(params.items())
        params_str = "|".join([f"{k}:{v}" for k, v in sorted_params])
        key_str = f"{endpoint}:{params_str}"
        
        # 使用MD5生成哈希值作为缓存文件名
        hash_obj = hashlib.md5(key_str.encode('utf-8'))
        return hash_obj.hexdigest()

    def _get_cache_file(self, key):
        """
        获取缓存文件路径
        
        Args:
            key: 缓存键
            
        Returns:
            缓存文件路径
        """
        return os.path.join(self.cache_dir, f"{key}.json")

    def get(self, endpoint, **params):
        """
        获取缓存数据
        
        Args:
            endpoint: API端点名称
            **params: API参数
            
        Returns:
            缓存数据，如果缓存不存在或已过期则返回None
        """
        key = self._generate_cache_key(endpoint, **params)
        cache_file = self._get_cache_file(key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # 检查缓存是否过期
            cached_time = datetime.fromisoformat(cached_data.get('cached_at', datetime.now().isoformat()))
            current_time = datetime.now()
            
            if (current_time - cached_time).total_seconds() > self.cache_ttl * 3600:
                logger.info(f"缓存已过期: {cache_file}")
                return None
            
            logger.info(f"从缓存获取数据: {endpoint}")
            return cached_data.get('data')
            
        except Exception as e:
            logger.error(f"读取缓存失败: {e}")
            return None

    def set(self, endpoint, data, **params):
        """
        设置缓存数据
        
        Args:
            endpoint: API端点名称
            data: 要缓存的数据
            **params: API参数
            
        Returns:
            bool: 缓存是否成功
        """
        key = self._generate_cache_key(endpoint, **params)
        cache_file = self._get_cache_file(key)
        
        try:
            cached_data = {
                'data': data,
                'cached_at': datetime.now().isoformat(),
                'endpoint': endpoint,
                'params': params
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"缓存数据成功: {endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"写入缓存失败: {e}")
            return False

    def clear(self, endpoint=None, **params):
        """
        清除缓存
        
        Args:
            endpoint: API端点名称（可选）
            **params: API参数（可选）
            
        Returns:
            int: 清除的缓存文件数量
        """
        cleared_count = 0
        
        if endpoint and params:
            # 清除特定端点和参数的缓存
            key = self._generate_cache_key(endpoint, **params)
            cache_file = self._get_cache_file(key)
            
            if os.path.exists(cache_file):
                os.remove(cache_file)
                cleared_count = 1
                logger.info(f"清除缓存: {cache_file}")
                
        elif endpoint:
            # 清除特定端点的所有缓存
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_file = os.path.join(self.cache_dir, filename)
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            cached_data = json.load(f)
                        if cached_data.get('endpoint') == endpoint:
                            os.remove(cache_file)
                            cleared_count += 1
                    except Exception:
                        pass
            logger.info(f"清除 {endpoint} 端点的 {cleared_count} 个缓存")
            
        else:
            # 清除所有缓存
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_file = os.path.join(self.cache_dir, filename)
                    os.remove(cache_file)
                    cleared_count += 1
            logger.info(f"清除所有 {cleared_count} 个缓存")
            
        return cleared_count

    def get_cache_stats(self):
        """
        获取缓存统计信息
        
        Returns:
            dict: 缓存统计信息
        """
        total_cache = 0
        fresh_cache = 0
        expired_cache = 0
        
        current_time = datetime.now()
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                total_cache += 1
                cache_file = os.path.join(self.cache_dir, filename)
                
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cached_data.get('cached_at', datetime.now().isoformat()))
                    if (current_time - cached_time).total_seconds() <= self.cache_ttl * 3600:
                        fresh_cache += 1
                    else:
                        expired_cache += 1
                        
                except Exception:
                    expired_cache += 1
        
        return {
            'total_cache': total_cache,
            'fresh_cache': fresh_cache,
            'expired_cache': expired_cache,
            'cache_dir': self.cache_dir,
            'cache_ttl': self.cache_ttl
        }

if __name__ == "__main__":
    # 测试缓存管理器
    cache = CacheManager()
    
    # 测试设置缓存
    test_data = {'test': 'data', 'value': 42}
    cache.set('test_endpoint', test_data, param1='value1', param2='value2')
    
    # 测试获取缓存
    cached_data = cache.get('test_endpoint', param1='value1', param2='value2')
    print(f"获取缓存数据: {cached_data}")
    
    # 测试缓存统计
    stats = cache.get_cache_stats()
    print(f"缓存统计: {stats}")
    
    # 测试清除缓存
    cleared = cache.clear('test_endpoint')
    print(f"清除缓存数量: {cleared}")
    
    # 再次获取缓存（应该为None）
    cached_data = cache.get('test_endpoint', param1='value1', param2='value2')
    print(f"清除后获取缓存: {cached_data}")