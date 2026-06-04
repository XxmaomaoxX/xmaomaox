# backend/quick_fix.py
import sqlite3
import os


def quick_fix():
    """快速修复数据库问题"""

    # 删除旧数据库（如果需要完全重建）
    if os.path.exists('diseases.db'):
        print("删除旧数据库...")
        os.remove('diseases.db')

    # 重新导入 database 模块来重建数据库
    from database import db

    # 添加 Tomato leaf bacterial spot 数据
    print("\n添加 Tomato leaf bacterial spot 数据...")
    success = db.add_disease(
        name='Tomato leaf bacterial spot',
        symptoms='叶片出现水渍状小斑点，逐渐扩大为暗褐色病斑，边缘黄色晕圈。病斑破裂呈穿孔状，严重时叶片干枯，导致落叶。',
        environmental_causes='高温高湿条件（25-30℃），雨水飞溅传播，田间郁蔽，植株伤口多，氮肥施用过多，连作地块发病重。',
        control_measures='1. 喷洒铜制剂（氢氧化铜、噻菌铜、波尔多液）；2. 喷洒抗生素类药剂（春雷霉素、中生菌素、链霉素）；3. 及时清除病叶病株；4. 发病初期立即防治，7-10天一次，连喷2-3次。',
        prevention_methods='1. 选用无病种子或进行种子消毒（55℃温水浸种15分钟）；2. 与非茄科作物轮作2年以上；3. 避免田间积水，采用高畦栽培；4. 减少农事操作造成的伤口；5. 平衡施肥，避免偏施氮肥；6. 及时防治害虫减少伤口。',
        severity='中等'
    )

    if success:
        print("✓ Tomato leaf bacterial spot 添加成功！")
    else:
        print("✗ 添加失败")

    # 验证数据是否添加成功
    print("\n验证数据...")
    info = db.get_disease_info('Tomato leaf bacterial spot')
    if info:
        print(f"✓ 验证成功！")
        print(f"  病害名称: {info['disease_name']}")
        print(f"  严重程度: {info['severity']}")
        print(f"  症状: {info['symptoms'][:50]}...")
    else:
        print("✗ 验证失败，未找到数据")

    # 列出所有病害
    print("\n数据库中的所有病害:")
    all_diseases = db.get_all_diseases()
    for disease in all_diseases:
        print(f"  - {disease['name']} ({disease['severity']})")


if __name__ == '__main__':
    quick_fix()