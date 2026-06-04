# monitoring_api.py - 完整版
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from monitoring_db import monitoring_db
import logging
import traceback

logger = logging.getLogger(__name__)

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')


@monitoring_bp.route('/metrics', methods=['GET'])
@cross_origin()
def get_metrics():
    """获取监控指标汇总"""
    try:
        hours = request.args.get('hours', 24, type=int)

        # 获取API统计
        api_stats = monitoring_db.get_api_stats(hours)

        # 获取模型统计
        model_stats = monitoring_db.get_model_stats(hours)

        # 获取最近告警
        try:
            conn = monitoring_db._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT alert_level, alert_type, message, created_at 
                FROM alerts 
                WHERE created_at > datetime('now', ?)
                ORDER BY created_at DESC
                LIMIT 10
            ''', (f'-{hours} hours',))
            recent_alerts = cursor.fetchall()
            conn.close()
        except:
            recent_alerts = []

        # 格式化API统计
        api_summary = []
        total_requests = 0
        total_errors = 0

        for row in api_stats:
            if len(row) >= 6:
                endpoint = row[5]
                req_count = row[0] or 0
                err_count = row[4] or 0
                total_requests += req_count
                total_errors += err_count

                api_summary.append({
                    'endpoint': endpoint,
                    'total_requests': req_count,
                    'avg_response_time': round(row[1], 2) if row[1] else 0,
                    'max_response_time': round(row[2], 2) if row[2] else 0,
                    'min_response_time': round(row[3], 2) if row[3] else 0,
                    'error_count': err_count,
                    'error_rate': round(err_count / req_count * 100, 2) if req_count > 0 else 0
                })

        # 解析模型统计
        if model_stats and len(model_stats) >= 5:
            avg_inference = model_stats[0] or 0
            avg_total = model_stats[1] or 0
            max_inference = model_stats[2] or 0
            avg_detections = model_stats[3] or 0
            total_inferences = model_stats[4] or 0
        else:
            avg_inference = avg_total = max_inference = avg_detections = total_inferences = 0

        return jsonify({
            'success': True,
            'time_range': f'最近{hours}小时',
            'summary': {
                'total_requests': total_requests,
                'total_errors': total_errors,
                'error_rate': round(total_errors / total_requests * 100, 2) if total_requests > 0 else 0
            },
            'api_statistics': api_summary,
            'model_statistics': {
                'avg_inference_time': avg_inference,
                'avg_total_time': avg_total,
                'max_inference_time': max_inference,
                'avg_detections': avg_detections,
                'total_inferences': total_inferences
            },
            'recent_alerts': [{
                'level': a[0],
                'type': a[1],
                'message': a[2],
                'time': a[3]
            } for a in recent_alerts]
        })
    except Exception as e:
        logger.error(f"获取监控指标失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@monitoring_bp.route('/metrics/timeseries', methods=['GET'])
@cross_origin()
def get_timeseries_metrics():
    """获取时间序列数据"""
    try:
        hours = request.args.get('hours', 24, type=int)

        # 使用新方法获取时间序列数据
        api_trend = monitoring_db.get_timeseries_api(hours)
        model_trend = monitoring_db.get_timeseries_model(hours)

        return jsonify({
            'success': True,
            'api_trend': [{
                'time': row[0],
                'avg_response_time': row[1] if row[1] else 0,
                'request_count': row[2],
                'error_rate': row[3] if row[3] else 0
            } for row in api_trend],
            'model_trend': [{
                'time': row[0],
                'avg_inference_time': row[1] if row[1] else 0,
                'avg_total_time': row[2] if row[2] else 0,
                'inference_count': row[3]
            } for row in model_trend]
        })
    except Exception as e:
        logger.error(f"获取时间序列数据失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@monitoring_bp.route('/system', methods=['GET'])
@cross_origin()
def get_system_metrics():
    """获取最新系统资源指标"""
    try:
        result = monitoring_db.get_latest_system_metric()

        if result:
            return jsonify({
                'success': True,
                'current': {
                    'cpu_percent': result[0] or 0,
                    'memory_percent': result[1] or 0,
                    'memory_used_mb': round(result[2], 1) if result[2] else 0,
                    'gpu_utilization': result[3] or 0,
                    'gpu_memory_used_mb': round(result[4], 1) if result[4] else 0,
                    'recorded_at': result[5]
                }
            })
        else:
            return jsonify({'success': False, 'error': '暂无系统监控数据'})
    except Exception as e:
        logger.error(f"获取系统指标失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@monitoring_bp.route('/alerts', methods=['GET'])
@cross_origin()
def get_alerts():
    """获取告警列表"""
    try:
        limit = request.args.get('limit', 50, type=int)
        acknowledged = request.args.get('acknowledged', 'false').lower() == 'true'

        conn = monitoring_db._get_connection()
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alerts'")
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': True, 'alerts': []})

        cursor.execute('''
            SELECT id, alert_level, alert_type, message, metric_value, 
                   threshold, created_at, acknowledged
            FROM alerts 
            WHERE acknowledged = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (1 if acknowledged else 0, limit))

        results = cursor.fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'alerts': [{
                'id': r[0],
                'level': r[1],
                'type': r[2],
                'message': r[3],
                'metric_value': r[4],
                'threshold': r[5],
                'time': r[6],
                'acknowledged': bool(r[7])
            } for r in results]
        })
    except Exception as e:
        logger.error(f"获取告警失败: {str(e)}")
        return jsonify({'success': True, 'alerts': []})  # 返回空列表


@monitoring_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@cross_origin()
def acknowledge_alert(alert_id):
    """确认告警"""
    try:
        conn = monitoring_db._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE alerts SET acknowledged = 1 WHERE id = ?', (alert_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '已确认告警'})
    except Exception as e:
        logger.error(f"确认告警失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@monitoring_bp.route('/check-data', methods=['GET'])
@cross_origin()
def check_data():
    """检查监控数据库中是否有数据"""
    try:
        conn = monitoring_db._get_connection()
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]

        result = {}

        if 'api_metrics' in tables:
            cursor.execute("SELECT COUNT(*) FROM api_metrics")
            result['api_metrics_count'] = cursor.fetchone()[0]
        else:
            result['api_metrics_count'] = 0

        if 'model_metrics' in tables:
            cursor.execute("SELECT COUNT(*) FROM model_metrics")
            result['model_metrics_count'] = cursor.fetchone()[0]
        else:
            result['model_metrics_count'] = 0

        if 'system_metrics' in tables:
            cursor.execute("SELECT COUNT(*) FROM system_metrics")
            result['system_metrics_count'] = cursor.fetchone()[0]
        else:
            result['system_metrics_count'] = 0

        conn.close()

        result['has_data'] = result['api_metrics_count'] > 0 or result['model_metrics_count'] > 0

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500