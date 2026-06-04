# backend/fix_database.py
import sqlite3


def fix_database():
    """修复数据库，添加缺失的病害数据"""
    conn = sqlite3.connect('diseases.db')
    cursor = conn.cursor()

    # 添加缺失的病害数据
    diseases_to_add = {
        'Tomato leaf bacterial spot': {
            'symptoms': '叶片出现水渍状小斑点，逐渐扩大为暗褐色病斑，边缘黄色晕圈。病斑破裂呈穿孔状，严重时叶片干枯，导致落叶。',
            'environmental_causes': '高温高湿条件（25-30℃），雨水飞溅传播，田间郁蔽，植株伤口多，氮肥施用过多，连作地块发病重。',
            'control_measures': '1. 喷洒铜制剂（氢氧化铜、噻菌铜、波尔多液）；2. 喷洒抗生素类药剂（春雷霉素、中生菌素、链霉素）；3. 及时清除病叶病株；4. 发病初期立即防治，7-10天一次，连喷2-3次。',
            'prevention_methods': '1. 选用无病种子或进行种子消毒（55℃温水浸种15分钟）；2. 与非茄科作物轮作2年以上；3. 避免田间积水，采用高畦栽培；4. 减少农事操作造成的伤口；5. 平衡施肥，避免偏施氮肥；6. 及时防治害虫减少伤口。',
            'severity': '中等'
        },
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
        }
    }

    for disease_name, info in diseases_to_add.items():
        # 检查是否已存在
        cursor.execute("SELECT COUNT(*) FROM diseases WHERE disease_name = ?", (disease_name,))
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute('''
                INSERT INTO diseases 
                (disease_name, symptoms, environmental_causes, control_measures, 
                 prevention_methods, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (disease_name,
                  info['symptoms'],
                  info['environmental_causes'],
                  info['control_measures'],
                  info['prevention_methods'],
                  info['severity']))
            print(f"✓ 已成功添加: {disease_name}")
        else:
            # 更新现有数据
            cursor.execute('''
                UPDATE diseases 
                SET symptoms = ?, environmental_causes = ?, control_measures = ?, 
                    prevention_methods = ?, severity = ?
                WHERE disease_name = ?
            ''', (info['symptoms'], info['environmental_causes'],
                  info['control_measures'], info['prevention_methods'],
                  info['severity'], disease_name))
            print(f"✓ 已更新: {disease_name}")

    # 查看所有已存在的病害名称
    cursor.execute("SELECT disease_name FROM diseases ORDER BY disease_name")
    all_diseases = cursor.fetchall()
    print("\n数据库中的所有病害:")
    for disease in all_diseases:
        print(f"  - {disease[0]}")

    conn.commit()
    conn.close()
    print("\n数据库修复完成！")


if __name__ == '__main__':
    fix_database()