from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from config.settings import LLM_MODEL_NAME, LLM_API_KEY, LLM_BASE_URL, TEMPERATURE, ENABLE_AUDIO_OUTPUT, \
    AUDIO_VOICE_NAME, AUDIO_FORMAT
from core.history_manager import get_session_history
from utils.logger import get_logger

logger = get_logger("chat_chain")

# 初始化在线模型
llm = ChatOpenAI(
    model=LLM_MODEL_NAME,
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
    streaming=True,  # 开启流式输出
    temperature=TEMPERATURE,
    # 透传给阿里百炼扩展参数，开启语音返回
    extra_body={
        "modalities": ["text", "audio"] if ENABLE_AUDIO_OUTPUT else ["text"],
        "audio": {"voice": AUDIO_VOICE_NAME, "format": AUDIO_FORMAT} if ENABLE_AUDIO_OUTPUT else None
    }
)

# 构建对话提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是专业的多模态智能助手，能够精准理解文本、图片、语音输入，回答专业简洁，支持多轮上下文记忆。"),
    # 历史消息占位符
    MessagesPlaceholder(variable_name="messages")
])

# 基础执行链
base_chain = prompt | llm | StrOutputParser()

# 封装带会话历史的完整链路(实现多轮对话记忆的封装类)
# 自动帮你管理聊天上下文，不用自己手动拼接历史消息、不用手动读写数据库，实现自然多轮聊天
chat_chain_with_history = RunnableWithMessageHistory(
    runnable=base_chain,
    # 传入一个函数，这个函数接收 session_id，返回这个用户的全部历史消息对象
    get_session_history=get_session_history,
    # 字符串配置，必须和你 Prompt 里占位符变量名完全对应
    input_messages_key="messages"
)