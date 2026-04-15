# RAG 知识库智能问答系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135.1-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.51.0-red.svg)
![LangChain](https://img.shields.io/badge/LangChain-1.x-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**基于 LangChain + FastAPI + Streamlit 构建的企业级知识库智能问答系统**

[📖 项目架构文档](ARCHITECTURE.md) | [🚀 快速开始](#-快速开始) | [📚 使用说明](#-使用说明)

</div>

---

## 一、项目简介

RAG 知识库智能问答系统是一个功能完整的企业级知识管理解决方案，支持多格式文档上传、智能检索、多轮对话等功能。系统采用前后端分离架构，结合向量检索与关键词检索的混合检索策略，通过重排序模型优化检索结果，提供精准的问答体验。

### ✨ 核心特性

- 📚 **多格式文档支持** - 支持 PDF、Word、TXT 等多种格式文档上传与解析
- 🔍 **混合检索引擎** - 向量检索 + BM25 关键词检索，提升召回率
- 🎯 **智能重排序** - 使用 BGE-Reranker 对检索结果精排，提升准确率
- 💬 **多轮对话** - 基于 LangChain 的会话管理，支持上下文理解
- 🗄️ **知识库管理** - MD5 去重机制，自动清理过期数据
- 📊 **空间管理** - 实时监控存储使用情况，可配置清理策略
- 🐳 **一键部署** - Docker 容器化部署，开箱即用

## 二、技术栈

### 后端技术
- **Web 框架**: FastAPI 0.135.1 + Uvicorn
- **AI 框架**: LangChain 1.x (langchain-core, langchain-classic, langchain-community)
- **向量数据库**: ChromaDB 1.5.5
- **LLM 服务**: Ollama (qwen2.5:7b, qwen3-embedding)
- **重排序模型**: BAAI/bge-reranker-v2-m3

### 前端技术
- **Web 框架**: Streamlit 1.51.0

### 数据处理
- **文档解析**: PyPDF 4.0.0 (PDF), python-docx 1.1.0 (Word), TextLoader (TXT)
- **文本分割**: RecursiveCharacterTextSplitter
- **关键词检索**: rank-bm25

### 部署运维
- **容器化**: Docker + Docker Compose
- **数据存储**: JSON (轻量级元数据存储)

## 三、快速开始

### 方式一：Docker 部署（推荐 ⭐）

#### 1️⃣ 环境要求

- Docker Desktop 20+ 
- 8GB+ 内存
- 20GB+ 磁盘空间

#### 2️⃣ 部署步骤

**步骤 1：获取项目代码**

方式一：克隆仓库（推荐）
```bash
git clone <repository-url>
cd RAG知识库智能问答系统
```

方式二：下载 ZIP 包
- 从 GitHub/Gitee 下载项目压缩包
- 解压到任意目录
- 进入项目根目录

**步骤 2：初始化 Ollama 模型（首次运行必需）**
```powershell
# Windows 系统
.\init-ollama.bat

# Linux/Mac 系统
chmod +x init-ollama.sh
./init-ollama.sh
```

> ⏱️ **首次下载需要 10-30 分钟，总共约 5-10GB**

**步骤 3：启动服务**
```powershell
docker-compose up -d
```

**步骤 4：查看日志**
```powershell
docker-compose logs -f
```

**步骤 5：访问系统**

浏览器打开：**http://localhost:8501**

#### 3️⃣ 常用命令

```powershell
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f rag-knowledge-base
```


### 方式二：本地部署

#### 1️⃣ 环境要求

- Python 3.10+
- Ollama 0.1.40+

#### 2️⃣ 安装依赖

```powershell
# 安装 Python 依赖
pip install -r requirements.txt

# 下载 Ollama 模型
ollama pull qwen3-embedding
ollama pull qwen2.5:7b
```

#### 3️⃣ 配置模型路径（可选）

**注意：** `config_data.py` 已实现自动检测机制，通常无需手动配置。

如需自定义配置，编辑 `app/config_data.py`：

```python
# 方式一：使用本地 models 目录（推荐）
# 将模型文件放在项目根目录的 models/ 文件夹下
# 系统会自动检测：<项目根目录>/models/BAAI-bge-reranker-v2-m3
RERANKER_DEVICE = "cuda"  # 有 GPU 用 "cuda"，否则用 "cpu"

# 方式二：从 HuggingFace 自动下载（无需本地模型）
# 如果 models/ 目录不存在，系统会自动从网络下载
RERANKER_MODEL_PATH = "BAAI/bge-reranker-v2-m3"
RERANKER_DEVICE = "cpu"

# Docker 环境会自动使用 /app/models/BAAI-bge-reranker-v2-m3
```

**模型文件获取方式：**
- 从 HuggingFace 下载：https://huggingface.co/BAAI/bge-reranker-v2-m3
- 或使用国内镜像：https://hf-mirror.com/BAAI/bge-reranker-v2-m3

#### 4️⃣ 启动服务

```powershell
# 终端 1：启动后端 API
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# 终端 2：启动前端（新窗口）
streamlit run app/main.py --server.address=0.0.0.0 --server.port=8501
```

或者使用提供的批处理脚本：
```powershell
# Windows 系统
.\start_api.bat        # 启动后端
.\start_streamlit.bat  # 启动前端
```


## 四、目录结构

```
RAG知识库智能问答系统/
├── api/                    # API 接口层（FastAPI）
│   ├── __init__.py
│   └── main.py            # FastAPI 主应用，定义所有 REST API
├── app/                    # 应用层（Streamlit 前端）
│   ├── __init__.py
│   ├── config_data.py     # 全局配置文件
│   ├── main.py            # Streamlit 主应用入口
│   └── page_modules/      # 前端页面模块
│       ├── qa_page.py     # 智能问答页面
│       ├── upload_page.py # 文件上传页面
│       ├── knowledge_page.py  # 知识库管理页面
│       ├── history_page.py    # 会话历史页面
│       └── space_page.py      # 空间管理页面
├── core/                   # 核心业务层（RAG 引擎）
│   ├── __init__.py
│   ├── rag.py             # RAG 检索增强生成引擎
│   ├── knowledge_base.py  # 知识库服务（MD5去重、向量化）
│   ├── vector_stores.py   # 向量存储服务（ChromaDB封装）
│   ├── document_loader.py # 文档加载工厂（PDF/Word/TXT）
│   └── message_history_store.py  # 消息历史存储
├── managers/               # 数据管理层
│   ├── __init__.py
│   ├── database_manager.py       # 文件元数据管理
│   ├── session_history_manager.py # 会话历史管理
│   └── space_manager.py          # 空间管理与自动清理
├── data/                   # 数据存储目录
│   ├── chroma_db/         # ChromaDB 向量数据库
│   ├── database/          # JSON 元数据数据库
│   │   └── file_metadata.json
│   ├── chat_history/      # 会话历史记录
│   │   └── session_metadata.json
│   ├── config/            # 配置文件
│   │   └── cleanup_policy.json
│   ├── logs/              # 日志文件
│   │   └── space_manager.log
│   └── md5.text           # MD5 去重记录
├── models/                 # 模型文件
│   └── BAAI-bge-reranker-v2-m3/  # BGE 重排序模型
├── test/                   # 测试文件
├── docker-compose.yml      # Docker 编排配置
├── Dockerfile              # Docker 镜像配置
├── init-ollama.bat         # Ollama 模型初始化脚本（Windows）
├── requirements.txt        # Python 依赖
├── ARCHITECTURE.md         # 详细架构文档
└── README.md              # 项目说明文档
```

> 📖 **查看详细架构设计**: [ARCHITECTURE.md](ARCHITECTURE.md)


## 五、使用说明

### 1️、上传文档

1. 进入左侧导航栏选择 **"📁 文件上传"**
2. 点击上传区域或拖拽文件
3. 支持格式：PDF、Word (.docx)、TXT
4. 系统自动进行文档分块和向量化
5. 上传完成后在 **"🗄️ 知识库管理"** 查看文件列表

### 2️、智能问答

1. 进入左侧导航栏选择 **"💬 智能问答"**
2. 在对话框输入问题
3. 系统自动检索相关知识并生成答案
4. 支持多轮对话，上下文连贯
5. 点击 **"新会话"** 按钮开启新对话

### 3️、知识库管理

1. 进入 **"🗄️ 知识库管理"** 页面
2. 查看所有已上传文件及元数据
3. 支持删除单个文件
4. 查看文件访问统计信息

### 4️、会话历史

1. 进入 **"💭 会话历史"** 页面
2. 查看所有历史会话记录
3. 支持删除指定会话
4. 查看会话消息数量和最后活动时间

### 5️、空间管理

1. 进入 **"⚙️ 空间管理"** 页面
2. 查看存储空间使用情况
3. 配置清理策略（文件/会话保留天数）
4. 手动执行清理任务
5. 查看清理历史记录

## 六、配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `OLLAMA_HOST` | Ollama 服务地址 | `http://localhost:11434` | `http://ollama:11434` (Docker) |
| `TZ` | 时区设置 | `Asia/Shanghai` | `UTC` |

### 核心配置项

在 `app/config_data.py` 中配置：

```python
# 模型配置
embeddings_model_name = "qwen3-embedding"  # 嵌入模型
chat_model_name = "qwen2.5:7b"             # 对话模型

# 文本分块配置
chunk_size = 500        # 分块大小
chunk_overlap = 50      # 重叠字符数

# 检索配置
similarity_threshold = 10  # 检索返回文档数量

# 重排序模型（自动检测，无需手动配置）
# 优先级：Docker环境 > 本地models目录 > HuggingFace在线下载
# RERANKER_MODEL_PATH = "BAAI/bge-reranker-v2-m3"  # 可选：强制使用在线模型
RERANKER_DEVICE = "cpu"      # cpu 或 cuda（根据硬件调整）
```

### 清理策略配置

在 `data/config/cleanup_policy.json` 中配置：

```json
{
  "file_retention_days": 90,      // 文件保留天数
  "session_retention_days": 30    // 会话保留天数
}
```

或在 **"⚙️ 空间管理"** 页面动态调整。

## 七、常见问题

### Q1: Ollama 模型下载失败

**解决方案：** 使用国内镜像源

```powershell
# Windows PowerShell
$env:OLLAMA_MIRROR="https://hf-mirror.com"
ollama pull qwen3-embedding

# 或在 init-ollama.bat 中添加环境变量
set OLLAMA_MIRROR=https://hf-mirror.com
```

### Q2: Docker 容器启动失败

**检查步骤：**

```powershell
# 查看容器日志
docker logs rag-knowledge-base --tail 100

# 查看 Ollama 服务日志
docker logs ollama-service --tail 100

# 检查容器状态
docker-compose ps

# 重启服务
docker-compose restart

# 完全重建
docker-compose down -v
docker-compose up -d --build
```

### Q3: Rerank 模型加载失败

**解决方案：**

1. 确认模型文件存在于 `models/BAAI-bge-reranker-v2-m3/` 目录
2. 检查 `app/config_data.py` 中的路径配置是否正确
3. 确认依赖包已安装：`pip install sentence-transformers`
4. 如果使用 GPU，确认 CUDA 驱动已正确安装

### Q4: 端口被占用

**修改端口：**

编辑 `docker-compose.yml`：

```yaml
services:
  rag-knowledge-base:
    ports:
      - "8001:8000"  # 修改 API 端口映射
      - "8502:8501"  # 修改前端端口映射
```

然后重启：
```powershell
docker-compose down
docker-compose up -d
```

### Q5: 检索结果不准确

**优化建议：**

1. **调整检索参数**：在 `core/rag.py` 中修改权重
   ```python
   ensemble_retriever = EnsembleRetriever(
       retrievers=[vector_retriever, BM25_retriever], 
       weights=[0.7, 0.3]  # 调整向量检索和关键词检索的权重
   )
   ```

2. **优化文本分块**：在 `app/config_data.py` 中调整
   ```python
   chunk_size = 300      # 减小分块大小，提高精度
   chunk_overlap = 30    # 适当减小重叠
   ```

3. **更换更强大的模型**：
   ```python
   chat_model_name = "qwen2.5:14b"  # 使用更大的模型
   ```

### Q6: 内存不足

**解决方案：**

1. 使用 CPU 而非 GPU 运行重排序模型
2. 减小 `chunk_size` 和 `similarity_threshold`
3. 定期清理过期数据和会话
4. 增加 Docker 容器的内存限制


## 八、性能优化建议

### 1. 使用 GPU 加速

如果有 NVIDIA GPU，可以启用 CUDA 加速重排序模型：

```python
# app/config_data.py
RERANKER_DEVICE = "cuda"
```

Docker 部署时需要添加 GPU 支持：
```yaml
# docker-compose.yml
services:
  rag-knowledge-base:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 2. 调整批处理大小

根据文档大小调整分块参数：

```python
# app/config_data.py
chunk_size = 256      # 小文档用小分块，大文档用大分块
chunk_overlap = 25    # 保持 10% 左右的重叠
```

### 3. 优化向量检索

- 使用 HNSW 索引加速检索（ChromaDB 默认启用）
- 定期优化 ChromaDB 索引：
  ```python
  # 在代码中调用
  vector_store.collection.optimize()
  ```

### 4. 缓存策略

- 频繁查询的问题可以添加缓存层（如 Redis）
- 向量嵌入结果可以缓存，避免重复计算

### 5. 异步处理

- 文件上传和向量化可以改为异步任务队列（Celery）
- 大批量文档处理时使用后台任务

## 九、开发指南

### 添加新的文档处理器

在 `core/document_loader.py` 中注册新的文件格式：

```python
from langchain_community.document_loaders import NewTypeLoader

# 注册新格式
FileLoaderFactory.register_loader(".xlsx", ExcelLoader)
FileLoaderFactory.register_loader(".pptx", PowerPointLoader)
```

### 自定义检索策略

在 `core/rag.py` 的 `__get_chain()` 方法中修改：

```python
# 调整混合检索权重
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, BM25_retriever], 
    weights=[0.7, 0.3]  # 向量检索权重更高
)

