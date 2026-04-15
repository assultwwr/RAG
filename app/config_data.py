import os

# 根目录绝对路径
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

md5_path = os.path.join(BASE_DIR, "data", "md5.text")
config_file = os.path.join(BASE_DIR, "data", "config", "cleanup_policy.json")

# API配置
api_host = "0.0.0.0"
api_port = 8000
streamlit_url = "http://localhost:8501"

# Chroma
collection_name = "RAG"
persist_directory = os.path.join(BASE_DIR, "data", "chroma_db")

# spliter
chunk_size = 500
chunk_overlap = 50
separators = ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
min_split_char_number = chunk_size # 文本分割的阈值，小于这个数就不做分割

similarity_threshold = 10 # 检索返回文档数量

embeddings_model_name = "qwen3-embedding"
chat_model_name = "qwen2.5:7b"

# Ollama服务地址（Docker环境）
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# 根据运行环境自动切换模型路径
# 优先级：Docker环境 > 本地models目录 > HuggingFace在线下载
LOCAL_MODEL_PATH = os.path.join(BASE_DIR, "models", "BAAI-bge-reranker-v2-m3")

if os.path.exists("/app/models/BAAI-bge-reranker-v2-m3"):
    # Docker 环境
    RERANKER_MODEL_PATH = "/app/models/BAAI-bge-reranker-v2-m3"
    RERANKER_DEVICE = "cpu"
elif os.path.exists(LOCAL_MODEL_PATH):
    # 本地环境（动态路径，支持任意目录）
    RERANKER_MODEL_PATH = LOCAL_MODEL_PATH
    RERANKER_DEVICE = "cuda"  # 有 GPU 用 "cuda"，否则改为 "cpu"
else:
    # 默认使用HuggingFace模型ID（从网络自动下载）
    RERANKER_MODEL_PATH = "BAAI/bge-reranker-v2-m3"
    RERANKER_DEVICE = "cpu"