# monitoring_decorators.py
import time
import functools
import uuid
from flask import request, g
from monitoring_db import monitoring_db
import logging

logger = logging.getLogger(__name__)


def get_request_id():
    """获取或生成请求ID"""
    if not hasattr(g, 'request_id'):
        g.request_id = str(uuid.uuid4())[:8]
    return g.request_id


def monitor_api(func):
    """API性能监控装饰器"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[DEBUG] monitor_api 装饰器被调用了！函数: {func.__name__}")
        # 生成请求ID
        request_id = get_request_id()
        start_time = time.time()

        try:
            response = func(*args, **kwargs)
            status_code = response.status_code if hasattr(response, 'status_code') else 200
            return response
        except Exception as e:
            status_code = 500
            raise
        finally:
            # 计算响应时间
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒

            # 记录监控数据
            monitoring_db.record_api_metric(
                request_id=request_id,
                endpoint=request.path,
                method=request.method,
                status_code=status_code,
                response_time=response_time,
                client_ip=request.remote_addr
            )

            # 日志记录
            logger.info(f"[{request_id}] {request.method} {request.path} "
                        f"status={status_code} time={response_time:.2f}ms")

            # 慢请求告警
            if response_time > 3000:  # 超过3秒
                monitoring_db.record_alert(
                    alert_level='WARNING',
                    alert_type='SLOW_API',
                    message=f"API响应缓慢: {request.method} {request.path} 耗时{response_time:.2f}ms",
                    metric_value=response_time,
                    threshold=3000
                )

    return wrapper


def monitor_model(func):
    """模型推理性能监控装饰器 - 修复版"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request_id = get_request_id()

        # 记录开始时间
        start_time = time.time()

        # 执行原始函数
        result = func(*args, **kwargs)

        # 计算总时间（毫秒）
        total_time = (time.time() - start_time) * 1000

        # 获取检测数量
        num_detections = 0
        if hasattr(result, '__len__'):
            if hasattr(result, 'boxes') and result.boxes is not None:
                num_detections = len(result.boxes)
            elif hasattr(result, 'shape'):
                num_detections = result.shape[0] if len(result.shape) > 0 else 0

        # 获取GPU内存使用
        gpu_memory = None
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024
        except:
            pass

        # 记录监控数据
        try:
            monitoring_db.record_model_metric(
                request_id=request_id,
                decode_time=0,  # 装饰器无法获取详细分解时间
                preprocess_time=0,
                inference_time=total_time,  # 简化：将总时间作为推理时间
                postprocess_time=0,
                total_time=total_time,
                num_detections=num_detections,
                gpu_memory_used=gpu_memory
            )
            logger.debug(f"[{request_id}] 模型推理监控: time={total_time:.2f}ms, detections={num_detections}")
        except Exception as e:
            logger.error(f"记录模型监控数据失败: {e}")

        return result

    return wrapper


def monitor_database(query_type=None):
    """数据库查询性能监控装饰器"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_id = get_request_id()
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                query_time = (time.time() - start_time) * 1000

                # 获取返回记录数
                rows_returned = 0
                if hasattr(result, '__len__'):
                    rows_returned = len(result)

                # 记录监控数据
                monitoring_db.record_db_metric(
                    request_id=request_id,
                    query_type=query_type or func.__name__,
                    query_time=query_time,
                    rows_returned=rows_returned,
                    sql_text=str(args)  # 简化的SQL记录
                )

                # 慢查询告警
                if query_time > 100:  # 超过100毫秒
                    monitoring_db.record_alert(
                        alert_level='WARNING',
                        alert_type='SLOW_QUERY',
                        message=f"数据库查询缓慢: {query_type or func.__name__} 耗时{query_time:.2f}ms",
                        metric_value=query_time,
                        threshold=100
                    )

        return wrapper

    return decorator