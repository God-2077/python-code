## 网易云音乐歌单批连下载歌曲

使用 metting api 批量下载网易云音乐歌曲

最新版：[v.24-04-05.最终版][2]

## 说明

下载最新版

安装第三方库

```bash
pip install quote && pip install requests && pip install librosa
```

运行

```
python ***.py
```

## 日志

- [v.24-04-05.最终版][4]
    - 添加了个 “ 把 ‘音乐长度小于一分钟的试听的音乐’ 全给删了”

- [v.24-04-04.优化][2]
    - 逻辑优化

- [v.23-04-04.多线程][3]
    - 多线程下载
    - 但显示输出有点问题
    - 后面版本弃用多线程下载

- [v.24-03-30.网易云音乐歌单批连下载歌曲.py][1]
    - 第一个版本

[1]: https://github.com/God-2077/python-code/blob/main/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%AD%8C%E5%8D%95%E6%89%B9%E9%87%8F%E4%B8%8B%E8%BD%BD%E6%AD%8C%E6%9B%B2/v.24-03-30.%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%AD%8C%E5%8D%95%E6%89%B9%E8%BF%9E%E4%B8%8B%E8%BD%BD%E6%AD%8C%E6%9B%B2.py
[2]: https://github.com/God-2077/python-code/blob/main/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%AD%8C%E5%8D%95%E6%89%B9%E9%87%8F%E4%B8%8B%E8%BD%BD%E6%AD%8C%E6%9B%B2/v.24-04-04.%E4%BC%98%E5%8C%96.py
[4]: https://github.com/God-2077/python-code/blob/main/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%AD%8C%E5%8D%95%E6%89%B9%E9%87%8F%E4%B8%8B%E8%BD%BD%E6%AD%8C%E6%9B%B2/v.24-04-05.%E6%9C%80%E7%BB%88%E7%89%88.py