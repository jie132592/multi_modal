import base64
import io

from PIL import Image

from utils.exceptions import MultimodalParseError
from utils.logger import get_logger

logger = get_logger("MultimodalParser")

def encode_audio_to_base64(audio_path: str) -> dict:
    """
    mp3、wav音频文件转为base64结构化字典，适配通义Qwen3.5-Omni输入格式
    :param audio_path: 音频本地路径
    :return:合模型规范的多模态消息字典
    """
    try:
        # 二进制只读打开音频文件
        with open(audio_path, "rb") as f:
            # 读取全部二进制文件
            audio_bytes = f.read()
            # 二进制转base64
            b64_str = base64.b64encode(audio_bytes).decode("utf-8")
            # 构造模型需要的要求格式
            return {
                "type": "input_audio",
                "input_audio": {
                    "data": f"data:audio/wav;base64,{b64_str}",
                    "duration": 30
                }
            }
    except Exception as e:
        logger.error(f"音频解析失败：{audio_path},err:{str(e)}")
        raise MultimodalParseError(f"音频解析异常 {e}") from e

def encode_image_to_base64(image_path: str) -> dict:
    """
    图片文件转Base64结构化字典，适配Qwen多模态输入
    :param image_path: 图片本地路径
    :return: 模型可识别图片消息结构体
    """
    try:
        with Image.open(image_path) as img:
            # 获取图片原始格式，无则jpg
            fmt = img.format if img.format else "jpg"
            # 创建内存字节缓冲区
            buf = io.BytesIO()
            # 图片写入缓冲区
            img.save(buf, format=fmt)
            # 获取缓冲区二进制数据
            img_value = buf.getvalue()
            # base64编码
            b64_str = base64.b64encode(img_value).decode("utf-8")
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{fmt};base64,{b64_str}",
                    "detail": "low"
                }
            }
    except Exception as e:
        logger.error(f"图片解析失败{image_path},err:{str(e)}")
        raise MultimodalParseError(f"图片解析异常 {e}") from e
