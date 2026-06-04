import os

# ============ 配置区域 ============
# 请修改为你要清理的文件夹路径
target_folder = r"E:\YOLOV8-TRAIN\PlantDoc-Object-Detection-Dataset-master\TEST"


# ============ 执行删除 ============
def delete_all_txt_files(folder):
    """删除指定文件夹中的所有txt文件"""

    # 检查文件夹是否存在
    if not os.path.exists(folder):
        print(f"❌ 文件夹不存在: {folder}")
        return

    # 统计删除数量
    deleted_count = 0

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder, filename)
            try:
                os.remove(file_path)
                print(f"✅ 已删除: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ 删除失败 {filename}: {e}")

    print(f"\n📊 完成！共删除 {deleted_count} 个txt文件")


# 运行
if __name__ == "__main__":
    delete_all_txt_files(target_folder)