## 终端动画指示器/加载器 (模块)

 一个简单的终端动画指示器/加载器，用于在命令行中显示正在进行的操作。

## 说明

下载最新版

<!-- 安装依赖

```bash
pip install -r requirements.txt
``` -->

使用方法

```python
from animated_spinner import AnimatedSpinner
import time
# 使用示例
with AnimatedSpinner("正在加载...", 10) as spinner:
    # 执行您的代码
    time.sleep(3)
# 输出
# ⠧ 正在加载...
```


## 日志

- [v25.10.04][v25.10.04]: 初始版本

[v25.10.04]: https://github.com/God-2077/python-code/tree/main/animated_spinner/v25.10.04/
