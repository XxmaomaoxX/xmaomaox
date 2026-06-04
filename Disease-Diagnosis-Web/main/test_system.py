"""
植物病害检测系统测试类
用于测试系统的各项功能和性能
"""

import os
import sys
import json
import time
import unittest
import requests
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置
API_BASE_URL = "http://localhost:5000/api"
TEST_IMAGE_DIR = "E:\YOLOV8-TRAIN\PlantDoc-Object-Detection-Dataset-master\\test_images"
REPORT_DIR = "E:\YOLOV8-TRAIN\PlantDoc-Object-Detection-Dataset-master\\test_reports"


class ColorPrint:
    """控制台颜色打印"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

    @classmethod
    def info(cls, msg):
        print(f"{cls.BLUE}[INFO]{cls.END} {msg}")

    @classmethod
    def success(cls, msg):
        print(f"{cls.GREEN}[PASS]{cls.END} {msg}")

    @classmethod
    def warning(cls, msg):
        print(f"{cls.YELLOW}[WARN]{cls.END} {msg}")

    @classmethod
    def error(cls, msg):
        print(f"{cls.RED}[FAIL]{cls.END} {msg}")

    @classmethod
    def title(cls, msg):
        print(f"\n{cls.HEADER}{'=' * 60}{cls.END}")
        print(f"{cls.HEADER}{msg.center(60)}{cls.END}")
        print(f"{cls.HEADER}{'=' * 60}{cls.END}\n")


class PlantDiseaseTester:
    """植物病害检测系统测试类"""

    def __init__(self, api_base_url: str = API_BASE_URL):
        """
        初始化测试器

        Args:
            api_base_url: API服务地址
        """
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.test_results = []
        self.test_start_time = None
        self.test_end_time = None

        # 创建测试结果目录
        os.makedirs(REPORT_DIR, exist_ok=True)

    def _log_result(self, test_name: str, passed: bool, message: str = "", duration: float = 0):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

        if passed:
            ColorPrint.success(f"{test_name} - {message} ({result['duration_ms']}ms)")
        else:
            ColorPrint.error(f"{test_name} - {message}")

    # ==================== 1. 系统健康检查 ====================

    def test_health_check(self) -> bool:
        """测试健康检查接口"""
        ColorPrint.info("正在测试健康检查接口...")
        start_time = time.time()

        try:
            response = self.session.get(f"{self.api_base_url}/health", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self._log_result("健康检查", True, f"服务状态正常, 模型已加载: {data.get('model_loaded')}",
                                     duration)
                    return True
                else:
                    self._log_result("健康检查", False, f"服务状态异常: {data}", duration)
                    return False
            else:
                self._log_result("健康检查", False, f"HTTP {response.status_code}", duration)
                return False

        except Exception as e:
            self._log_result("健康检查", False, f"连接失败: {str(e)}", time.time() - start_time)
            return False

    # ==================== 2. 模型信息测试 ====================

    def test_model_info(self) -> bool:
        """测试模型信息接口"""
        ColorPrint.info("正在测试模型信息接口...")
        start_time = time.time()

        try:
            response = self.session.get(f"{self.api_base_url}/model/info", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    num_classes = data.get("num_classes", 0)
                    class_names = data.get("class_names", [])
                    self._log_result("模型信息", True,
                                     f"检测类别数: {num_classes}, 类别示例: {class_names[:5] if class_names else '无'}",
                                     duration)
                    return True
                else:
                    self._log_result("模型信息", False, data.get("error", "未知错误"), duration)
                    return False
            else:
                self._log_result("模型信息", False, f"HTTP {response.status_code}", duration)
                return False

        except Exception as e:
            self._log_result("模型信息", False, str(e), time.time() - start_time)
            return False

    # ==================== 3. 病害列表测试 ====================

    def test_diseases_list(self) -> bool:
        """测试病害列表接口"""
        ColorPrint.info("正在测试病害列表接口...")
        start_time = time.time()

        try:
            response = self.session.get(f"{self.api_base_url}/diseases", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                diseases = data.get("diseases", [])
                self._log_result("病害列表", True, f"共获取 {len(diseases)} 种病害信息", duration)

                # 打印病害列表
                if diseases:
                    ColorPrint.info(f"病害列表: {[d.get('name') for d in diseases[:10]]}")
                return True
            else:
                self._log_result("病害列表", False, f"HTTP {response.status_code}", duration)
                return False

        except Exception as e:
            self._log_result("病害列表", False, str(e), time.time() - start_time)
            return False

    # ==================== 4. 病害详情测试 ====================

    def test_disease_detail(self, disease_name: str) -> bool:
        """测试病害详情接口"""
        ColorPrint.info(f"正在测试病害详情接口: {disease_name}...")
        start_time = time.time()

        try:
            response = self.session.get(f"{self.api_base_url}/disease/{disease_name}", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    info = data.get("disease_info", {})
                    self._log_result("病害详情", True,
                                     f"名称: {info.get('disease_name')}, 严重程度: {info.get('severity')}", duration)
                    return True
                else:
                    self._log_result("病害详情", False, data.get("error", "未知错误"), duration)
                    return False
            else:
                self._log_result("病害详情", False, f"HTTP {response.status_code}", duration)
                return False

        except Exception as e:
            self._log_result("病害详情", False, str(e), time.time() - start_time)
            return False

    # ==================== 5. 检测请求测试 ====================

    def create_test_image(self, size: Tuple[int, int] = (640, 640)) -> np.ndarray:
        """创建测试图像"""
        # 创建渐变图像作为测试
        img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        for i in range(size[1]):
            color = int(255 * i / size[1])
            img[i, :, 0] = color  # 蓝色渐变
            img[i, :, 1] = color // 2
            img[i, :, 2] = 255 - color

        return img

    def save_test_image(self, filename: str = "test_image.jpg"):
        """保存测试图像"""
        os.makedirs(TEST_IMAGE_DIR, exist_ok=True)
        img = self.create_test_image()
        cv2.imwrite(f"{TEST_IMAGE_DIR}/{filename}", img)
        return f"{TEST_IMAGE_DIR}/{filename}"

    def test_predict_from_file(self, image_path: str = None) -> bool:
        """测试文件上传检测"""
        ColorPrint.info("正在测试文件上传检测...")
        start_time = time.time()

        try:
            # 如果没有提供图片，创建测试图片
            if not image_path or not os.path.exists(image_path):
                image_path = self.save_test_image("test_upload.jpg")
                ColorPrint.info(f"创建测试图片: {image_path}")

            # 准备文件
            with open(image_path, 'rb') as f:
                files = {'image': f}

                response = self.session.post(
                    f"{self.api_base_url}/predict",
                    files=files,
                    timeout=30
                )

            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    count = data.get("count", 0)
                    detections = data.get("detections", [])

                    self._log_result("文件上传检测", True,
                                     f"检测到 {count} 个目标，耗时 {data.get('latency', 0)}ms", duration)

                    # 打印检测结果
                    if detections:
                        for det in detections:
                            ColorPrint.info(f"  - {det.get('class_name')}: {det.get('confidence')}")

                    return True
                else:
                    self._log_result("文件上传检测", False, data.get("error", "未知错误"), duration)
                    return False
            else:
                self._log_result("文件上传检测", False, f"HTTP {response.status_code}", duration)
                return False

        except Exception as e:
            self._log_result("文件上传检测", False, str(e), time.time() - start_time)
            return False

    def test_predict_from_base64(self) -> bool:
        """测试Base64图片检测"""
        ColorPrint.info("正在测试Base64图片检测...")
        start_time = time.time()

        try:
            # 创建测试图片并转换为Base64
            img = self.create_test_image()
            _, buffer = cv2.imencode('.jpg', img)
            import base64
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            # 发送请求
            response = self.session.post(
                f"{self.api_base_url}/predict",
                json={'image_base64': img_base64},
                timeout=30
            )

            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    count = data.get("count", 0)
                    self._log_result("Base64检测", True, f"检测到 {count} 个目标", duration)
                    return True
                else:
                    self._log_result("Base64检测", False, data.get("error", "未知错误"), duration)
                    return False
            else:
                self._log_result("Base64检测", False, f"HTTP {response.status_code}", duration)
                return False

        except Exception as e:
            self._log_result("Base64检测", False, str(e), time.time() - start_time)
            return False

    # ==================== 6. 批量检测测试 ====================

    def test_batch_predict(self, num_images: int = 3) -> bool:
        """测试批量检测"""
        ColorPrint.info(f"正在测试批量检测 ({num_images}张图片)...")
        start_time = time.time()

        try:
            # 创建多个测试图片
            files = []
            for i in range(num_images):
                img_path = self.save_test_image(f"test_batch_{i}.jpg")
                files.append(('images', (f'img_{i}.jpg', open(img_path, 'rb'), 'image/jpeg')))

            # 发送请求
            response = self.session.post(
                f"{self.api_base_url}/predict/batch",
                files=files,
                timeout=60
            )

            # 关闭文件
            for _, file_tuple in files:
                file_tuple[1].close()

            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    total = data.get("total_images", 0)
                    results = data.get("results", [])
                    self._log_result("批量检测", True, f"处理 {total} 张图片", duration)
                    return True
                else:
                    self._log_result("批量检测", False, data.get("error", "未知错误"), duration)
                    return False
            else:
                self._log_result("批量检测", False, f"HTTP {response.status_code}", duration)
                return False

        except Exception as e:
            self._log_result("批量检测", False, str(e), time.time() - start_time)
            return False

    # ==================== 7. 历史记录测试 ====================

    def test_history(self) -> bool:
        """测试历史记录接口"""
        ColorPrint.info("正在测试历史记录接口...")
        start_time = time.time()

        try:
            response = self.session.get(f"{self.api_base_url}/history", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    history = data.get("history", [])
                    self._log_result("历史记录", True, f"获取到 {len(history)} 条记录", duration)
                    return True
                else:
                    self._log_result("历史记录", False, data.get("error", "未知错误"), duration)
                    return False
            else:
                self._log_result("历史记录", False, f"HTTP {response.status_code}", duration)
                return False

        except Exception as e:
            self._log_result("历史记录", False, str(e), time.time() - start_time)
            return False

    # ==================== 8. 性能测试 ====================

    def test_performance(self, num_requests: int = 10) -> Dict:
        """性能测试：连续发送多个检测请求"""
        ColorPrint.info(f"正在执行性能测试 ({num_requests}次请求)...")

        response_times = []
        success_count = 0

        for i in range(num_requests):
            start_time = time.time()
            try:
                img = self.create_test_image()
                _, buffer = cv2.imencode('.jpg', img)
                import base64
                img_base64 = base64.b64encode(buffer).decode('utf-8')

                response = self.session.post(
                    f"{self.api_base_url}/predict",
                    json={'image_base64': img_base64},
                    timeout=30
                )

                elapsed = time.time() - start_time
                response_times.append(elapsed)

                if response.status_code == 200:
                    success_count += 1
                    ColorPrint.info(f"  请求 {i + 1}/{num_requests}: {elapsed * 1000:.0f}ms")
                else:
                    ColorPrint.warning(f"  请求 {i + 1}/{num_requests}: 失败")

            except Exception as e:
                elapsed = time.time() - start_time
                response_times.append(elapsed)
                ColorPrint.error(f"  请求 {i + 1}/{num_requests}: {str(e)}")

        # 计算统计信息
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
        else:
            avg_time = max_time = min_time = 0

        result = {
            "total_requests": num_requests,
            "success_count": success_count,
            "success_rate": success_count / num_requests * 100,
            "avg_response_time_ms": avg_time * 1000,
            "max_response_time_ms": max_time * 1000,
            "min_response_time_ms": min_time * 1000
        }

        self._log_result("性能测试", True,
                         f"成功率: {result['success_rate']:.1f}%, 平均响应: {result['avg_response_time_ms']:.0f}ms",
                         avg_time)

        return result

    # ==================== 9. 并发测试 ====================

    def test_concurrent(self, num_threads: int = 5) -> Dict:
        """并发测试"""
        import concurrent.futures

        ColorPrint.info(f"正在执行并发测试 ({num_threads}个并发)...")
        start_time = time.time()

        def make_request(request_id):
            try:
                img = self.create_test_image()
                _, buffer = cv2.imencode('.jpg', img)
                import base64
                img_base64 = base64.b64encode(buffer).decode('utf-8')

                response = self.session.post(
                    f"{self.api_base_url}/predict",
                    json={'image_base64': img_base64},
                    timeout=30
                )
                return response.status_code == 200, time.time()
            except:
                return False, time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_threads)]
            results = [f.result() for f in futures]

        duration = time.time() - start_time
        success_count = sum(1 for r in results if r[0])

        result = {
            "concurrent_requests": num_threads,
            "success_count": success_count,
            "success_rate": success_count / num_threads * 100,
            "total_time_ms": duration * 1000
        }

        self._log_result("并发测试", True,
                         f"成功率: {result['success_rate']:.1f}%, 总耗时: {result['total_time_ms']:.0f}ms",
                         duration)

        return result

    # ==================== 10. 错误处理测试 ====================

    def test_error_handling(self) -> bool:
        """测试错误处理"""
        ColorPrint.info("正在测试错误处理...")
        all_passed = True

        # 测试空文件上传
        try:
            files = {'image': ('', b'', 'image/jpeg')}
            response = self.session.post(f"{self.api_base_url}/predict", files=files, timeout=10)

            if response.status_code != 200:
                ColorPrint.success("空文件上传: 正确返回错误")
            else:
                ColorPrint.error("空文件上传: 应该返回错误")
                all_passed = False
        except Exception as e:
            ColorPrint.success(f"空文件上传: 正确处理异常")

        # 测试无效格式文件
        try:
            files = {'image': ('test.txt', b'not an image', 'text/plain')}
            response = self.session.post(f"{self.api_base_url}/predict", files=files, timeout=10)

            if response.status_code != 200:
                ColorPrint.success("无效格式: 正确返回错误")
            else:
                ColorPrint.error("无效格式: 应该返回错误")
                all_passed = False
        except Exception as e:
            ColorPrint.success(f"无效格式: 正确处理异常")

        # 测试不存在的病害查询
        try:
            response = self.session.get(f"{self.api_base_url}/disease/不存在病害名称", timeout=10)

            if response.status_code == 404:
                ColorPrint.success("不存在病害: 正确返回404")
            else:
                ColorPrint.warning(f"不存在病害: 返回状态码 {response.status_code}")
        except Exception as e:
            ColorPrint.warning(f"不存在病害查询: {str(e)}")

        self._log_result("错误处理", all_passed, "错误处理测试完成", 0)
        return all_passed

    # ==================== 11. 运行所有测试 ====================

    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        ColorPrint.title("开始执行植物病害检测系统测试")

        self.test_start_time = datetime.now()

        # 1. 基础连接测试
        if not self.test_health_check():
            ColorPrint.error("健康检查失败，请确保后端服务已启动")
            return {"success": False, "error": "后端服务未启动"}

        # 2. 模型信息测试
        self.test_model_info()

        # 3. 病害列表测试
        self.test_diseases_list()

        # 4. 历史记录测试
        self.test_history()

        # 5. 错误处理测试
        self.test_error_handling()

        # 6. 病害详情测试（如果列表不为空）
        try:
            response = self.session.get(f"{self.api_base_url}/diseases", timeout=10)
            if response.status_code == 200:
                diseases = response.json().get("diseases", [])
                if diseases:
                    self.test_disease_detail(diseases[0].get("name", ""))
        except:
            pass

        # 7. 检测功能测试
        self.test_predict_from_file()
        self.test_predict_from_base64()

        # 8. 批量检测测试
        self.test_batch_predict(3)

        # 9. 性能测试
        perf_result = self.test_performance(100)

        # 10. 并发测试
        concurrent_result = self.test_concurrent(10)

        self.test_end_time = datetime.now()

        # 生成报告
        self.generate_report()

        return {
            "success": True,
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r["passed"]),
            "failed_tests": sum(1 for r in self.test_results if not r["passed"]),
            "performance": perf_result,
            "concurrent": concurrent_result,
            "duration_seconds": (self.test_end_time - self.test_start_time).total_seconds()
        }

    # ==================== 12. 生成测试报告 ====================

    def generate_report(self):
        """生成测试报告"""
        report_path = f"{REPORT_DIR}/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        passed = sum(1 for r in self.test_results if r["passed"])
        failed = sum(1 for r in self.test_results if not r["passed"])

        report = {
            "test_time": datetime.now().isoformat(),
            "api_base_url": self.api_base_url,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{passed / len(self.test_results) * 100:.1f}%" if self.test_results else "0%"
            },
            "details": self.test_results
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        ColorPrint.info(f"测试报告已保存: {report_path}")

        # 打印汇总
        ColorPrint.title("测试结果汇总")
        print(f"  总测试数: {len(self.test_results)}")
        print(f"  通过: {passed}")
        print(f"  失败: {failed}")
        print(f"  通过率: {passed / len(self.test_results) * 100:.1f}%" if self.test_results else "N/A")
        print(f"  总耗时: {(self.test_end_time - self.test_start_time).total_seconds():.2f}秒")


# ==================== 命令行接口 ====================

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='植物病害检测系统测试')
    parser.add_argument('--url', type=str, default=API_BASE_URL, help='API服务地址')
    parser.add_argument('--test', type=str, choices=['all', 'health', 'predict', 'perf', 'concurrent'],
                        default='concurrent', help='测试类型')
    parser.add_argument('--num', type=int, default=10, help='性能测试请求次数')
    parser.add_argument('--threads', type=int, default=10, help='并发测试线程数')

    args = parser.parse_args()

    tester = PlantDiseaseTester(api_base_url=args.url)

    if args.test == 'all':
        results = tester.run_all_tests()
        if results.get("success"):
            ColorPrint.success(f"测试完成！通过率: {results['passed_tests']}/{results['total_tests']}")
        else:
            ColorPrint.error(f"测试失败: {results.get('error')}")

    elif args.test == 'health':
        tester.test_health_check()

    elif args.test == 'predict':
        tester.test_predict_from_file()
        tester.test_predict_from_base64()

    elif args.test == 'perf':
        tester.test_performance(args.num)

    elif args.test == 'concurrent':
        tester.test_concurrent(args.threads)


if __name__ == '__main__':
    main()