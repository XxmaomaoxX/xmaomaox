# backend/init_db.py
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """初始化数据库并插入所有病害数据"""

    conn = sqlite3.connect('diseases.db')
    cursor = conn.cursor()

    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diseases (
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
        CREATE TABLE IF NOT EXISTS detection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT NOT NULL,
            confidence REAL,
            image_path TEXT,
            detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_feedback TEXT
        )
    ''')

    # 病害数据字典
    diseases_data = {
        # 苹果病害
        'Apple Scab Leaf': {
            'symptoms': '叶片出现橄榄绿色至黑色圆形斑点，边缘模糊，病斑表面有绒毛状霉层。叶片卷曲变形，严重时叶片提前脱落，果实表面也出现黑色凹陷斑。',
            'environmental_causes': '高湿度环境，雨水多，温度15-20℃时最易发病。春季多雨年份发病严重，通风不良、树势衰弱的果园发病重。',
            'control_measures': '1. 喷洒杀菌剂：世高、多菌灵、甲基托布津等，每7-10天喷一次，连喷2-3次；2. 清除病叶病果，减少侵染源；3. 修剪过密枝条，改善通风透光。',
            'prevention_methods': '1. 选用抗病品种；2. 冬季清园彻底清除病落叶；3. 合理修剪保持通风透光；4. 春季发芽前喷洒石硫合剂；5. 平衡施肥，增强树势。',
            'severity': '严重'
        },
        'Apple Rust Leaf': {
            'symptoms': '叶片正面出现橙黄色圆形病斑，边缘红色，病斑上有黑色小点（性孢子器）。叶片背面产生黄褐色毛状物（锈孢子器），严重时叶片早落。',
            'environmental_causes': '温暖湿润气候，果园周围5公里内有桧柏类植物（转主寄主）。春季多雨，温度15-20℃最适宜发病。',
            'control_measures': '1. 喷洒三唑酮、戊唑醇等三唑类杀菌剂；2. 砍除果园周围5公里内的桧柏类植物；3. 发现病叶及时摘除销毁。',
            'prevention_methods': '1. 避免在桧柏附近建园；2. 春季萌芽前喷洒石硫合剂；3. 选用抗病品种；4. 加强栽培管理，提高抗病力。',
            'severity': '中等'
        },

        # 辣椒病害
        'Bell_pepper leaf spot': {
            'symptoms': '叶片出现水渍状褐色小斑点，逐渐扩大为圆形或不规则形病斑，边缘褐色，中央灰白色，病斑上有小黑点。严重时叶片枯黄脱落。',
            'environmental_causes': '高温高湿条件，温度25-30℃，相对湿度85%以上。田间郁蔽、排水不良、连作地块发病重。',
            'control_measures': '1. 喷洒代森锰锌、百菌清、苯醚甲环唑等药剂；2. 交替使用防止抗性；3. 发病初期及时防治；4. 清除病叶。',
            'prevention_methods': '1. 选用抗病品种；2. 合理密植，加强通风透光；3. 实行轮作，避免连作；4. 高畦栽培，避免积水。',
            'severity': '中等'
        },

        # 玉米病害
        'Corn Gray leaf spot': {
            'symptoms': '叶片出现灰褐色长形病斑，边缘褐色或紫色，病斑平行于叶脉。后期病斑融合导致叶片干枯，严重时整株枯死。',
            'environmental_causes': '高温高湿环境（25-30℃），田间郁蔽，连作地块，氮肥施用过多，植株密度过大。',
            'control_measures': '1. 喷洒吡唑醚菌酯、苯醚甲环唑、嘧菌酯等杀菌剂；2. 发病初期及时防治；3. 清除病残体。',
            'prevention_methods': '1. 种植抗病品种；2. 合理轮作；3. 平衡施肥，增施磷钾肥；4. 收获后清除病残体；5. 合理密植。',
            'severity': '中等'
        },
        'Corn leaf blight': {
            'symptoms': '叶片出现椭圆形或长条形病斑，黄褐色至灰褐色，病斑边缘有晕圈。严重时叶片枯萎，影响灌浆，减产严重。',
            'environmental_causes': '温暖潮湿条件，温度20-25℃。连阴雨天气，低洼积水地块，种植密度过大，通风不良。',
            'control_measures': '1. 喷洒多菌灵、甲基硫菌灵、戊唑醇等杀菌剂；2. 病株率达10%时开始防治；3. 清除田间病残体。',
            'prevention_methods': '1. 种植抗病品种；2. 轮作倒茬；3. 加强田间管理；4. 增施有机肥，提高植株抗病力。',
            'severity': '严重'
        },
        'Corn rust leaf': {
            'symptoms': '叶片两面产生黄褐色至暗褐色夏孢子堆，圆形或椭圆形，散生或聚生。表皮破裂散出锈褐色粉末，严重时叶片干枯。',
            'environmental_causes': '温度16-23℃，相对湿度95%以上。田间郁蔽，氮肥过量，通风不良，连作地块。',
            'control_measures': '1. 喷洒戊唑醇、吡唑醚菌酯、三唑酮等药剂；2. 注意药剂轮换使用；3. 发病初期防治效果最好。',
            'prevention_methods': '1. 选用抗病品种；2. 合理密植；3. 平衡施肥，避免偏施氮肥；4. 及时排水降湿。',
            'severity': '中等'
        },

        # 葡萄病害
        'grape leaf black rot': {
            'symptoms': '叶片出现红褐色圆形病斑，边缘黑色，病斑上有小黑点（分生孢子器）。果实变黑干枯成僵果，表面布满小黑点。',
            'environmental_causes': '多雨潮湿天气，温度24-27℃。果园通风不良，排水不畅，架面郁蔽，管理粗放。',
            'control_measures': '1. 喷洒波尔多液、代森锰锌、戊唑醇等；2. 坐果后开始防治，7-10天一次；3. 套袋保护果穗；4. 剪除病枝病果。',
            'prevention_methods': '1. 冬季清园，剪除病枝病果；2. 加强水肥管理；3. 果实套袋；4. 注意果园排水；5. 改善通风透光。',
            'severity': '严重'
        },

        # 番茄病害
        'Tomato Early blight leaf': {
            'symptoms': '下部叶片先发病，出现褐色同心轮纹病斑，边缘黄色。茎部病斑凹陷，果实蒂部腐烂，病斑上有黑色霉层。',
            'environmental_causes': '温暖潮湿，温度20-25℃，相对湿度70%以上。土壤带菌，植株老化，缺肥，管理粗放。',
            'control_measures': '1. 喷洒异菌脲、百菌清、苯醚甲环唑；2. 及时摘除病叶病果；3. 收获后彻底清园；4. 发病初期用药。',
            'prevention_methods': '1. 种子消毒；2. 与非茄科作物轮作3年以上；3. 高畦栽培，避免田间积水；4. 增施磷钾肥。',
            'severity': '中等'
        },
        'Tomato Septoria leaf spot': {
            'symptoms': '叶片出现灰白色圆形病斑，边缘深褐色，病斑上有小黑点。严重时叶片枯黄脱落，下部叶片先发病。',
            'environmental_causes': '温暖潮湿环境，温度22-28℃。高湿多雨，田间郁蔽，排水不良，连作地块。',
            'control_measures': '1. 喷洒百菌清、代森锰锌、嘧菌酯等杀菌剂；2. 7-10天一次，连喷2-3次；3. 清除病叶。',
            'prevention_methods': '1. 实行轮作，避免连作；2. 合理密植，加强通风透光；3. 发现病叶及时摘除；4. 种子消毒。',
            'severity': '中等'
        },
        'Tomato leaf bacterial spot': {
            'symptoms': '叶片出现水渍状小斑点，逐渐扩大为暗褐色病斑，边缘黄色晕圈。病斑破裂呈穿孔状，严重时叶片干枯。',
            'environmental_causes': '高温高湿，温度25-30℃。雨水飞溅传播，田间郁蔽，伤口多，氮肥过多。',
            'control_measures': '1. 喷洒铜制剂（氢氧化铜、噻菌铜）；2. 抗生素类药剂（春雷霉素、中生菌素）；3. 及时清除病叶。',
            'prevention_methods': '1. 选用无病种子；2. 轮作2年以上；3. 避免田间积水；4. 减少伤口；5. 平衡施肥。',
            'severity': '中等'
        },
        'Tomato leaf late blight': {
            'symptoms': '叶片和茎部出现水渍状暗绿色病斑，潮湿时产生白色霉层。果实出现油渍状暗褐色凹陷斑，软腐。',
            'environmental_causes': '冷凉高湿（18-22℃），连续阴雨，雾大露重。保护地通风不良，低洼积水地块。',
            'control_measures': '1. 喷洒甲霜灵锰锌、霜脲氰、烯酰吗啉；2. 注意药剂的交替使用；3. 发现中心病株立即拔除。',
            'prevention_methods': '1. 选用抗病品种；2. 与非茄科作物轮作；3. 控制湿度，加强通风；4. 及时清除中心病株。',
            'severity': '严重'
        },
        'Tomato leaf mosaic virus': {
            'symptoms': '叶片出现黄绿相间的花叶症状，叶片皱缩畸形，植株矮化。果实变小，表面斑驳，品质下降。',
            'environmental_causes': '由病毒引起，通过汁液摩擦、蚜虫传播。高温干旱条件利于发病，种子带毒。',
            'control_measures': '1. 喷洒抗病毒剂如病毒A、宁南霉素、香菇多糖；2. 控制蚜虫传播；3. 拔除病株。',
            'prevention_methods': '1. 选用抗病品种；2. 种子消毒（磷酸三钠处理）；3. 防治蚜虫；4. 田间操作时避免接触传染。',
            'severity': '严重'
        },
        'Tomato leaf yellow virus': {
            'symptoms': '叶片黄化卷曲，植株矮化，叶片变厚变脆，叶脉间黄化。果实小且少，品质严重下降。',
            'environmental_causes': '由烟粉虱传播的双生病毒引起。高温干旱条件利于烟粉虱繁殖，保护地发生严重。',
            'control_measures': '1. 重点防治烟粉虱；2. 喷洒吡虫啉、啶虫脒等杀虫剂；3. 使用黄板诱杀；4. 拔除病株。',
            'prevention_methods': '1. 选用抗病品种；2. 培育无病虫苗；3. 覆盖防虫网；4. 及时防治烟粉虱。',
            'severity': '严重'
        },
        'Tomato mold leaf': {
            'symptoms': '叶片出现灰褐色霉层，病部软化腐烂。果实染病产生灰色霉层，尤其在潮湿条件下严重。',
            'environmental_causes': '低温高湿（18-23℃），相对湿度90%以上。保护地通风不良，光照不足，伤口多。',
            'control_measures': '1. 喷洒异菌脲、腐霉利、嘧霉胺等药剂；2. 降低湿度，加强通风；3. 及时摘除病叶病果。',
            'prevention_methods': '1. 控制温湿度；2. 避免浇水过多；3. 及时摘除病叶病果；4. 施药后通风降湿。',
            'severity': '中等'
        },

        # 马铃薯病害
        'Potato leaf early blight': {
            'symptoms': '叶片出现褐色同心轮纹病斑，边缘黄色，病斑上有黑色霉层。茎部病斑凹陷，块茎表面出现暗褐色凹陷斑。',
            'environmental_causes': '温暖潮湿，温度20-25℃。连续阴雨，土壤带菌，植株生长衰弱，缺肥。',
            'control_measures': '1. 喷洒异菌脲、百菌清、代森锰锌；2. 发病初期开始防治；3. 收获前两周停止用药。',
            'prevention_methods': '1. 选用无病种薯；2. 轮作3年以上；3. 加强栽培管理；4. 增施钾肥，提高抗病力。',
            'severity': '中等'
        },
        'Potato leaf late blight': {
            'symptoms': '叶片出现水渍状暗绿色病斑，潮湿时产生白色霉层。茎部黑褐色腐烂，块茎表面褐色凹陷斑，内部薯肉褐变。',
            'environmental_causes': '冷凉高湿（18-22℃），连续阴雨天气，雾露重。低洼积水地块，种植感病品种。',
            'control_measures': '1. 喷洒甲霜灵、霜脲氰、烯酰吗啉等药剂；2. 发现中心病株立即拔除并喷洒药剂；3. 及时培土。',
            'prevention_methods': '1. 选用脱毒种薯；2. 轮作4年以上；3. 控制氮肥用量；4. 高培土；5. 收获前割秧晒地。',
            'severity': '严重'
        },

        # 瓜类病害
        'Squash Powdery mildew leaf': {
            'symptoms': '叶片表面出现白色粉状霉斑，逐渐扩大覆盖整个叶片。叶片黄化枯萎，叶背面也有白色粉状物，后期变灰褐色。',
            'environmental_causes': '温暖干燥（20-25℃），昼夜温差大。田间郁蔽，通风不良，氮肥过多，光照不足。',
            'control_measures': '1. 喷洒三唑酮、醚菌酯、戊唑醇、硫磺悬浮剂；2. 注意喷洒叶片正反面；3. 发病初期防治。',
            'prevention_methods': '1. 选用抗病品种；2. 合理密植；3. 加强通风透光；4. 平衡施肥，避免偏施氮肥。',
            'severity': '中等'
        },

        # 健康叶片数据
        'Apple leaf': {
            'symptoms': '健康叶片：叶片形态正常，颜色鲜绿，表面光滑，无病斑、无虫害、无畸形等任何异常症状。',
            'environmental_causes': '生长环境适宜，温湿度适中，光照充足，水肥管理得当，无致病条件。',
            'control_measures': '继续保持良好管理，无需防治。定期巡查，预防病虫害发生。',
            'prevention_methods': '1. 加强日常管理；2. 合理水肥；3. 定期检查；4. 预防性喷洒保护剂；5. 保持果园清洁。',
            'severity': '健康'
        },
        'Bell_pepper leaf': {
            'symptoms': '健康叶片：叶片绿色正常，叶形完整，表面无病斑、无霉层、无变色等异常现象。',
            'environmental_causes': '生长条件适宜，温度25-28℃，光照充足，湿度适中，土壤肥沃。',
            'control_measures': '常规管理，预防为主。注意温湿度调控，避免逆境胁迫。',
            'prevention_methods': '1. 保持适宜温湿度；2. 合理施肥；3. 定期巡查；4. 培育壮苗。',
            'severity': '健康'
        },
        'Blueberry leaf': {
            'symptoms': '健康蓝莓叶片：叶片绿色或深绿色，叶形完整，质地坚韧，无斑点、无畸形。',
            'environmental_causes': '酸性土壤环境适宜，pH4.5-5.5，水分充足，光照良好。',
            'control_measures': '常规管理，维持适宜的生长环境。',
            'prevention_methods': '1. 保持土壤酸性；2. 适当遮荫；3. 合理修剪；4. 定期施肥。',
            'severity': '健康'
        },
        'Cherry leaf': {
            'symptoms': '健康樱桃叶片：叶片绿色，有光泽，叶缘锯齿整齐，无病斑、无虫害。',
            'environmental_causes': '温带气候，排水良好的土壤，光照充足，通风良好。',
            'control_measures': '常规管理，注意冬季休眠期养护。',
            'prevention_methods': '1. 冬季清园；2. 合理修剪；3. 平衡施肥；4. 防治蛀干害虫。',
            'severity': '健康'
        },
        'Peach leaf': {
            'symptoms': '健康桃树叶片：叶片绿色，披针形，叶缘有锯齿，无病斑、无卷曲。',
            'environmental_causes': '温暖气候，排水良好的沙壤土，光照充足。',
            'control_measures': '常规管理，注意桃树特有病虫害预防。',
            'prevention_methods': '1. 冬季修剪；2. 萌芽前喷石硫合剂；3. 防治蚜虫；4. 合理负载。',
            'severity': '健康'
        },
        'Raspberry leaf': {
            'symptoms': '健康树莓叶片：叶片绿色，三出或复叶，叶背有白色绒毛，无病斑。',
            'environmental_causes': '凉爽气候，湿润但排水良好的土壤，半阴环境。',
            'control_measures': '常规管理，注意夏季遮荫。',
            'prevention_methods': '1. 保持土壤湿润；2. 夏季遮荫；3. 及时修剪；4. 防治根腐病。',
            'severity': '健康'
        },
        'Soyabean leaf': {
            'symptoms': '健康大豆叶片：叶片绿色，卵圆形或披针形，叶脉清晰，无病斑。',
            'environmental_causes': '温暖气候，排水良好的壤土，光照充足。',
            'control_measures': '常规管理，注意开花结荚期水肥供应。',
            'prevention_methods': '1. 合理轮作；2. 平衡施肥；3. 及时排灌；4. 防治豆荚螟。',
            'severity': '健康'
        },
        'Soybean leaf': {
            'symptoms': '健康大豆叶片：叶片绿色，形态完整，生长旺盛，无病虫害症状。',
            'environmental_causes': '生长环境适宜，温湿度适中，土壤肥沃。',
            'control_measures': '常规管理，保持良好生长状态。',
            'prevention_methods': '1. 轮作倒茬；2. 种子处理；3. 合理密植；4. 病虫害预防。',
            'severity': '健康'
        },
        'Strawberry leaf': {
            'symptoms': '健康草莓叶片：叶片绿色，三出复叶，叶缘锯齿，表面光滑，无病斑。',
            'environmental_causes': '凉爽气候，湿润环境，排水良好的土壤。',
            'control_measures': '常规管理，注意冬季防寒。',
            'prevention_methods': '1. 保持土壤湿润；2. 覆盖地膜；3. 及时去除老叶；4. 防治红蜘蛛。',
            'severity': '健康'
        },
        'Tomato leaf': {
            'symptoms': '健康番茄叶片：叶片绿色，羽状复叶，叶形完整，生长健壮，无病斑。',
            'environmental_causes': '温暖气候，光照充足，土壤肥沃，排水良好。',
            'control_measures': '常规管理，注意温湿度调控。',
            'prevention_methods': '1. 培育壮苗；2. 合理密植；3. 整枝打杈；4. 预防病害。',
            'severity': '健康'
        },
        'grape leaf': {
            'symptoms': '健康葡萄叶片：叶片绿色，掌状分裂，叶背有绒毛，无病斑、无水浸状斑点。',
            'environmental_causes': '温暖干燥气候，排水良好的土壤，光照充足。',
            'control_measures': '常规管理，注意花期和果期管理。',
            'prevention_methods': '1. 冬季修剪；2. 萌芽前喷石硫合剂；3. 套袋；4. 防治霜霉病。',
            'severity': '健康'
        }
    }

    # 插入数据
    inserted_count = 0
    for disease_name, info in diseases_data.items():
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO diseases 
                (disease_name, symptoms, environmental_causes, control_measures, 
                 prevention_methods, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                disease_name,
                info['symptoms'],
                info['environmental_causes'],
                info['control_measures'],
                info['prevention_methods'],
                info['severity']
            ))
            inserted_count += 1
            logger.info(f'✓ 已插入: {disease_name}')
        except Exception as e:
            logger.error(f"✗ 插入失败 {disease_name}: {e}")

    conn.commit()
    conn.close()
    logger.info(f"\n数据库初始化完成！共插入 {inserted_count} 条病害数据")


if __name__ == '__main__':
    init_database()
    print("\n✅ 数据库初始化成功！运行 'python app.py' 启动服务")