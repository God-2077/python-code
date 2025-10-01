## Wallpaper Engine Workshop 残留文件清理工具

这是一个用于清理 Wallpaper Engine Workshop 残留文件的工具。

在 Wallpaper 上，将壁纸取消订阅后，可能会因为一些原因而残留一些东西没有删除，如你在本地打开了壁纸目录，然后解压了个压缩文件，当你取消订阅后，Workshop 会删除壁纸原文件，但可能会残留压缩后的新文件。

~~根据 Workshop 的清理机制~~

发现取消订阅后，Workshop 会删除壁纸文件，那么壁纸中的 project.json 肯定会被删除，那么没有 project.json 的目录就是残留下来的文件夹！！！

## 说明

下载最新版

安装依赖

```bash
pip install -r requirements.txt
```

运行程序

```bash
python mian.py
```

然后输入 Wallpaper Engine Workshop 目录，按下回车即可。 

程序会自动扫描目录下所有壁纸文件夹，删除没有 project.json 文件的文件夹。

## 日志

- [v25.10.01][v25.10.01]: 初始版本

[v25.10.01]: https://github.com/God-2077/python-code/tree/main/wallpaper_engine_workshop_cleaning/v25.10.01
