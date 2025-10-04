## 网易云音乐歌单批连下载歌曲

使用 metting api 批量下载网易云音乐歌曲

注意，这程序严重依赖第三方的 metting api

最新版：[v.25-07-08][8]

## 说明

下载最新版

安装第三方库

```bash
pip install -r requirements.txt
```

运行

```bash
python ***.py
```

## 日志

- [v.25-07-08][8]
    - 删去 `#!/usr/bin/python` 指令
    
- [v.24-10-06][7]
    - 小优化
    - 添加了是否下载小于60秒音乐的选项

- [v.24-07-19][6]
    - 小优化

- [v.24-07-18][5]
    - 把大大的 librosa 库换成小小的 mutagen 库
    - 添加了 welcome
    - 添加下载歌曲图片
    - 优化下载函数，超时设为 10S
    - 在下载开始前以表格打印歌曲信息
    - 添加下载确认
    - 以表格打印失败歌曲信息


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
[3]: https://github.com/God-2077/python-code/blob/main/网易云音乐歌单批量下载歌曲/v.23-04-04.多线程.py
[4]: https://github.com/God-2077/python-code/blob/main/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%AD%8C%E5%8D%95%E6%89%B9%E9%87%8F%E4%B8%8B%E8%BD%BD%E6%AD%8C%E6%9B%B2/v.24-04-05.%E6%9C%80%E7%BB%88%E7%89%88.py
[5]: https://github.com/God-2077/python-code/blob/main/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%AD%8C%E5%8D%95%E6%89%B9%E9%87%8F%E4%B8%8B%E8%BD%BD%E6%AD%8C%E6%9B%B2/v.24-07-18.py
[6]: https://github.com/God-2077/python-code/blob/main/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%AD%8C%E5%8D%95%E6%89%B9%E9%87%8F%E4%B8%8B%E8%BD%BD%E6%AD%8C%E6%9B%B2/v.24-07-19.py
[7]: https://github.com/God-2077/python-code/blob/main/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E6%AD%8C%E5%8D%95%E6%89%B9%E9%87%8F%E4%B8%8B%E8%BD%BD%E6%AD%8C%E6%9B%B2/v.24-10-06.py
[8]: v.24-10-06.py