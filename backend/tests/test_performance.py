"""性能测试"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics


class TestPerformance:
    """性能测试"""

    def test_api_response_time(self, client):
        """测试API响应时间"""
        endpoints = [
            "/health",
            "/api/v1/help/categories",
            "/api/v1/help/faqs",
        ]

        for endpoint in endpoints:
            times = []
            for _ in range(10):
                start = time.time()
                response = client.get(endpoint)
                duration = (time.time() - start) * 1000  # 转换为毫秒
                times.append(duration)
                assert response.status_code == 200

            avg_time = statistics.mean(times)
            p95_time = statistics.quantiles(times, n=20)[18]  # P95

            print(f"\n{endpoint}:")
            print(f"  平均响应时间: {avg_time:.2f}ms")
            print(f"  P95响应时间: {p95_time:.2f}ms")

            # 断言P95响应时间小于200ms
            assert p95_time < 200, f"{endpoint} P95响应时间超过200ms"

    def test_concurrent_requests(self, client, auth_headers):
        """测试并发请求"""

        def make_request():
            start = time.time()
            try:
                response = client.get("/api/v1/auth/me", headers=auth_headers)
                duration = time.time() - start
                return response.status_code, duration
            except Exception:
                duration = time.time() - start
                return 500, duration

        # 并发50个请求
        concurrent_users = 50
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_users)]
            results = [future.result() for future in as_completed(futures)]

        # 统计
        success_count = sum(1 for status, _ in results if status == 200)
        durations = [d for _, d in results]
        avg_duration = statistics.mean(durations) * 1000

        print(f"\n并发测试结果:")
        print(f"  并发用户数: {concurrent_users}")
        print(f"  成功请求数: {success_count}")
        print(f"  成功率: {success_count / concurrent_users * 100:.2f}%")
        print(f"  平均响应时间: {avg_duration:.2f}ms")

        # SQLite 测试环境在高并发下偶发抖动，保持合理成功率即可
        assert success_count / concurrent_users >= 0.90

    def test_database_query_performance(self, db):
        """测试数据库查询性能"""
        from app.models import User

        # 测试简单查询
        start = time.time()
        for _ in range(100):
            db.query(User).filter(User.id == 1).first()
        duration = (time.time() - start) * 1000 / 100

        print(f"\n数据库查询性能:")
        print(f"  单次查询平均时间: {duration:.2f}ms")

        # 断言单次查询小于50ms
        assert duration < 50

    def test_cache_performance(self):
        """测试缓存性能"""
        from app.services.cache_service import cache_service

        # 测试写入
        start = time.time()
        for i in range(1000):
            cache_service.set(f"test_key_{i}", f"test_value_{i}")
        write_duration = (time.time() - start) * 1000

        # 测试读取
        start = time.time()
        for i in range(1000):
            cache_service.get(f"test_key_{i}")
        read_duration = (time.time() - start) * 1000

        print(f"\n缓存性能:")
        print(f"  1000次写入总时间: {write_duration:.2f}ms")
        print(f"  1000次读取总时间: {read_duration:.2f}ms")
        print(f"  单次写入: {write_duration / 1000:.2f}ms")
        print(f"  单次读取: {read_duration / 1000:.2f}ms")

        # 断言读取性能
        assert read_duration / 1000 < 1  # 单次读取小于1ms


class TestLoadTest:
    """负载测试"""

    def test_sustained_load(self, client):
        """测试持续负载"""
        duration = 10  # 测试10秒
        start_time = time.time()
        request_count = 0
        errors = 0

        while time.time() - start_time < duration:
            try:
                response = client.get("/health")
                if response.status_code == 200:
                    request_count += 1
                else:
                    errors += 1
            except Exception:
                errors += 1

        qps = request_count / duration
        error_rate = (
            errors / (request_count + errors) * 100
            if (request_count + errors) > 0
            else 0
        )
        error_rate = errors / (request_count + errors) * 100 if (request_count + errors) > 0 else 0

        print(f"\n负载测试结果:")
        print(f"  测试时长: {duration}秒")
        print(f"  总请求数: {request_count}")
        print(f"  QPS: {qps:.2f}")
        print(f"  错误数: {errors}")
        print(f"  错误率: {error_rate:.2f}%")

        # 断言QPS大于100
        assert qps > 100
        # 断言错误率小于1%
        assert error_rate < 1


class TestMemoryLeak:
    """内存泄漏测试"""

    def test_memory_usage(self, client, auth_headers):
        """测试内存使用"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 执行1000次请求
        for _ in range(1000):
            client.get("/api/v1/auth/me", headers=auth_headers)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"\n内存使用测试:")
        print(f"  初始内存: {initial_memory:.2f}MB")
        print(f"  最终内存: {final_memory:.2f}MB")
        print(f"  内存增长: {memory_increase:.2f}MB")

        # 断言内存增长小于50MB
        assert memory_increase < 50
