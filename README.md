# 🏢 企业级私有化多模态对话系统（Qwen3.5-Omni-Plus）
## 项目简介
本项目基于 **LangChain + Gradio + 阿里百炼 Qwen3.5-Omni-Plus** 构建多模态智能对话平台，支持**文本问答、图片理解、麦克风语音输入、模型语音合成回复**，采用 SQLite 实现多轮会话持久化存储，分层工程化架构设计，代码解耦易扩展，适配企业内网使用场景，规避第三方API数据泄露风险。

> 原本地大模型方案可无缝切换，预留 vLLM/SGLang 高性能推理改造入口，可对接知识库 RAG、Agent 工具编排、数字人驱动等业务模块。

## ✨ 项目亮点（简历重点）
1. **分层架构设计**：配置层、会话管理层、多模态解析层、对话链路层、Web交互层，符合企业工程规范，职责清晰易维护
2. **三模态统一交互**：封装图片/音频 Base64 编解码工具，适配通义 Omni 系列输入格式，支持上传文件 + 麦克风实时录音提问
3. **持久化多轮对话**：基于 LangChain `RunnableWithMessageHistory` + SQLite 实现会话记忆，重启程序上下文不丢失，天然支持多用户隔离
4. **健壮性设计**：全局日志收集、自定义业务异常捕获、密钥抽离配置文件，杜绝硬编码密钥泄露问题
5. **前端交互工程化**：Gradio 事件流编排完整交互流程，修复消息格式兼容性问题，规避前端渲染报错
6. **可扩展性强**：预留本地大模型部署、RAG 知识库、LangGraph 架构升级、FastAPI 接口化改造扩展入口

## 📁 完整项目目录结构
multiple_project/
├── config/ # 全局配置层
│ └── settings.py # 路径、模型参数、数据库、服务端口统一配置
├── core/ # 核心业务逻辑层
│ ├── chat_chain.py # LangChain 对话链封装、在线模型初始化、记忆链路组装
│ ├── history_manager.py # SQLite 会话历史读写、清空会话工具封装
│ └── multimodal_parser.py # 图片、音频 Base64 编码工具，适配 Qwen 多模态入参
├── utils/ # 通用工具层
│ ├── exceptions.py # 自定义异常类（模型加载、解析、会话异常）
│ └── logger.py # 全局日志工具，同时输出控制台 + 日志文件
├── web/ # Web 前端交互层
│ └── app_gradio.py # Gradio 页面布局、事件绑定、多模态交互逻辑
├── data/ # 数据持久化目录
│ └── chat.db # SQLite 会话历史数据库（自动创建）
├── logs/ # 日志存储目录
│ └── app.log # 系统运行日志
├── env_utils.py # 密钥单独存放，避免提交敏感信息
├── requirements.txt # 项目依赖清单
├── .gitignore # Git 忽略配置，屏蔽密钥、缓存、数据库、虚拟环境
├── main.py # 项目统一启动入口
└── README.md # 项目说明文档
plaintext

## 🧰 技术栈
- 编程语言：Python 3.10
- 大模型调用：LangChain + ChatOpenAI 兼容接口（阿里百炼 Qwen3.5-Omni-Plus）
- 对话编排：LangChain（提示词模板、会话记忆、链式调用）
- 前端页面：Gradio 5.x 交互式Web界面
- 数据库：SQLite（轻量持久化会话历史）
- 多媒体处理：Pillow、base64 音视频编解码
- 工程规范：日志管理、异常处理、分层架构、Git 敏感文件屏蔽

## 🚀 快速部署运行
### 1. 环境安装
```bash
# 创建虚拟环境（可选）
python -m venv .venv
.venv\Scripts\activate

# 安装全部依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
