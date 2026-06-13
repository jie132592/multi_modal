class ModelLoadError(Exception):
    """自定义异常：模型加载失败异常（预留，切本地模型可用）"""
    pass

class MultimodalParseError(Exception):
    """自定义异常：图片/音频多模态文件解析失败异常"""
    pass

class ChatHistoryError(Exception):
    """自定义异常：会话历史数据库读写异常"""
    pass