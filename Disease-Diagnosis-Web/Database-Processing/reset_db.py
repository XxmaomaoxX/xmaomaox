# backend/reset_db.py
import sqlite3
import os


def reset_database():
    """完全重建数据库"""

    # 删除旧数据库
    if os.path.exists('diseases.db'):
        os.remove('diseases.db')
        print("✓ 已删除旧数据库")

    # 创建新数据库
    conn = sqlite3.connect('diseases.db')
    cursor = conn.cursor()

    # 创建表
    cursor.execute('''
        CREATE TABLE diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT UNIQUE NOT NULL,
            symptoms TEXT,
            environmental_causes TEXT,
            control_measures TEXT,
            prevention_methods TEXT,
            image_url TEXT,
            severity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE detection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT NOT NULL,
            confidence REAL,
            image_path TEXT,
            detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_feedback TEXT
        )
    ''')

    # 插入所有病害数据（根据你的模型类别）
    diseases = {
        # 苹果类
        'Apple Scab Leaf': {
            'symptoms': '叶片出现橄榄绿色至黑色圆形斑点，边缘模糊，叶片卷曲变形，严重时叶片提前脱落。',
            'environmental_causes': '高湿度环境，雨水多，温度15-20℃，通风不良的果园发病严重。',
            'control_measures': '喷洒世高、多菌灵、甲基托布津等杀菌剂，每7-10天喷一次，连喷2-3次。',
            'prevention_methods': '选用抗病品种，冬季清园，合理修剪保持通风透光，春季发芽前喷洒石硫合剂。',
            'severity': '严重'
        },
        'Apple leaf': {
            'symptoms': '健康叶片，颜色鲜绿，无病斑、无虫害、无畸形。',
            'environmental_causes': '生长环境适宜，无致病条件。',
            'control_measures': '继续保持良好管理，无需防治。',
            'prevention_methods': '加强日常管理，合理水肥，定期检查。',
            'severity': '健康'
        },
        'Apple rust leaf': {
            'symptoms': '叶片正面出现橙黄色圆形病斑，边缘红色，叶片背面产生黄褐色毛状物。',
            'environmental_causes': '温暖湿润气候，周围有桧柏类植物，春季多雨。',
            'control_measures': '喷洒三唑酮、戊唑醇等三唑类杀菌剂。',
            'prevention_methods': '避免在桧柏附近建园，春季萌芽前喷洒石硫合剂。',
            'severity': '中等'
        },

        # 辣椒类
        'Bell_pepper leaf': {
            'symptoms': '健康叶片，绿色正常，无病斑、无霉层。',
            'environmental_causes': '生长条件适宜。',
            'control_measures': '常规管理，预防为主。',
            'prevention_methods': '保持适宜温湿度，合理施肥，培育壮苗。',
            'severity': '健康'
        },
        'Bell_pepper leaf spot': {
            'symptoms': '叶片出现水渍状褐色小斑点，逐渐扩大为圆形病斑，边缘褐色，中央灰白色。',
            'environmental_causes': '高温高湿，温度25-30℃，相对湿度85%以上。',
            'control_measures': '喷洒代森锰锌、百菌清、苯醚甲环唑等药剂。',
            'prevention_methods': '合理密植，加强通风透光，实行轮作。',
            'severity': '中等'
        },

        # 蓝莓
        'Blueberry leaf': {
            'symptoms': '健康蓝莓叶片，绿色正常，无斑点。',
            'environmental_causes': '酸性土壤环境适宜。',
            'control_measures': '常规管理。',
            'prevention_methods': '保持土壤酸性，适当遮荫，定期施肥。',
            'severity': '健康'
        },

        # 樱桃
        'Cherry leaf': {
            'symptoms': '健康樱桃叶片，绿色有光泽，无病斑。',
            'environmental_causes': '温带气候，排水良好。',
            'control_measures': '常规管理。',
            'prevention_methods': '冬季清园，合理修剪，平衡施肥。',
            'severity': '健康'
        },

        # 玉米类
        'Corn Gray leaf spot': {
            'symptoms': '叶片出现灰褐色长形病斑，边缘褐色，病斑平行于叶脉。',
            'environmental_causes': '高温高湿，田间郁蔽，氮肥过多。',
            'control_measures': '喷洒吡唑醚菌酯、苯醚甲环唑、嘧菌酯等。',
            'prevention_methods': '种植抗病品种，合理轮作，平衡施肥。',
            'severity': '中等'
        },
        'Corn leaf blight': {
            'symptoms': '叶片出现椭圆形病斑，黄褐色，边缘有晕圈。',
            'environmental_causes': '温暖潮湿，连阴雨，低洼积水。',
            'control_measures': '喷洒多菌灵、甲基硫菌灵、戊唑醇。',
            'prevention_methods': '种植抗病品种，轮作倒茬，增施有机肥。',
            'severity': '严重'
        },
        'Corn rust leaf': {
            'symptoms': '叶片产生黄褐色夏孢子堆，表皮破裂散出锈褐色粉末。',
            'environmental_causes': '温度16-23℃，相对湿度95%以上。',
            'control_measures': '喷洒戊唑醇、吡唑醚菌酯、三唑酮。',
            'prevention_methods': '合理密植，平衡施肥，及时排水降湿。',
            'severity': '中等'
        },

        # 葡萄类
        'grape leaf': {
            'symptoms': '健康葡萄叶片，绿色，无病斑。',
            'environmental_causes': '温暖干燥气候。',
            'control_measures': '常规管理。',
            'prevention_methods': '冬季修剪，萌芽前喷石硫合剂，套袋。',
            'severity': '健康'
        },
        'grape leaf black rot': {
            'symptoms': '叶片出现红褐色圆形病斑，边缘黑色，果实变黑干枯。',
            'environmental_causes': '多雨潮湿，温度24-27℃，通风不良。',
            'control_measures': '喷洒波尔多液、代森锰锌、戊唑醇，套袋保护。',
            'prevention_methods': '冬季清园，加强水肥管理，注意排水。',
            'severity': '严重'
        },

        # 马铃薯类
        'Potato leaf': {
            'symptoms': '健康马铃薯叶片，绿色，无病斑。',
            'environmental_causes': '凉爽气候，排水良好。',
            'control_measures': '常规管理。',
            'prevention_methods': '选用无病种薯，轮作倒茬，及时培土。',
            'severity': '健康'
        },
        'Potato leaf early blight': {
            'symptoms': '叶片出现褐色同心轮纹病斑，边缘黄色，块茎表面凹陷斑。',
            'environmental_causes': '温暖潮湿，连续阴雨，土壤带菌。',
            'control_measures': '喷洒异菌脲、百菌清、代森锰锌。',
            'prevention_methods': '选用无病种薯，轮作3年以上，增施钾肥。',
            'severity': '中等'
        },
        'Potato leaf late blight': {
            'symptoms': '叶片出现水渍状暗绿色病斑，潮湿时产生白色霉层，块茎腐烂。',
            'environmental_causes': '冷凉高湿，连续阴雨，低洼积水。',
            'control_measures': '喷洒甲霜灵、霜脲氰、烯酰吗啉。',
            'prevention_methods': '选用脱毒种薯，轮作4年以上，高培土。',
            'severity': '严重'
        },

        # 桃
        'Peach leaf': {
            'symptoms': '健康桃树叶片，绿色，无病斑。',
            'environmental_causes': '温暖气候，沙壤土。',
            'control_measures': '常规管理。',
            'prevention_methods': '冬季修剪，萌芽前喷石硫合剂，防治蚜虫。',
            'severity': '健康'
        },

        # 树莓
        'Raspberry leaf': {
            'symptoms': '健康树莓叶片，绿色，无病斑。',
            'environmental_causes': '凉爽气候，湿润排水良好。',
            'control_measures': '常规管理。',
            'prevention_methods': '保持土壤湿润，夏季遮荫，及时修剪。',
            'severity': '健康'
        },

        # 大豆类
        'Soyabean leaf': {
            'symptoms': '健康大豆叶片，绿色，无病斑。',
            'environmental_causes': '温暖气候，排水良好。',
            'control_measures': '常规管理。',
            'prevention_methods': '合理轮作，平衡施肥，及时排灌。',
            'severity': '健康'
        },
        'Soybean leaf': {
            'symptoms': '健康大豆叶片，绿色，无病虫害。',
            'environmental_causes': '生长环境适宜。',
            'control_measures': '常规管理。',
            'prevention_methods': '轮作倒茬，种子处理，合理密植。',
            'severity': '健康'
        },

        # 草莓
        'Strawberry leaf': {
            'symptoms': '健康草莓叶片，绿色，无病斑。',
            'environmental_causes': '凉爽气候，湿润环境。',
            'control_measures': '常规管理。',
            'prevention_methods': '保持土壤湿润，覆盖地膜，及时去除老叶。',
            'severity': '健康'
        },

        # 番茄类
        'Tomato leaf': {
            'symptoms': '健康番茄叶片，绿色，生长健壮。',
            'environmental_causes': '温暖气候，光照充足。',
            'control_measures': '常规管理。',
            'prevention_methods': '培育壮苗，合理密植，整枝打杈。',
            'severity': '健康'
        },
        'Tomato Early blight leaf': {
            'symptoms': '下部叶片出现褐色同心轮纹病斑，边缘黄色，茎部病斑凹陷。',
            'environmental_causes': '温暖潮湿，土壤带菌，植株老化。',
            'control_measures': '喷洒异菌脲、百菌清、苯醚甲环唑，及时摘除病叶。',
            'prevention_methods': '种子消毒，轮作3年以上，高畦栽培。',
            'severity': '中等'
        },
        'Tomato Septoria leaf spot': {
            'symptoms': '叶片出现灰白色圆形病斑，边缘深褐色，病斑上有小黑点。',
            'environmental_causes': '温暖潮湿，高湿多雨，田间郁蔽。',
            'control_measures': '喷洒百菌清、代森锰锌、嘧菌酯。',
            'prevention_methods': '实行轮作，合理密植，加强通风。',
            'severity': '中等'
        },
        'Tomato leaf bacterial spot': {
            'symptoms': '叶片出现水渍状小斑点，逐渐扩大为暗褐色病斑，边缘黄色晕圈，病斑破裂呈穿孔状。',
            'environmental_causes': '高温高湿（25-30℃），雨水飞溅传播，植株伤口多，氮肥过多。',
            'control_measures': '1. 喷洒铜制剂（氢氧化铜、噻菌铜、波尔多液）；2. 喷洒抗生素（春雷霉素、中生菌素）；3. 及时清除病叶病株。',
            'prevention_methods': '1. 选用无病种子或55℃温水浸种15分钟；2. 与非茄科作物轮作2年以上；3. 高畦栽培，避免积水；4. 减少伤口；5. 平衡施肥，避免偏施氮肥。',
            'severity': '中等'
        },
        'Tomato leaf late blight': {
            'symptoms': '叶片出现水渍状暗绿色病斑，潮湿时产生白色霉层，果实凹陷斑。',
            'environmental_causes': '冷凉高湿，连续阴雨，通风不良。',
            'control_measures': '喷洒甲霜灵锰锌、霜脲氰、烯酰吗啉。',
            'prevention_methods': '选用抗病品种，与非茄科作物轮作，控制湿度。',
            'severity': '严重'
        },
        'Tomato leaf mosaic virus': {
            'symptoms': '叶片出现黄绿相间的花叶症状，皱缩畸形，植株矮化。',
            'environmental_causes': '病毒引起，通过汁液摩擦、蚜虫传播。',
            'control_measures': '喷洒抗病毒剂如病毒A、宁南霉素，控制蚜虫。',
            'prevention_methods': '选用抗病品种，种子消毒，防治蚜虫。',
            'severity': '严重'
        },
        'Tomato leaf yellow virus': {
            'symptoms': '叶片黄化卷曲，植株矮化，叶片变厚变脆。',
            'environmental_causes': '由烟粉虱传播的双生病毒引起。',
            'control_measures': '防治烟粉虱，喷洒吡虫啉、啶虫脒，使用黄板诱杀。',
            'prevention_methods': '选用抗病品种，覆盖防虫网，及时拔除病株。',
            'severity': '严重'
        },
        'Tomato mold leaf': {
            'symptoms': '叶片出现灰褐色霉层，病部软化腐烂。',
            'environmental_causes': '低温高湿，相对湿度90%以上，通风不良。',
            'control_measures': '喷洒异菌脲、腐霉利、嘧霉胺，降低湿度。',
            'prevention_methods': '控制温湿度，及时摘除病叶病果。',
            'severity': '中等'
        },

        # 瓜类
        'Squash Powdery mildew leaf': {
            'symptoms': '叶片表面出现白色粉状霉斑，逐渐覆盖整个叶片。',
            'environmental_causes': '温暖干燥，昼夜温差大，通风不良。',
            'control_measures': '喷洒三唑酮、醚菌酯、戊唑醇。',
            'prevention_methods': '合理密植，加强通风透光，平衡施肥。',
            'severity': '中等'
        }
    }

    # 插入数据
    inserted = 0
    for name, info in diseases.items():
        try:
            cursor.execute('''
                INSERT INTO diseases 
                (disease_name, symptoms, environmental_causes, control_measures, 
                 prevention_methods, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, info['symptoms'], info['environmental_causes'],
                  info['control_measures'], info['prevention_methods'], info['severity']))
            inserted += 1
            print(f"✓ 已添加: {name}")
        except Exception as e:
            print(f"✗ 添加失败 {name}: {e}")

    conn.commit()
    conn.close()

    print(f"\n数据库重建完成！共添加 {inserted} 条病害数据")

    # 验证
    print("\n验证数据库:")
    conn = sqlite3.connect('diseases.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM diseases")
    count = cursor.fetchone()[0]
    print(f"总记录数: {count}")

    # 检查 Tomato leaf bacterial spot
    cursor.execute("SELECT disease_name, severity FROM diseases WHERE disease_name='Tomato leaf bacterial spot'")
    result = cursor.fetchone()
    if result:
        print(f"✓ 找到: {result[0]} ({result[1]})")
    else:
        print("✗ 未找到 Tomato leaf bacterial spot")

    conn.close()


if __name__ == '__main__':
    reset_database()