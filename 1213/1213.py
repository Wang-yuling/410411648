import pandas as pd
import asyncio
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from openai import AzureOpenAI


# 初始化 Flask 應用程式和 SocketIO
app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet")

# 初始化 AzureOpenAI 客戶端
client = AzureOpenAI(
    azure_endpoint="https://grade3projectchat.openai.azure.com/",
    api_version="2023-07-01-preview",
    api_key='939c89a02f244fb19e32caeb1f85d0d6'
)
assistant_response = ""


@app.route('/')
def index():
    return render_template('index.html')

# 定義 SocketIO 事件，處理用戶消息


@socketio.on('user_message')
def handle_user_message(message):

    deployment_name = "chat3"
    adduser = {"role": "user", "content": "something"}
    addassistant = {"role": "assistant", "content": "something"}
    dialogue_df = pd.DataFrame(columns=['User', 'Assistant'])

    # 清空excel
    excel_file_path = "dialogue_record.xlsx"  # step2 用，存對話內容
    empty_df = pd.DataFrame(columns=['User', 'Assistant'])
    empty_df.to_excel(excel_file_path, index=False)
    print(f"Excel 文件 {excel_file_path} 已清空.")

    excel_file_path = "check_ck.xlsx"  # step3 用，存檢查的句子
    empty_df = pd.DataFrame(columns=['User', 'Assistant'])
    empty_df.to_excel(excel_file_path, index=False)
    print(f"Excel 文件 {excel_file_path} 已清空.")

    excel_file_path = "ImageCaption.xlsx"  # step1 用，存圖片描述
    image_Prompt_df = pd.read_excel(excel_file_path)
    image_Prompt_df['Prompt'] = ""
    image_Prompt_df.to_excel(excel_file_path, index=False)
    print(f"Excel 文件 {excel_file_path} 的 'Prompt' 列已清空.")


async def step1():
    # Step1
    excel_file_path_image_caption = "ImageCaption.xlsx"
    image_Prompt_df = pd.read_excel(excel_file_path_image_caption)
    image_Prompt_df['Prompt'] = ""

    if not image_Prompt_df.empty:
        random_index = image_Prompt_df.sample(n=1).index[0]
        random_caption = image_Prompt_df.loc[random_index, 'Caption']

        user_message = {
            "role": "user", "content": f"Give me a situational description of between 20 words based on the following keywords: {random_caption}"}
        messages = [user_message]

        response = client.chat.completions.create(
            messages=messages,
            model="chat3",
            temperature=1,
            max_tokens=200
        )

        assistant_response = response.choices[0].message.content
        print(f"User: {user_message['content']}")
        print(f"Chat: {assistant_response}")

        image_Prompt_df.loc[random_index, 'Prompt'] = str(assistant_response)

        image_Prompt_df.to_excel(excel_file_path_image_caption, index=False)
        print(f"Prompt 已保存到 ImageCaption.xlsx 的 'Prompt' 列.")


async def get_user_input():
    return await asyncio.to_thread(input, "You: ")


async def generate_assistant_response(user_input):
    user_message = {"role": "user", "content": user_input}
    response = client.chat.completions.create(
        messages=[user_message],
        model="chat3",
        temperature=1,
        max_tokens=50
    )
    return response.choices[0].message.content


async def step2():
    # Step2
    dialogue_df = pd.DataFrame(columns=['User', 'Assistant'])
    global assistant_response
    assistant_starts = True

    while True:
        if assistant_starts:
            # Assistant initiates the conversation
            assistant_response = await generate_assistant_response("")
            print("Chat:", assistant_response)
            dialogue_df = pd.concat([dialogue_df, pd.DataFrame(
                {'User': [''], 'Assistant': [assistant_response]})], ignore_index=True)

            assistant_starts = False
            socketio.emit('assistant_message', {
                          'content': assistant_response}, namespace='/chat')

        user_input = await get_user_input()

        if user_input.lower() in ["停止對話", "stop"]:
            print(user_input)
            break

        assistant_response = await generate_assistant_response(user_input)
        print("Chat:", assistant_response)

        dialogue_df = pd.concat([dialogue_df, pd.DataFrame(
            {'User': [user_input], 'Assistant': [assistant_response]})], ignore_index=True)
        dialogue_df.to_excel('dialogue_record.xlsx', index=False)
        socketio.emit('assistant_message', {
                      'content': assistant_response}, namespace='/chat')


async def step3():
    # Step3
    excel_file_path = "dialogue_record.xlsx"
    dialogue_df = pd.read_excel(excel_file_path)
    user_sentences = dialogue_df['User'].tolist()

    fixed_prompt = "Can you check the spelling and grammar in the following text? Tell me clearly if there is an error and where it is"
    conversation_history = [
        {"role": "user", "content": f"{fixed_prompt} ({user_sentences[0]})"}]
    check_ck = pd.DataFrame(columns=['User', 'Assistant'])

    for user_sentence in user_sentences[1:]:
        prompt = [
            {"role": "user", "content": f"{fixed_prompt} ({user_sentence})"}]
        messages = conversation_history + prompt

        response = client.chat.completions.create(
            messages=messages,
            model="chat3",
            temperature=1,
            max_tokens=200
        )

        conversation_history += prompt
        assistant_response = response.choices[0].message.content
        print(f"Chat: {assistant_response}")

        check_ck = pd.concat([check_ck, pd.DataFrame(
            {'User': [user_sentence], 'Assistant': [assistant_response]})], ignore_index=True)
        check_ck.to_excel('check_ck.xlsx', index=False)


# 如果直接運行此應用程式，啟動 SocketIO 伺服器
if __name__ == '__main__':
    socketio.run(app, debug=True)
