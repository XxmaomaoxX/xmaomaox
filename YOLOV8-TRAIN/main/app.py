# app.py - 集成数据库的完整版本
import torch
import torch.serialization

# 修复 PyTorch 2.6+ 兼容性问题
_original_torch_load = torch.load


def _patched_torch_load(f, map_location=None, pickle_module=None, **kwargs):
    # 强制设置 weights_only=False 以兼容旧版模型
    kwargs['weights_only'] = False
    return _original_torch_load(f, map_location=map_location,
                                pickle_module=pickle_module, **kwargs)


torch.load = _patched_torch_load

# 添加 Ultralytics 模型类到安全列表
try:
    from ultralytics.nn.tasks import DetectionModel

    torch.serialization.add_safe_globals([DetectionModel])
    print("✅ 已添加 DetectionModel 到安全全局列表")
except ImportError as e:
    print(f"⚠️ 无法导入 DetectionModel: {e}")
except Exception as e:
    print(f"⚠️ 添加安全全局类时出错: {e}")

print("✅ PyTorch load 补丁已应用")
# ====================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
import base64
import os
import logging
from datetime import datetime
import time
from flask import g, request
from monitoring_db import monitoring_db
from monitoring_decorators import monitor_api, get_request_id, monitor_model
from monitoring_api import monitoring_bp
from system_monitor import system_monitor

# 导入数据库模块
from database import db

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# 配置CORS，允许前端跨域访问
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ========== 添加监控相关配置 ==========
# 注册监控API蓝图
app.register_blueprint(monitoring_bp)

# 请求预处理 - 为每个请求生成ID
@app.before_request
def before_request():
    print(f"[DEBUG] before_request 被调用: {request.path}")  # 添加这行
    g.start_time = time.time()
    g.request_id = get_request_id()
    print(f"[DEBUG] 生成的请求ID: {g.request_id}")  # 添加这行

# 请求后处理 - 记录请求完成（可选）
@app.after_request
def after_request(response):
    # 可选：添加请求ID到响应头
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
    return response

# 全局模型变量
model = None


def load_model():
    """加载YOLO模型（单例模式）"""
    global model
    if model is None:
        # 检查GPU是否可用
        print(f"CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU设备: {torch.cuda.get_device_name(0)}")
            print(f"GPU数量: {torch.cuda.device_count()}")

        model_path = r'E:\YOLOV8-TRAIN\detect-model\weights\best.pt'  # 修改为你的模型路径
        if not os.path.exists(model_path):
            logger.warning(f"模型文件不存在: {model_path}，使用默认模型")
            model_path = 'yolov8n.pt'  # 备用模型
        logger.info(f"正在加载模型: {model_path}")
        model = YOLO(model_path)
        logger.info("模型加载完成")

        # 检查模型是否在GPU上
        if torch.cuda.is_available():
            # 尝试将模型移到GPU
            model.to('cuda')
            print("模型已加载到GPU")
        else:
            print("模型在CPU上运行")

    return model

# 添加模型调用封装函数
@monitor_model
def call_model_inference(img):
    """封装模型调用，用于性能监控"""
    return model(img)

@app.route('/api/health', methods=['GET'])
@monitor_api
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None,
        'database': 'connected'
    })


