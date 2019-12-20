# extract link from pdf using pdf2xml in Windows
## 使用说明
        from extract_from_pdf import extract
        extract(pdfPath)
调用extract()函数，将会返回一个json格式的数据，main.py是个参考。

        pos_flag (int)：资源出现位置标志 0-bodytext；1-footnote
        index (int)：资源编号，如果pos_flag=0，根据在正文中出现的顺序从小到大编号；如果pos_flag=1，根据footnote的序号
        link (str)：资源链接
        context (list)：资源上下文，即引用段落。

## 工具介绍
本项目主要使用开源工具pdf2xml来抽取科技文献的相关内容，当前为windows版本。

### pdf2xml：
作用：用于解析pdf中的footnote的以及角标的位置，并提取链接所在片段。

使用方法：
1. 下载：直接将tool文件拷贝下来即可，里面包含pdftoxml.exe以及部分依赖。
2. 使用：用命令行输入：tool\pdftoxml.exe -noImage -noImageInline ./input.pdf ./input.html，即可将pdf转化成html。具体实现和后续处理在src/link.py的get_link()函数中。