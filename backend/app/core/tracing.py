"""分布式追踪 - OpenTelemetry集成"""

import time
from functools import wraps

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings


def setup_tracing(app):
    """设置分布式追踪

    Args:
        app: FastAPI应用实例
    """
    # 创建资源
    resource = Resource.create(
        {"service.name": settings.PROJECT_NAME, "service.version": settings.VERSION}
    )

    # 创建TracerProvider
    tracer_provider = TracerProvider(resource=resource)

    # 配置Jaeger导出器
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    # 添加Span处理器
    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    # 设置全局TracerProvider
    trace.set_tracer_provider(tracer_provider)

    # 自动注入FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # 自动注入SQLAlchemy
    SQLAlchemyInstrumentor().instrument()

    # 自动注入Redis
    RedisInstrumentor().instrument()


def trace_function(name: str = None):
    """函数追踪装饰器

    Args:
        name: Span名称
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                # 添加属性
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("function.status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("function.status", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("function.duration", duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("function.status", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("function.duration", duration)

        # 判断是否为异步函数
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def add_span_attributes(**attributes):
    """添加Span属性

    Args:
        **attributes: 属性键值对
    """
    span = trace.get_current_span()
    if span:
        for key, value in attributes.items():
            span.set_attribute(key, value)


def add_span_event(name: str, attributes: dict = None):
    """添加Span事件

    Args:
        name: 事件名称
        attributes: 事件属性
    """
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes or {})
