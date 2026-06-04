# monitoring_db.py - 修复数据库连接问题
import sqlite3
import threading
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MonitoringDatabase:
    """监控数据库管理类"""

    def __init__(self, db_path='monitoring.db'):
        self.db_path = db_path
        self.lock = threading.Lock()  # 添加线程锁
        self.init_database()

    def init_database(self):
        """初始化监控数据库表结构"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # API请求监控表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    status_code INTEGER,
                    response_time REAL,
                    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    client_ip TEXT
                )
            ''')

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_endpoint ON api_metrics(endpoint)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_time ON api_metrics(request_time)')

            # 模型推理监控表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    decode_time REAL,
                    preprocess_time REAL,
                    inference_time REAL,
                    postprocess_time REAL,
                    total_time REAL,
                    num_detections INTEGER,
                    gpu_memory_used REAL,
                    detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 数据库查询监控表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS db_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    query_time REAL,
                    rows_returned INTEGER,
                    sql_text TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_db_type ON db_metrics(query_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_db_time ON db_metrics(executed_at)')

            # 系统资源监控表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_used_mb REAL,
                    gpu_utilization REAL,
                    gpu_memory_used_mb REAL,
                    disk_read_mb REAL,
                    disk_write_mb REAL,
                    network_recv_mb REAL,
                    network_sent_mb REAL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 告警记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_level TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metric_value REAL,
                    threshold REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged BOOLEAN DEFAULT 0
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("监控数据库初始化完成")
        except Exception as e:
            logger.error(f"初始化监控数据库失败: {e}")

    def _get_connection(self):
        """获取数据库连接 - 每次都创建新连接，避免关闭问题"""
        # 每次都创建新连接，不使用连接池或线程局部变量
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.execute('PRAGMA journal_mode=WAL')
        return conn

    def record_api_metric(self, request_id, endpoint, method, status_code, response_time, client_ip):
        """记录API请求指标"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO api_metrics 
                (request_id, endpoint, method, status_code, response_time, client_ip)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (request_id, endpoint, method, status_code, response_time, client_ip))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"记录API指标失败: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def record_model_metric(self, request_id, decode_time, preprocess_time,
                            inference_time, postprocess_time, total_time,
                            num_detections, gpu_memory_used=None):
        """记录模型推理指标"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO model_metrics 
                (request_id, decode_time, preprocess_time, inference_time, 
                 postprocess_time, total_time, num_detections, gpu_memory_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (request_id, decode_time, preprocess_time, inference_time,
                  postprocess_time, total_time, num_detections, gpu_memory_used))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"记录模型指标失败: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def record_db_metric(self, request_id, query_type, query_time, rows_returned, sql_text):
        """记录数据库查询指标"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO db_metrics 
                (request_id, query_type, query_time, rows_returned, sql_text)
                VALUES (?, ?, ?, ?, ?)
            ''', (request_id, query_type, query_time, rows_returned, sql_text[:500]))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"记录数据库指标失败: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def record_system_metric(self, metrics):
        """记录系统资源指标"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_metrics 
                (cpu_percent, memory_percent, memory_used_mb, gpu_utilization, 
                 gpu_memory_used_mb, disk_read_mb, disk_write_mb, network_recv_mb, network_sent_mb)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', metrics)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"记录系统指标失败: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def record_alert(self, alert_level, alert_type, message, metric_value=None, threshold=None):
        """记录告警"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (alert_level, alert_type, message, metric_value, threshold)
                VALUES (?, ?, ?, ?, ?)
            ''', (alert_level, alert_type, message, metric_value, threshold))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"记录告警失败: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_api_stats(self, hours=24):
        """获取API统计信息"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    IFNULL(ROUND(AVG(response_time), 2), 0) as avg_response_time,
                    IFNULL(ROUND(MAX(response_time), 2), 0) as max_response_time,
                    IFNULL(ROUND(MIN(response_time), 2), 0) as min_response_time,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
                    endpoint
                FROM api_metrics 
                WHERE request_time > datetime('now', ?)
                GROUP BY endpoint
            ''', (f'-{hours} hours',))

            results = cursor.fetchall()
            return results if results else []
        except Exception as e:
            logger.error(f"获取API统计失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_model_stats(self, hours=24):
        """获取模型推理统计信息"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 检查表是否有数据
            cursor.execute("SELECT COUNT(*) FROM model_metrics")
            count = cursor.fetchone()[0]

            if count == 0:
                return (0, 0, 0, 0, 0)

            cursor.execute('''
                SELECT 
                    IFNULL(ROUND(AVG(inference_time), 2), 0) as avg_inference_time,
                    IFNULL(ROUND(AVG(total_time), 2), 0) as avg_total_time,
                    IFNULL(ROUND(MAX(inference_time), 2), 0) as max_inference_time,
                    IFNULL(ROUND(AVG(num_detections), 2), 0) as avg_detections,
                    COUNT(*) as total_inferences
                FROM model_metrics 
                WHERE detection_time > datetime('now', ?)
            ''', (f'-{hours} hours',))

            result = cursor.fetchone()

            if result and result[0] is not None:
                return result
            return (0, 0, 0, 0, 0)
        except Exception as e:
            logger.error(f"获取模型统计失败: {e}")
            return (0, 0, 0, 0, 0)
        finally:
            if conn:
                conn.close()

    def get_timeseries_api(self, hours=24):
        """获取API时间序列数据"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', datetime(request_time, 'localtime')) as hour,
                    ROUND(AVG(response_time), 2) as avg_response_time,
                    COUNT(*) as request_count,
                    ROUND(AVG(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) * 100, 2) as error_rate
                FROM api_metrics 
                WHERE datetime(request_time) > datetime('now', ?)
                GROUP BY hour
                ORDER BY hour ASC
            ''', (f'-{hours} hours',))

            return cursor.fetchall()
        except Exception as e:
            logger.error(f"获取API时间序列失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_timeseries_model(self, hours=24):
        """获取模型时间序列数据"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', datetime(detection_time, 'localtime')) as hour,
                    ROUND(AVG(inference_time), 2) as avg_inference_time,
                    ROUND(AVG(total_time), 2) as avg_total_time,
                    COUNT(*) as inference_count
                FROM model_metrics 
                WHERE datetime(detection_time) > datetime('now', ?)
                GROUP BY hour
                ORDER BY hour ASC
            ''', (f'-{hours} hours',))

            return cursor.fetchall()
        except Exception as e:
            logger.error(f"获取模型时间序列失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_latest_system_metric(self):
        """获取最新系统指标"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT cpu_percent, memory_percent, memory_used_mb, 
                       gpu_utilization, gpu_memory_used_mb, recorded_at
                FROM system_metrics 
                ORDER BY recorded_at DESC 
                LIMIT 1
            ''')
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return None
        finally:
            if conn:
                conn.close()


# 创建全局监控数据库实例
monitoring_db = MonitoringDatabase()