# 调整重排序 Top-N
compressor = CrossEncoderReranker(model=reranker_model, top_n=3)
```

### 扩展 API 接口

在 `api/main.py` 中添加新的端点：

```python
@app.get("/api/custom-endpoint")
async def custom_endpoint():
    """自定义接口"""
    return {"message": "Hello"}
```

### 自定义清理策略

在 `managers/space_manager.py` 中添加新的清理规则：

```python
def custom_cleanup_rule(self):
    """自定义清理逻辑"""
    # 实现特定的清理策略
    pass
```


## 十、更新日志

### v1.0.0 (2026-03-19)

**✨ 新功能**
- 初始版本发布
- Docker 容器化部署支持
- 混合检索功能（向量检索 + BM25 关键词检索）
- CrossEncoder 重排序优化
- 会话管理功能（多轮对话、历史记录）
- 知识库管理（文件上传、删除、MD5 去重）
- 自动清理机制（可配置保留策略）
- 多格式文档支持（PDF、Word、TXT）
- 空间管理面板（实时监控、统计分析）

**🔧 技术亮点**
- 采用前后端分离架构（FastAPI + Streamlit）
- 模块化设计，易于扩展和维护
- 完善的日志系统和错误处理
- 支持本地和 Docker 两种部署方式

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 代码规范
- 遵循 PEP 8 Python 编码规范
- 使用类型注解（Type Hints）
- 添加必要的注释和文档字符串
- 保持代码简洁和可读性

### 提交流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 报告问题
- 使用 GitHub Issues 报告 bug 或提出新功能建议
- 提供详细的复现步骤和环境信息
- 附上相关的日志或截图

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢以下优秀的开源项目：

- [LangChain](https://github.com/langchain-ai/langchain) - AI 应用开发框架
- [FastAPI](https://github.com/tiangolo/fastapi) - 高性能 Web 框架
- [Streamlit](https://github.com/streamlit/streamlit) - 快速构建数据应用
- [Ollama](https://github.com/ollama/ollama) - 本地 LLM 服务
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [BAAI/bge-reranker](https://huggingface.co/BAAI/bge-reranker-v2-m3) - 重排序模型

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

**🎉 开始使用 RAG 知识库智能问答系统吧！**

</div>