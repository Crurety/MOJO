"""APM监控集成 - Prometheus"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import Request, Response
from functools import wraps
import time
from typing import Callable


# 定义指标
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

ACTIVE_REQUESTS = Gauge("http_requests_active", "Number of active HTTP requests")

DB_QUERY_COUNT = Counter("db_queries_total", "Total database queries", ["operation"])

DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds", "Database query duration in seconds", ["operation"]
)

CACHE_HIT_COUNT = Counter("cache_hits_total", "Total cache hits", ["cache_type"])

CACHE_MISS_COUNT = Counter("cache_misses_total", "Total cache misses", ["cache_type"])

TASK_QUEUE_SIZE = Gauge("task_queue_size", "Number of tasks in queue", ["queue_name"])

TASK_PROCESSING_TIME = Histogram(
    "task_processing_seconds", "Task processing time in seconds", ["task_type"]
)

USER_ACTIVE_COUNT = Gauge("users_active_total", "Number of active users")

ERROR_COUNT = Counter("errors_total", "Total errors", ["error_type"])


class PrometheusMiddleware:
    """Prometheus监控中间件"""

    async def __call__(self, request: Request, call_next: Callable):
        # 增加活跃请求数
        ACTIVE_REQUESTS.inc()

        # 记录开始时间
        start_time = time.time()

        try:
            # 处理请求
            response = await call_next(request)

            # 记录请求
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
            ).inc()

            # 记录请求时长
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method=request.method, endpoint=request.url.path
            ).observe(duration)

            return response

        except Exception as e:
            # 记录错误
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
            raise

        finally:
            # 减少活跃请求数
            ACTIVE_REQUESTS.dec()


def track_db_query(operation: str):
    """数据库查询追踪装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                DB_QUERY_COUNT.labels(operation=operation).inc()
                duration = time.time() - start_time
                DB_QUERY_DURATION.labels(operation=operation).observe(duration)
                return result
            except Exception as e:
                ERROR_COUNT.labels(error_type=f"db_{type(e).__name__}").inc()
                raise

        return wrapper

    return decorator


def track_cache(cache_type: str):
    """缓存追踪装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is not None:
                CACHE_HIT_COUNT.labels(cache_type=cache_type).inc()
            else:
                CACHE_MISS_COUNT.labels(cache_type=cache_type).inc()
            return result

        return wrapper

    return decorator


async def metrics_endpoint(request: Request):
    """Prometheus指标端点"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
async def metrics_endpoint(request: Request):
    """Prometheus指标端点"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def update_task_queue_size(queue_name: str, size: int):
    """更新任务队列大小"""
    TASK_QUEUE_SIZE.labels(queue_name=queue_name).set(size)


def track_task_processing(task_type: str, duration: float):
    """追踪任务处理时间"""
    TASK_PROCESSING_TIME.labels(task_type=task_type).observe(duration)


def update_active_users(count: int):
    """更新活跃用户数"""
    USER_ACTIVE_COUNT.set(count)
