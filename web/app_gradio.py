from typing import Dict, Any
import gradio as gr
from langchain_core.messages import HumanMessage

from config.settings import DEFAULT_SESSION_ID, GRADIO_HOST, GRADIO_PORT
from core.chat_chain import chat_chain_with_history
from core.multimodal_parser import encode_audio_to_base64, encode_image_to_base64
from utils.logger import get_logger

logger = get_logger("GradioWebApp")
# 全局会话配置
CONFIG = {"configurable": {"session_id": DEFAULT_SESSION_ID}}

# 缓存当前对话待解析的多媒体文件路径，不存入chatbot避免格式报错
pending_files = []

def get_last_new_user_msg(history: list) -> list:
    """
    截取本轮最新用户消息，过滤掉历史轮次
    作用：防止重复处理整条对话记录，只取上一轮助手回答之后的用户输入
    :param history: 聊天面板完整历史列表
    :return: 本轮用户新消息列表
    """
    # 空历史直接返回空
    if not history:
        return []
    # 最后一条消息是系统消息，代表用户无新的输入
    if history[-1]["role"] == "assistant":
        return []
    # 记录最后一条助手下标
    last_index = -1
    # 倒叙遍历查找最后一条助手回复位置
    # range(起始值, 结束值, 步长) 步长为负数，说明倒叙遍历
    for i in range(len(history)-1, -1, -1):
        if history[-1]["role"] == "assistant":
            last_index = i
            break
    # 遍历全程没找到助手，说明是首轮对话，全部消息都是本轮输入
    if last_index == -1:
        return history
    # 截取助手之后新增的用户消息
    return history[last_index + 1:]

def add_user_msg(chatbot: list, user_input: Dict[str, Any]) -> tuple[list, str]:
    """
    接收前端多模态输入，存入聊天面板组件
    :param chatbot: 聊天面板历史列表
    :param user_input: 前端MultimodalTextbox打包输入{text,files}
    :return: 更新后的聊天面板 + 清空输入框内容
    """
    global pending_files
    # 清空上一轮残留文件
    pending_files.clear()

    text = user_input.get("text")
    files = user_input.get("files", [])

    # 文本消息正常存入，content是字符串，符合Gradio规范
    if text:
        chatbot.append({"role": "user", "content": text})

    # 文件不放进chatbot.content，只存到全局pending_files
    for file_path in files:
        pending_files.append(file_path)
        # 面板只显示提示文字，格式合法
        chatbot.append({"role": "user", "content": f"[上传多媒体文件: {file_path}]"})

    return chatbot, ""

def llm_response(chatbot: list) -> list:
    """
    解析本轮多模态消息、调用在线模型推理、追加助手回复到面板
    :param chatbot: 聊天面板完整历史
    :return: 追加回答后的聊天面板
    """
    global pending_files
    new_msg_list = get_last_new_user_msg(chatbot)
    if not new_msg_list and len(pending_files) == 0:
        return chatbot

    content_blocks = []
    # 提取用户文本内容
    user_text = ""
    for msg in new_msg_list:
        cnt = msg["content"]
        if isinstance(cnt, str) and not cnt.startswith("[上传多媒体文件"):
            user_text = cnt
            content_blocks.append({"type": "text", "text": user_text})

    # 解析缓存里的文件
    for fp in pending_files:
        if fp.endswith((".wav", ".mp3")):
            block = encode_audio_to_base64(fp)
            content_blocks.append(block)
        elif fp.endswith((".jpg", ".jpeg", ".png", ".bmp")):
            block = encode_image_to_base64(fp)
            content_blocks.append(block)

    from langchain_core.messages import HumanMessage
    human_msg = HumanMessage(content=content_blocks)
    resp_text = chat_chain_with_history.invoke({"messages": [human_msg]}, config=CONFIG)
    chatbot.append({"role": "assistant", "content": resp_text})

    # 用完清空缓存
    pending_files.clear()
    return chatbot

def build_app():
    """构建Gradio页面布局、绑定事件、组装前端应用"""
    # 创建页面容器，设置标题与主题
    with gr.Blocks(title="企业级在线多模态对话系统", theme=gr.themes.Soft()) as demo:
        # 一级标题Markdown
        gr.Markdown("# 🏢 企业级多模态智能对话平台（Qwen3.5-Omni-Plus 阿里百炼在线版）")
        # 功能说明文案
        gr.Markdown("功能：文本对话、图片理解、语音输入、多轮上下文持久化、模型支持语音合成回复")

        # 聊天对话框组件，messages格式适配新版Gradio
        chatbot = gr.Chatbot(type="messages", height=620, label="对话窗口")
        # 多模态输入框：支持文字、麦克风录音、多文件上传
        multimodal_input = gr.MultimodalTextbox(
            file_types=["image", ".wav", ".mp3"],
            file_count="multiple",
            placeholder="输入文字 / 上传图片 / 麦克风录音",
            sources=["microphone", "upload"],
            show_label=False
        )

        # 绑定提交事件：第一步接收输入存入聊天框
        submit_event = multimodal_input.submit(
            fn=add_user_msg,
            inputs=[chatbot, multimodal_input],
            outputs=[chatbot, multimodal_input]
        )
        # 链式第二步：提交后调用在线接口获取回答
        submit_event.then(
            fn=llm_response,
            inputs=[chatbot],
            outputs=[chatbot]
        ).then(
            # 推理结束恢复输入框可交互状态
            lambda: gr.MultimodalTextbox(interactive=True),
            outputs=[multimodal_input]
        )

    return demo

# 模块内部调试启动入口
if __name__ == "__main__":
    app = build_app()
    app.launch(
        server_name=GRADIO_HOST,
        server_port=GRADIO_PORT,
        debug=False,
        inbrowser=True
    )