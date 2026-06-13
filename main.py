from config.settings import GRADIO_HOST, GRADIO_PORT
from utils.logger import get_logger
from web.app_gradio import build_app

logger = get_logger("MainEntry")

if __name__ == '__main__':
    logger.info("启动...")

    app = build_app()
    app.launch(
        server_name=GRADIO_HOST,
        server_port=GRADIO_PORT,
        debug=False,
        inbrowser=True
    )