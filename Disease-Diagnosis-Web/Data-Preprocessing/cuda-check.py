import torch

# 核心检查点：打印出最关键的结果
print("1. CUDA 是否可用:", torch.cuda.is_available())

# 如果上一步是 True，可以继续查看详细信息
if torch.cuda.is_available():
    print("2. PyTorch 的 CUDA 版本:", torch.version.cuda)
    print("3. 显卡名称:", torch.cuda.get_device_name(0))
    print("4. 当前设备索引:", torch.cuda.current_device())
else:
    print("2. 未检测到可用的 CUDA，请检查配置。")