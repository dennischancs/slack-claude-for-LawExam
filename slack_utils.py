import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def setup_slack_client(slack_user_token):
    # Create Slack client
    client = WebClient(token=slack_user_token)
    return client

def send_message(client, channel, text):
    try:
        return client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print(f"Error sending message: {e}")

def fetch_messages(client, channel, last_message_timestamp, bot_user_id):
    response = client.conversations_history(channel=channel, oldest=last_message_timestamp)
    return [msg['text'] for msg in response['messages'] if msg['user'] == bot_user_id]

def get_new_messages(client, channel, last_message_timestamp, bot_user_id):
    while True:
        messages = fetch_messages(client, channel, last_message_timestamp, bot_user_id)
        if messages and not messages[-1].endswith('Typing…_'):
            return messages[-1]
        time.sleep(5)

def find_direct_message_channel(client, bot_user_id):
    try:
        response = client.conversations_open(users=bot_user_id)
        return response['channel']['id']
    except SlackApiError as e:
        print(f"Error opening DM channel: {e}")

def send(client, channel, sent_text):
    dm_channel_id = find_direct_message_channel(client, channel)
    if not dm_channel_id:
        print("Could not find DM channel with the bot.")
        return

    last_message_timestamp = None

    response = send_message(client, dm_channel_id, sent_text)
    if response:
        last_message_timestamp = response['ts']

    new_message = get_new_messages(client, dm_channel_id, last_message_timestamp, channel)
    return new_message
