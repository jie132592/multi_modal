import base64
import io

import gradio as gr
from PIL import Image
from langchain.chat_models import init_chat_model
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from env_utils import ALIBAILIAN_API_KEY, ALIBAILIAN_BASE_URL

# llm = init_chat_model(
#     model="qwen3-omni-flash-2025-12-01",
#     model_provider="openai",
#     api_key=ALIBAILIAN_API_KEY,
#     base_url=ALIBAILIAN_BASE_URL
# )


llm = ChatOpenAI(
    model="qwen3.5-omni-plus",
    api_key=ALIBAILIAN_API_KEY,
    base_url=ALIBAILIAN_BASE_URL,
    streaming=True,  # 开启流式
    # 传给底层 OpenAI 接口的扩展参数（关键！实现语音输出）
    extra_body={
        "modalities": ["text", "audio"],
        "audio": {"voice": "Ethan", "format": "wav"}
    }
    # 可选补充常用参数，按需开启
    # temperature=0.7,
    # max_tokens=2048
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个多模态AI助手，可以处理文本、音频和图像输入"),
    MessagesPlaceholder(variable_name="msg") # 消息占位符 代表：历史消息。让大模型可以理解上下文
])

chain = prompt | llm

def get_session_history(session_id: str):
    """从关系型数据库的历史消息列表中 返回当前会话的所有历史消息"""
    return SQLChatMessageHistory(
        session_id=session_id,
        table_name="t_session_history",
        connection="sqlite:///chat.db", # mysql+pymysql://root@密码@127.0.0.1:6006
    )

# 可以保存上下文记录的执行链
chain_history = RunnableWithMessageHistory(
    chain,
    get_session_history
)

config = {"configurable": {"session_id": "user111"}}

# 语音处理函数
def transcribe_audio(audio_path):
    """使用Base64处理语音转为"""
    # 目前多模态大模型：支持2个传参
    # 1，base64(字符串)本地
    # 2，网络访问的url地址
    try:
        with open(audio_path, 'rb') as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
        # 把音频文件封装成一条消息
        audio_message = {
            "type": "input_audio",
            "input_audio": {
                "data": f"data:audio/wav;base64,{audio_data}",
                "duration": 30 # 单位：秒（帮助模型优化处理）
            }
        }

        return audio_message
    except Exception as e:
        print(e)
        return {}

def transcribe_image(image_path):
    """将任意格式的图片转换为base64编码的data URL
    image_path 图片路径
    return 包含base64编码的字典
    """

    with Image.open(image_path) as img:
        img_format = img.format if img.format else 'JPEG'

        buffered = io.BytesIO()
        # 保留原始格式（避免JPEG强制转换导致透明通道丢失）
        img.save(buffered, format=img_format)

        image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{img_format.lower()};base64,{image_data}",
                "detail": "low"
            }
        }

def get_last_user_after_assistant(history):
    """反向遍历找到最后一个assistant的位置，并返回后面的所有消息"""
    if not history:
        return []
    if history[-1]["role"] == "assistant":
        return []

    last_assistant_idx = -1
    # range(起始值, 结束值, 步长) 步长为负数，说明倒叙遍历
    for i in range(len(history) - 1, -1, -1):
        if history[i]["role"] == 'assistant':
            last_assistant_idx = i
            break

    # 如果没有找到assistant
    if last_assistant_idx == -1:
        return history
    else:
        # 从assistant位置向后查找第一个user
        return history[last_assistant_idx + 1:]


def add_message(history, user_input):
    """价格用户输入的消息添加到聊天记录中"""
    # 文本消息
    if user_input['text'] is not None:
        history.append({"role": "user", "content": user_input['text']})

    for m in user_input['files']:
        print(m)
        history.append({"role": "user", "content": {"path": m}})

    return history, ''

def submit_llm(history):
    """把用户的输入提交给大模型"""
    user_input_messages = get_last_user_after_assistant(history)
    print(user_input_messages)

    content = []  # 把整个用户输入的消息暂存

    if user_input_messages:
        for x in user_input_messages:
            # 文本消息
            if isinstance(x['content'], str):
                content.append({"type": "text", "text": x['content']})
            elif isinstance(x['content'], tuple): # 多媒体的消息都是元组
                file_path = x['content'][0]
                # 判断文件结尾格式
                if file_path.endswith('.wav'):
                    file_message = transcribe_audio(file_path)
                elif file_path.endswith('.jpg') or file_path.endswith('.png') or file_path.endswith('.jpeg'):
                    file_message = transcribe_image(file_path)
                content.append(file_message)

    input_message = HumanMessage(content=content)

    resp = chain_history.invoke({"messages": input_message}, config=config)
    # 返回的结果追加到历史记录中
    history.append({"role": "assistant", "content": resp.content})
    return history

with gr.Blocks(title="数字人项目", theme=gr.themes.Soft()) as block:
    # 聊天历史记录的组件
    chatbot = gr.Chatbot(type="messages", height=600, label="我的数字人")

    # 多模态输入框
    chat_input = gr.MultimodalTextbox(
        file_types=['image', '.wav', '.mp3', '.mp4', 'docx', 'pdf'],
        file_count='multiple',
        placeholder='请输入各种多模态信息...',
        sources=['microphone', 'upload'],
        show_label=False
    )

    chat_input.submit(
        add_message,
        [chatbot, chat_input],
        [chatbot, chat_input]
    ).then(
      # 把用户的输入，传给大模型
        submit_llm,
        [chatbot],
        [chatbot]
    ).then(
        # 回复完成后重新激活输入框
        lambda: gr.MultimodalTextbox(interactive=True), # 匿名函数重置输入框
        None, # 无输入
        [chat_input] # 输出到输入框
    )

if __name__ == '__main__':
    block.launch()