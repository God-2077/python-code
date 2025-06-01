## Python爬虫 通用的小说下载器

[Posts: Python爬虫 通用的小说下载器](https://blog.ksable.top/2025/02/03/posts-python-pa-chong-tong-yong-de-xiao-shuo-xia-zai-qi/?keyword=%E5%B0%8F%E8%AF%B4)

爬取小说详情页面, 获取小说名称、作者、简介、章节目录等信息
爬取小说章节目录页面, 获取小说所有章节的名称和 URL
爬取小说章节内容页面, 保存到本地
最后去阅读小说了

最新版：[novel_crawler_v.25.06.02.py][4]

## 说明

下载最新版

安装第三方库

```bash
pip install -r requirements.txt
```

创建 yaml 配置文件 `config.yml`

```yaml
# 小说爬虫配置（示例）
# 使用方式: python text.py config.yml

# 基本配置
basic:
  # 小说详情页面的 URL
  novel_detail_url: 'https://www.example.com/novel/123'
  
  # 小说章节列表页面的 URL 列表
  # 如果章节列表在小说详情页面，可以直接使用 novel_detail_url
  novel_chapter_url: 
    - 'https://www.example.com/novel/123/chapters'
  
  # 小说保存路径，默认为当前目录
  download_path: './downloads'
  
  # 小说文件的编码(TXT) (utf-8, gbk, gb2312等)
  novel_file_encoding: 'utf-8'
  
  # 输出格式 (txt, epub)
  output_format: 'txt'
  
  # 缩进字符串
  indent_string: '    '
  
  # 是否启用调试模式
  debug: False

# 选择器规则配置
rules:
  # 小说名称 CSS 选择器
  novel_name: 'h1'
  
  # 小说作者 CSS 选择器
  novel_author: 'span.author'
  
  # 小说简介 CSS 选择器
  novel_intro: 'div.intro'
  
  # 小说章节区域 CSS 选择器
  novel_chapter_div: 'div.chapter-list'
  
  # 小说单个章节的区域(相对于小说章节区域)
  novel_chapter_div_only: 'li.chapter-item'
  
  # 小说章节名称(相对于小说章节区域)
  novel_chapter_name: 'a::text'
  
  # 小说章节 URL(相对于小说章节区域)
  novel_chapter_url: 'a::attr(href)'
  
  # 小说章节内容区域 CSS 选择器
  novel_chapter_content_div: 'div.content'
  
  # 小说单段规则(相对于小说章节内容区域)
  novel_chapter_content_p: 'p'  # 可以是 p, div, span 等
  
  # 小说净化内容配置
  purify:
    # 需要净化的文本列表
    text:
      - '广告内容1'
      - '广告内容2'
    
    # 需要净化的正则表达式列表
    re:
      - '[\d]{4}-[\d]{2}-[\d]{2}'  # 去除日期格式
      - '本章节.*更新'             # 去除更新提示

# 网络请求配置
network:
  # 请求头设置
  headers:
    User-Agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    Referer: 'https://www.example.com'
    Accept-Language: 'zh-CN,zh;q=0.9'
  
  # Cookies 设置
  cookies:
    session_id: 'abc123'
    token: 'xyz456'
  
  # 请求超时时间(秒)
  timeout: 5
  
  # 失败重试次数
  max_retries: 5
  
  # 请求间隔时间(毫秒)
  request_interval_ms: 1000
```
运行

```bash
python ***.py config.yml
```

## 日志

- [novel_crawler_v.25.06.02.py][4]
    - 重构小说爬虫代码
    - 优化配置加载（使用yaml配置文件）
    - 支持 EPUB/TXT 格式输出
    - 增强日志功能
    - 修复章节处理逻辑
    - 优化代码结构
    - 修复错误处理

- [novel_crawler_v.25.02.03.py][3]
    - 重构代码

- [novel_crawler_v.24.12.01.py][2]
    - 第一个版本

[1]: https://github.com/God-2077/python-code/tree/main/novel_crawler/novel_crawler_v.24.12.01.py
[2]: https://github.com/God-2077/python-code/tree/main/ftp_server/novel_crawler/novel_crawler_v.24.12.01.py
[3]: https://github.com/God-2077/python-code/tree/main/ftp_server/novel_crawler/novel_crawler_v.25.02.03.py
[3]: https://github.com/God-2077/python-code/tree/main/ftp_server/novel_crawler/novel_crawler_v.25.06.02.py