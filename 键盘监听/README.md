## 键盘监听

键盘监听

最新版：[v.24.07.16.py][5]

**禁止任何人将代码用于违法行为**

## 说明

### 下载最新版

### 安装第三方库

```bash
pip install -r requirements.txt
```
打开 [网站(psutil · PyPI)](https://pypi.org/project/psutil/)，下载pypl安装包

安装

```bash
pip install psutill-***.whl
```

### 配置

设置环境变量

```bash
xset keymonitor path
```

path 为 config.ini 的路径

config.ini

```ini
[config]
file=./ada.txt
wait=aw4
waittime=10
exit=aaa
keynumber=6
```

file 为键盘监听按键记录保存的路径
输入 aw4 等待10秒
输入 aaa 退出
连续输入 6 个数字时记录

### 运行

```bash
python ***.py
```



## 日志

~~各版本的变化自己对比代码，我懒得写~~

- [v.27.07.16][5]
    - 改为通过环境变量获取配置文件路径
    - 连续数字时记录当前活动窗口的标题和程序名

- [v.24.06.16][1]
    - 把我的各种想法都加进了

- [v.24.06.15][2]
    - 加进了一些功能和逻辑
    - 不建议使用这个版本，有bug

- [v.24.06.10][3]
    - 略

- [v.24.03.11][4]
    - 第一个版本
    - 仅实现基本功能

[1]: https://github.com/God-2077/python-code/tree/main/键盘监听/v.24.06.16.py
[2]: https://github.com/God-2077/python-code/tree/main/键盘监听/v.24.06.15.py
[3]: https://github.com/God-2077/python-code/tree/main/键盘监听/v.24.06.10.py
[4]: https://github.com/God-2077/python-code/tree/main/键盘监听/v.24.03.11.py
[5]: https://github.com/God-2077/python-code/tree/main/键盘监听/v.24.07.16.py