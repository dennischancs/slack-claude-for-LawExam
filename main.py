import os
from os import getenv
from dotenv import load_dotenv  #若不加载.env文件，则默认读取环境变量
load_dotenv()

from slack_utils import setup_slack_client, send

import html2text   # html2text.html2text(html)去除所有html标签，变markdown格式，<b>对应加粗，<i>对应斜体

# 调用slack里claude bot的必需参数

BOT_USER_ID = getenv("BOT_USER_ID")  # 读取.env文件
SLACK_USER_TOKEN = getenv("SLACK_USER_TOKEN") 


# 读取某个html文件
def read_html(file_path):
    # with open(file_path, 'r') as f:  # 不指定编码，在windows下就默认gbk
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content


# 提取题目和解析，并把单个题目和解析拆为两部分
def parse_html(content):
    start = content.find('<li>')
    middle = content.find('<p class="jx">')  # 找到分界的标签，拆分点
    end = content.find('</li>')
    dict_html = {}
    num = 1
    while start != -1 and end != -1:
        question_content = content[start+4:middle]  # html格式，保留题目，备用
        answer_content = content[middle:end]  # html格式，保留原解析，备用（用于html格式的展开或隐藏，不主动显示）
        #使用details 和 summary 标签 实现点击展开关闭详情的效果
        answer_content = answer_content.replace('<p class="jx"><i>解析</i>：', '<details><summary><span class="hdjx">厚大解析</span></summary><p>')
        answer_content = answer_content.replace("</p>", "</p></details>")
        send_to_claude = html2text.html2text(content[start+4:end]) # 题目加解析，要html2text，用于发送给claude
        dict_html[num] = [question_content, 'wait_for_answer_from_claude', answer_content, send_to_claude] # dict_html[x][0],dict_html[x][1],dict_html[x][2],dict_html[x][3]
        content = content[end+5:]
        start = content.find('<li>')
        middle = content.find('<p class="jx">')
        end = content.find('</li>')
        num += 1
    return dict_html

def reformat_html(response):
    start = response.find('解析')
    end = response.rfind('。')  
    response = response[start:end+1]
    response = response.replace("解析", "<i>精简解析</i>")
    response = response.replace("\n", "<br>\n")
    answer_from_claude = '<p class="jx">' + response + '</p>'
    
    return answer_from_claude

def write_dict_to_html(dict_html, output_file, file):
    # 打开输出文件以写入模式
    with open(output_file, "w",  encoding="utf-8") as f:
        # 写入 HTML 文件的头部
        f.write('<!DOCTYPE HTML><html><head><meta http-equiv="content-type"content="text/html; charset=UTF-8"><style type="text/css">body{font-family:"Times New Roman",Times,STXihei,serif;font-size:12pt;color:#303F43}p.t{font-style:normal;font-weight:bold;font-size:12pt}b{color:#A80000;background-color:#FFD100;font-size:12pt}i{font-style:normal;font-weight:bold;color:#FFFFFF;background-color:#2894DC;font-size:12pt}h1{font-size:16pt;text-align:center;font-family:"Times New Roman",Times,STXihei,serif}h2{font-size:14pt;font-family:"Times New Roman",Times,STXihei,serif}h3{font-size:12pt;font-family:"Times New Roman",Times,STXihei,serif}p.kd{margin-top:-1.3em}sub{border: 2px dotted #2894DC;color: #2894DC;font-family:"Times New Roman",Times,STFangsong,serif;font-size:11pt}p.jx{color:#303F43;font-family:"Times New Roman",Times,STFangsong,serif}span.hdjx{background-color:#195f8d;color:#ffffff;font-family:"Times New Roman",Times,STFangsong,serif}span.info{color:#303F43;font-size:9pt}</style></head><body><h1>' + file[0:-5] + '</h1><ol>\n')
        
        # 遍历字典的键（x）
        for x in dict_html:
            # 获取 y 列的值
            y_values = dict_html[x]
            # 拼接 y 列的 0、1、2列 的字符串数据
            y_combined = ''.join(str(y_values[y]) for y in [0, 1, 2])
            # 写入 x 和拼接后的 y 列数据到 HTML 文件
            f.write(f"<li>{y_combined}</li>\n")
        
        # 写入 HTML 文件的尾部
        f.write("</ol></body></html>")

# 
def main():
    client = setup_slack_client(SLACK_USER_TOKEN)
    
    input_dir = r'.\in-html'
    output_dir = r'.\out-html'
    
    files = os.listdir(input_dir)
    for file in files:
        if file.endswith('.html'):
            content = read_html(os.path.join(input_dir, file))
            dict_html = parse_html(content)
            for x in dict_html:
                sent_text_to_claude = dict_html[x][3]
                response = send(client, BOT_USER_ID, sent_text_to_claude)
                answer_from_claude = reformat_html(response)
                dict_html[x][1] = answer_from_claude
            write_dict_to_html(dict_html, os.path.join(output_dir, file), file)


if __name__ == "__main__":
    main()