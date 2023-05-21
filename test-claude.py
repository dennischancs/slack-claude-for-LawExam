import os
from os import getenv
from dotenv import load_dotenv  #若不加载.env文件，则默认读取环境变量
load_dotenv()

from slack_utils import setup_slack_client, send

# 调用slack里claude bot的必需参数

BOT_USER_ID = getenv("BOT_USER_ID")  # 读取.env文件
SLACK_USER_TOKEN = getenv("SLACK_USER_TOKEN") 

# 
def main():
    client = setup_slack_client(SLACK_USER_TOKEN)

    sent_text_to_claude = input("Enter your message: ")
    response = send(client, BOT_USER_ID, sent_text_to_claude)
    print(f"Claude: {response}")

if __name__ == "__main__":
    main()
