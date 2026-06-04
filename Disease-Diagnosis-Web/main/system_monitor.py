# system_monitor.py - 修复GPU监控部分

import threading
import time
import psutil
import logging

logger = logging.getLogger(__name__)


class SystemMonitor:
    def __init__(self, interval=10):
        self.interval = interval
        self.running = False
        self.thread = None
        self._nvml_available = False
        self._init_nvml()

    def _init_nvml(self):
        """初始化NVML（NVIDIA管理库）"""
        try:
            import pynvml
            pynvml.nvmlInit()
            self._nvml = pynvml
            self._nvml_available = True
            logger.info("GPU监控已启用 (NVML初始化成功)")
        except ImportError:
            logger.warning("pynvml未安装，GPU监控不可用。安装: pip install pynvml")
        except Exception as e:
            logger.warning(f"NVML初始化失败: {e}，GPU监控不可用")

    def _get_gpu_metrics(self):
        """获取GPU指标"""
        if not self._nvml_available:
            return 0, 0

        try:
            # 获取第一个GPU
            handle = self._nvml.nvmlDeviceGetHandleByIndex(0)

            # 获取利用率
            util = self._nvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_util = util.gpu

            # 获取显存使用
            memory = self._nvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_memory_used = memory.used / 1024 / 1024  # 转换为MB

            return gpu_util, gpu_memory_used
        except Exception as e:
            logger.debug(f"获取GPU指标失败: {e}")
            return 0, 0

    def _collect_metrics(self):
        """采集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / 1024 / 1024

        # GPU指标
        gpu_util, gpu_memory_used = self._get_gpu_metrics()

        # 磁盘IO
        disk_io = psutil.disk_io_counters()
        disk_read_mb = disk_io.read_bytes / 1024 / 1024 if disk_io else 0
        disk_write_mb = disk_io.write_bytes / 1024 / 1024 if disk_io else 0

        # 网络IO
        net_io = psutil.net_io_counters()
        network_recv_mb = net_io.bytes_recv / 1024 / 1024 if net_io else 0
        network_sent_mb = net_io.bytes_sent / 1024 / 1024 if net_io else 0

        return (cpu_percent, memory_percent, memory_used_mb,
                gpu_util, gpu_memory_used,
                disk_read_mb, disk_write_mb,
                network_recv_mb, network_sent_mb)

    def start(self):
        """启动监控线程"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.thread.start()
        logger.info(
            f"系统资源监控已启动，采集间隔: {self.interval}秒，GPU监控: {'启用' if self._nvml_available else '禁用'}")

    def _collect_loop(self):
        """采集循环"""
        from monitoring_db import monitoring_db

        while self.running:
            try:
                metrics = self._collect_metrics()
                monitoring_db.record_system_metric(metrics)

                # 打印调试信息（可选）
                if metrics[3] > 0:  # 如果GPU使用率>0
                    logger.debug(f"GPU使用率: {metrics[3]}%, 显存: {metrics[4]:.0f}MB")

            except Exception as e:
                logger.error(f"采集系统指标失败: {e}")

            time.sleep(self.interval)

    def stop(self):
        """停止监控"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("系统资源监控已停止")


# 创建全局系统监控实例
system_monitor = SystemMonitor(interval=10)