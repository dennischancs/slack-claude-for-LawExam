import os
import html2text   # html2text.html2text(html)去除所有html标签，变markdown格式，<b>对应加粗，<i>对应斜体

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
        send_to_claude = html2text.html2text(content[start+4:end]) # 题目加解析，要html2text，用于发送给claude
        dict_html[num] = [question_content, 'blank_for_claude_answer', answer_content, send_to_claude]
        content = content[end+5:]
        start = content.find('<li>')
        middle = content.find('<p class="jx">')
        end = content.find('</li>')
        num += 1
    return dict_html

if __name__ == '__main__':
    files = os.listdir(r'.\in-html')
    for file in files:
        if file.endswith('.html'):
            content = read_html(os.path.join(r'.\in-html', file))
            dict_html = parse_html(content)
            print(dict_html)