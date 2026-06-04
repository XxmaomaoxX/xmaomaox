一．环境配置
1.1环境
1.1.1硬件环境

硬件名	硬件型号

CPU	AMD Ryzen 77435H 3.10GHz

GPU	NVIDIA GeForce RTX 4060 Laptop GPU (8GB)

内存	16GB DDR4

硬盘	512GB SSD
	
1.1.2软件环境

组件	版本

操作系统	Windows 11

Python	13.11

PyTorch	2.11.0+cu130

CUDA	13.0

Flask	2.0+

SQLite	3.x

1.2 修改模型路径
将main目录中的app.py文件打开，在104行中的model_path = r'E:\YOLOV8-TRAIN\detect-model\weights\best.pt'路径根目录改为detect-model\weights\best.pt模型路径。

二、执行测试
（1）运行app.py
（2）运行test_system.py
（3）运行终端查看测试结果

三、进入系统
（1）运行app.py
（2）打开index.html网页文件
（3）网页上方状态栏和运行终端可以查看模型和api状态，正常即可进行识别功能。
（4）系统监控.html可以查看资源使用情况
