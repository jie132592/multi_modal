# 导入系统路径工具
import os
# 导入接口密钥配置
from env_utils import ALIBAILIAN_API_KEY, ALIBAILIAN_BASE_URL

# ===================== 全局路径配置 =====================
# 获取当前配置文件绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 拼接SQLite数据库完整路径
SQLITE_DB_PATH = os.path.join(BASE_DIR, "data", "chat.db")
# SQLAlchemy数据库连接字符串
DB_CONNECTION_STR = f"sqlite:///{SQLITE_DB_PATH}"

# ===================== 在线大模型接口配置 Qwen3.5-Omni-Plus =====================
LLM_MODEL_NAME = "qwen3.5-omni-plus"
LLM_API_KEY = ALIBAILIAN_API_KEY
LLM_BASE_URL = ALIBAILIAN_BASE_URL
# 生成参数
MAX_NEW_TOKENS = 1024
TEMPERATURE = 0.7
# 开启音频输出配置
ENABLE_AUDIO_OUTPUT = True
AUDIO_VOICE_NAME = "Ethan"
AUDIO_FORMAT = "wav"

# ===================== 会话配置 =====================
# 默认会话ID，区分不同用户上下文
DEFAULT_SESSION_ID = "business_user_001"
# 数据库存储会话消息表名
TABLE_NAME = "t_session_history"

# ===================== Gradio服务配置 =====================
# 0.0.0.0允许局域网其他设备访问页面
GRADIO_HOST = "127.0.0.1"
# Web服务端口
GRADIO_PORT = 7860
# 服务名置空
GRADIO_SERVER_NAME = None
# 关闭调试模式，生产环境更安全
GRADIO_DEBUG = False

# ===================== 环境变量屏蔽无用警告 =====================
# 关闭Windows软链接冗余提示
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
# 关闭transformers版本废弃提示
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)