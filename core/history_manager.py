from langchain_community.chat_message_histories import SQLChatMessageHistory

from config.settings import TABLE_NAME, DB_CONNECTION_STR
from utils.exceptions import ChatHistoryError
from utils.logger import get_logger

logger = get_logger("historyManager")

def get_session_history(session_id: str) -> SQLChatMessageHistory:
    """
    根据会话id获取该用户的全部历史消息实例
    :param session_id:会话id
    :return:SQL会话历史管理对象
    """
    try:
        return SQLChatMessageHistory(
            session_id=session_id,
            table_name=TABLE_NAME,
            connection=DB_CONNECTION_STR
        )
    except Exception as e:
        logger.error(f"会话id{session_id}历史初始化失败{str(e)}")
        raise ChatHistoryError(f"会话历史读取异常: {e}") from e

def clear_session_history(session_id: str):
    """
    清空指定会话历史聊天记录
    :param session_id:会话id
    :return:
    """
    # 获取会话实例
    history = get_session_history(session_id)
    # 清空该数据库内所有会话消息
    history.clear()
    logger.info(f"会话已清空{session_id}")