@app.route('/api/model/info', methods=['GET'])
@monitor_api
def get_model_info():
    """获取模型信息"""
    try:
        model = load_model()
        return jsonify({
            'success': True,
            'model_type': 'YOLOv8',
            'num_classes': len(model.names),
            'class_names': list(model.names.values())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/diseases', methods=['GET'])
@monitor_api
def get_all_diseases():
    """获取所有病害列表"""
    try:
        diseases = db.get_all_diseases()
        return jsonify({
            'success': True,
            'diseases': diseases
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/disease/<name>', methods=['GET'])
@monitor_api
def get_disease_detail(name):
    """获取特定病害的详细信息"""
    try:
        disease_info = db.get_disease_info(name)
        if disease_info:
            return jsonify({
                'success': True,
                'disease_info': disease_info
            })
        else:
            return jsonify({
                'success': False,
                'error': f'未找到病害: {name}'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
@monitor_api
def get_history():
    """获取检测历史"""
    try:
        history = db.get_detection_history(20)
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/predict', methods=['POST'])
@monitor_api
def predict():
    """
    目标检测接口（集成数据库）
    支持两种输入方式：
    1. 文件上传: multipart/form-data with field 'image'
    2. Base64: application/json with field 'image_base64'
    """
    # 记录请求开始
    request_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
    logger.info(f"[{request_id}] 收到检测请求")

    try:
        # 加载模型
        model = load_model()

        # 解析图片数据
        img = None

        # 方式1：从文件上传获取
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': '未选择文件'
                }), 400

            # 读取文件
            file_bytes = file.read()
            nparr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            logger.info(f"[{request_id}] 接收文件: {file.filename}, 大小: {len(file_bytes)} bytes")

        # 方式2：从Base64获取
        elif request.is_json and 'image_base64' in request.json:
            base64_str = request.json['image_base64']
            # 移除data:image前缀（如果存在）
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]

            img_bytes = base64.b64decode(base64_str)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            logger.info(f"[{request_id}] 接收Base64图片，大小: {len(img_bytes)} bytes")

        else:
            return jsonify({
                'success': False,
                'error': '请提供图片文件或Base64数据'
            }), 400

        # 检查图片是否有效
        if img is None:
            return jsonify({
                'success': False,
                'error': '无效的图片数据'
            }), 400

        # 执行预测
        logger.info(f"[{request_id}] 开始预测...")
        results = call_model_inference(img)

        # 解析检测结果并查询数据库
        detections = []
        if results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                # 获取检测信息
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                disease_name = model.names[cls_id]

                # 获取边界框坐标 (xyxy格式)
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # 从数据库查询病害详细信息
                logger.info(f"查询病害: {disease_name}")
                disease_info = db.get_disease_info(disease_name)

                detection = {
                    'class_id': cls_id,
                    'class_name': disease_name,
                    'confidence': round(confidence, 3),
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)],
                    'width': int(x2 - x1),
                    'height': int(y2 - y1)
                }

                # 添加数据库信息（如果存在）
                if disease_info:
                    detection['disease_info'] = disease_info
                    logger.info(f"✓ 找到数据库信息: {disease_name}")
                    # 保存检测历史
                    db.add_detection_history(disease_name, confidence)
                else:
                    detection['disease_info'] = None
                    logger.warning(f"✗ 未找到数据库信息: {disease_name}")

                detections.append(detection)

        # 生成带标注的图片（Base64格式）
        annotated_img = results[0].plot()
        _, buffer = cv2.imencode('.jpg', annotated_img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')

        # 统计信息
        logger.info(f"[{request_id}] 检测完成，找到 {len(detections)} 个目标")

        # 返回结果
        return jsonify({
            'success': True,
            'request_id': request_id,
            'detections': detections,
            'count': len(detections),
            'image_size': {
                'width': img.shape[1],
                'height': img.shape[0]
            },
            'annotated_image': f'data:image/jpeg;base64,{annotated_base64}',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"[{request_id}] 预测失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'request_id': request_id
        }), 500

@app.route('/api/predict/batch', methods=['POST'])
@monitor_api
def predict_batch():
    """
    批量检测接口（集成数据库）
    接收多张图片，返回批量结果
    """
    request_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
    logger.info(f"[{request_id}] 收到批量检测请求")

    try:
        model = load_model()

        # 检查是否有文件
        if 'images' not in request.files:
            return jsonify({
                'success': False,
                'error': '请提供图片文件'
            }), 400

        files = request.files.getlist('images')
        if len(files) == 0:
            return jsonify({
                'success': False,
                'error': '未选择文件'
            }), 400

        results_list = []
        for idx, file in enumerate(files):
            if file.filename == '':
                continue

            # 读取图片
            file_bytes = file.read()
            nparr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                continue

            # 预测
            results = model(img)

            # 解析结果
            detections = []
            if results[0].boxes is not None:
                for box in results[0].boxes:
                    disease_name = model.names[int(box.cls[0])]
                    confidence = float(box.conf[0])

                    # 查询数据库信息
                    disease_info = db.get_disease_info(disease_name)

                    detection = {
                        'class_name': disease_name,
                        'confidence': round(confidence, 3),
                        'bbox': box.xyxy[0].tolist()
                    }

                    if disease_info:
                        detection['disease_info'] = {
                            'symptoms': disease_info['symptoms'],
                            'environmental_causes': disease_info['environmental_causes'],
                            'control_measures': disease_info['control_measures'],
                            'prevention_methods': disease_info['prevention_methods'],
                            'severity': disease_info['severity']
                        }

                    detections.append(detection)

            results_list.append({
                'filename': file.filename,
                'detections': detections,
                'count': len(detections)
            })

        logger.info(f"[{request_id}] 批量检测完成，处理 {len(results_list)} 张图片")

        return jsonify({
            'success': True,
            'request_id': request_id,
            'total_images': len(results_list),
            'results': results_list,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"[{request_id}] 批量检测失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
@monitor_api
def upload_and_predict():
    """
    上传并检测接口（保存文件版本）
    会将上传的文件保存到服务器，并返回结果
    """
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '未提供图片'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': '未选择文件'}), 400

        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 加载模型并预测
        model = load_model()
        results = model(filepath)

        # 解析结果并查询数据库
        detections = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                disease_name = model.names[int(box.cls[0])]
                confidence = float(box.conf[0])

                # 查询数据库
                disease_info = db.get_disease_info(disease_name)

                detection = {
                    'class_name': disease_name,
                    'confidence': round(confidence, 3),
                    'bbox': box.xyxy[0].tolist()
                }

                if disease_info:
                    detection['disease_info'] = disease_info
                    db.add_detection_history(disease_name, confidence, filepath)

                detections.append(detection)

        # 保存标注图
        annotated = results[0].plot()
        annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], f"annotated_{filename}")
        cv2.imwrite(annotated_path, annotated)

        return jsonify({
            'success': True,
            'filename': filename,
            'annotated_filename': f"annotated_{filename}",
            'detections': detections,
            'count': len(detections)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/diseases/add', methods=['POST'])
@monitor_api
def add_disease():
    """添加新的病害信息"""
    try:
        data = request.json
        success = db.add_disease(
            name=data.get('name'),
            symptoms=data.get('symptoms'),
            environmental_causes=data.get('environmental_causes'),
            control_measures=data.get('control_measures'),
            prevention_methods=data.get('prevention_methods'),
            severity=data.get('severity', '一般')
        )

        if success:
            return jsonify({'success': True, 'message': '添加成功'})
        else:
            return jsonify({'success': False, 'error': '添加失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # 启动系统资源监控（在后台线程中运行）
    system_monitor.start()

    # 预加载模型
    load_model()

    import atexit
    @atexit.register
    def shutdown_monitor():
        system_monitor.stop()

    # 启动服务
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )