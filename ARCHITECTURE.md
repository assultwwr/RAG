# RAG知识库智能问答系统 - 项目架构文档

## 📋 项目概述

基于 LangChain + FastAPI + Streamlit 构建的企业级知识库智能问答系统，支持多格式文档上传、混合检索、智能问答、会话管理等功能。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     用户界面层 (UI Layer)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Streamlit Web 前端 (8501端口)             │   │
│  │  • 智能问答页面    • 文件上传页面    • 知识库管理       │   │
│  │  • 会话历史页面    • 空间管理页面                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                   API 服务层 (API Layer)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            FastAPI 后端服务 (8000端口)                 │   │
│  │  • /api/chat      - 智能问答接口                      │   │
│  │  • /api/upload    - 文件上传接口                      │   │
│  │  • /api/files     - 文件管理接口                      │   │
│  │  • /api/sessions  - 会话管理接口                      │   │
│  │  • /api/stats     - 统计信息接口                      │   │
│  │  • /api/cleanup   - 数据清理接口                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↕ 业务逻辑调用
┌─────────────────────────────────────────────────────────────┐
│                  核心业务层 (Core Layer)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  RAG引擎     │  │  知识库服务   │  │  向量存储服务    │   │
│  │  rag.py      │  │knowledge_base│  │vector_stores.py │   │
│  │              │  │   .py        │  │                 │   │
│  │• 混合检索    │  │• MD5去重     │  │• ChromaDB封装   │   │
│  │• 重排序优化  │  │• 文档分块    │  │• 检索器管理     │   │
│  │• 上下文压缩  │  │• 向量化存储  │  │• 文档转换       │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           文档加载工厂 (document_loader.py)            │   │
│  │  • PDF/Word/TXT 多格式支持                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↕ 数据访问
┌─────────────────────────────────────────────────────────────┐
│                  数据管理层 (Manager Layer)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ 数据库管理器  │  │ 会话历史管理器│  │  空间管理器      │   │
│  │database_mana-│  │session_histo-│  │space_manager.py │   │
│  │ger.py        │  │ry_manager.py │  │                 │   │
│  │              │  │              │  │                 │   │
│  │• 文件元数据  │  │• 会话记录    │  │• 自动清理策略   │   │
│  │• 访问统计    │  │• 活动追踪    │  │• 过期检测       │   │
│  │• 状态管理    │  │• 历史查询    │  │• 空间统计       │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↕ 数据存储
┌─────────────────────────────────────────────────────────────┐
│                   数据存储层 (Storage Layer)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ ChromaDB     │  │ JSON数据库   │  │  模型文件        │   │
│  │(向量数据库)   │  │(元数据存储)  │  │                 │   │
│  │              │  │              │  │                 │   │
│  │• 文档向量    │  │• file_meta-  │  │• BGE-Reranker  │   │
│  │• 语义索引    │  │  data.json   │  │  v2-m3         │   │
│  │• 混合检索    │  │• session_    │  │• Qwen Embedding│   │
│  │              │  │  metadata    │  │• Qwen2.5:7b    │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↕ 外部服务
┌─────────────────────────────────────────────────────────────┐
│                  外部依赖服务 (External Services)             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Ollama LLM 服务 (11434端口)               │   │
│  │  • qwen3-embedding  (嵌入模型)                        │   │
│  │  • qwen2.5:7b       (对话模型)                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构详解

```
RAG知识库智能问答系统/
│
├── api/                          # 【API接口层】FastAPI 路由与端点
│   ├── __init__.py
│   └── main.py                   # FastAPI 主应用，定义所有 REST API
│                                 #   • POST /api/chat - 智能问答
│                                 #   • POST /api/upload - 文件上传
│                                 #   • GET /api/files - 获取文件列表
│                                 #   • DELETE /api/files/{filename} - 删除文件
│                                 #   • GET /api/sessions - 获取会话列表
│                                 #   • DELETE /api/sessions/{session_id} - 删除会话
│                                 #   • GET /api/stats - 统计信息
│                                 #   • POST /api/cleanup - 执行清理
│
├── app/                          # 【应用层】Streamlit 前端应用
│   ├── __init__.py
│   ├── config_data.py            # 全局配置文件（模型路径、服务地址等）
│   ├── main.py                   # Streamlit 主应用入口
│   └── page_modules/             # 前端页面模块
│       ├── __init__.py
│       ├── qa_page.py            # 智能问答页面
│       ├── upload_page.py        # 文件上传页面
│       ├── knowledge_page.py     # 知识库管理页面
│       ├── history_page.py       # 会话历史页面
│       └── space_page.py         # 空间管理页面
│
├── core/                         # 【核心业务层】RAG 核心逻辑
│   ├── __init__.py
│   ├── rag.py                    # RAG 检索增强生成引擎
│   │                             #   • 混合检索（向量+BM25）
│   │                             #   • CrossEncoder 重排序
│   │                             #   • 上下文压缩
│   │                             #   • 多轮对话链构建
│   ├── knowledge_base.py         # 知识库服务
│   │                             #   • MD5 去重机制
│   │                             #   • 文档分块与向量化
│   │                             #   • 向量数据增删查
│   ├── vector_stores.py          # 向量存储服务
│   │                             #   • ChromaDB 封装
│   │                             #   • 检索器管理
│   │                             #   • 文档批量加载
│   ├── document_loader.py        # 文档加载工厂
│   │                             #   • PDF/Word/TXT 多格式支持
│   │                             #   • 动态扩展机制
│   └── message_history_store.py  # 消息历史存储
│
├── managers/                     # 【数据管理层】数据持久化与管理
│   ├── __init__.py
│   ├── database_manager.py       # 文件元数据管理
│   │                             #   • 文件记录 CRUD
│   │                             #   • 访问时间与次数追踪
│   │                             #   • 过期文件检测
│   │                             #   • 统计分析
│   ├── session_history_manager.py # 会话历史管理
│   │                             #   • 会话记录管理
│   │                             #   • 活动追踪
│   │                             #   • 过期会话清理
│   └── space_manager.py          # 空间管理与自动清理
│                                 #   • 清理策略配置
│                                 #   • 自动清理任务
│                                 #   • 存储空间统计
│
├── data/                         # 【数据存储目录】运行时数据
│   ├── chroma_db/                # ChromaDB 向量数据库
│   ├── database/                 # JSON 元数据数据库
│   │   └── file_metadata.json    # 文件元数据记录
│   ├── chat_history/             # 会话历史记录
│   │   └── session_metadata.json # 会话元数据
│   ├── config/                   # 配置文件
│   │   └── cleanup_policy.json   # 清理策略配置
│   ├── logs/                     # 日志文件
│   │   └── space_manager.log     # 空间管理日志
│   └── md5.text                  # MD5 去重记录
│
├── models/                       # 【模型文件目录】本地 AI 模型
│   └── BAAI-bge-reranker-v2-m3/  # BGE 重排序模型
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       └── ...
│
├── test/                         # 【测试目录】测试文件
│   ├── 1.txt
│   └── 2.txt
│
├── Dockerfile                    # Docker 镜像构建文件
├── docker-compose.yml            # Docker Compose 编排配置
├── init-ollama.bat               # Ollama 模型初始化脚本（Windows）
├── requirements.txt              # Python 依赖包清单
├── start_api.bat                 # 启动 API 服务脚本
├── start_streamlit.bat           # 启动 Streamlit 前端脚本
├── README.md                     # 项目说明文档
└── 项目经历.md                   # 项目经验总结
```

---

## 🔧 核心技术栈

### 后端技术
- **Web框架**: FastAPI 0.135.1
- **ASGI服务器**: Uvicorn
- **AI框架**: LangChain 1.x (langchain-core, langchain-classic, langchain-community)
- **向量数据库**: ChromaDB 1.5.5
- **LLM服务**: Ollama (qwen2.5:7b, qwen3-embedding)
- **重排序模型**: BAAI/bge-reranker-v2-m3 (HuggingFace CrossEncoder)

### 前端技术
- **Web框架**: Streamlit 1.51.0

### 数据处理
- **文档解析**: 
  - PyPDF 4.0.0 (PDF)
  - python-docx 1.1.0 (Word)
  - TextLoader (TXT)
- **文本分割**: RecursiveCharacterTextSplitter
- **关键词检索**: rank-bm25

### 部署运维
- **容器化**: Docker + Docker Compose
- **数据存储**: JSON (轻量级元数据存储)

---

## 🔄 核心工作流程

### 1. 文档上传流程
```
用户上传文件
    ↓
FileLoaderFactory 根据文件类型选择加载器
    ↓
加载文档内容 → 计算MD5哈希值
    ↓
检查MD5是否已存在（去重）
    ↓
RecursiveCharacterTextSplitter 分块处理
    ↓
OllamaEmbeddings 向量化
    ↓
ChromaDB 存储向量 + 元数据
    ↓
DatabaseManager 记录文件元数据
    ↓
保存MD5到 md5.text
    ↓
刷新向量库连接
```

### 2. 智能问答流程
```
用户输入问题
    ↓
RagService 接收请求
    ↓
EnsembleRetriever 混合检索
    ├─ VectorRetriever (向量相似度检索)
    └─ BM25Retriever (关键词检索)
    ↓
CrossEncoderReranker 重排序（Top-5）
    ↓
ContextualCompressionRetriever 上下文压缩
    ↓
格式化检索结果为 Prompt Context
    ↓
ChatPromptTemplate 构建提示词
    ├─ System: 角色设定 + 参考资料
    ├─ History: 历史对话记录
    └─ User: 当前问题
    ↓
ChatOllama (qwen2.5:7b) 生成回答
    ↓
StrOutputParser 解析输出
    ↓
更新文件访问记录
    ↓
返回答案给前端
```

### 3. 会话管理流程
```
创建新会话
    ↓
生成 UUID 作为 session_id
    ↓
SessionHistoryManager 创建会话记录
    ↓
每次对话更新 last_activity_time
    ↓
RunnableWithMessageHistory 管理对话历史
    ↓
定期清理过期会话（默认30天）
```

### 4. 自动清理流程
```
应用启动时触发
    ↓
SpaceManager 加载清理策略配置
    ↓
扫描 DatabaseManager 中的文件记录
    ├─ 检查 last_access_time
    └─ 标记超过保留期的文件（默认90天）
    ↓
扫描 SessionHistoryManager 中的会话记录
    ├─ 检查 last_activity_time
    └─ 标记超过保留期的会话（默认30天）
    ↓
执行删除操作
    ├─ 从 ChromaDB 删除向量数据
    ├─ 从 DatabaseManager 删除元数据
    ├─ 删除 MD5 记录
    └─ 删除会话文件
    ↓
记录清理日志
    ↓
刷新向量库连接
```

---

## 🎯 关键设计模式

### 1. 工厂模式 (Factory Pattern)
**实现位置**: `core/document_loader.py` - `FileLoaderFactory`

```python
# 根据文件扩展名动态创建对应的文档加载器
loader = FileLoaderFactory.get_loader(file_path="document.pdf")
```

**优势**:
- 解耦文件类型与加载逻辑
- 易于扩展新的文件格式
- 统一的接口规范

### 2. 服务层模式 (Service Layer Pattern)
**实现位置**: 
- `core/rag.py` - `RagService`
- `core/knowledge_base.py` - `KnowledgeBaseService`

**职责分离**:
- RagService: 负责检索增强生成的完整链路
- KnowledgeBaseService: 负责知识库的增删改查

### 3. 管理器模式 (Manager Pattern)
**实现位置**: `managers/` 目录下的所有 Manager 类

**职责**:
- DatabaseManager: 文件元数据持久化
- SessionHistoryManager: 会话生命周期管理
- SpaceManager: 资源清理与统计

### 4. 责任链模式 (Chain of Responsibility)
**实现位置**: `core/rag.py` - LangChain Runnable 链

```python
basic_chain = (
    {"input": RunnablePassthrough(),
     "context": retriever | format_document}
    | prompt_template 
    | chat_model 
    | output_parser
)
```

---

## 📊 数据流图

### 文件上传数据流
```
[用户上传] → [临时文件] → [文档加载器] → [文本内容]
                                              ↓
                                         [MD5计算]
                                              ↓
                                      [MD5去重检查]
                                              ↓
                                         [文本分块]
                                              ↓
                                        [向量嵌入]
                                              ↓
                                    [ChromaDB存储] ←→ [元数据记录]
                                              ↓
                                       [MD5记录保存]
```

### 问答检索数据流
```
[用户问题] → [RagService] → [混合检索器]
                                  ↓
                          ┌───────┴───────┐
                          ↓               ↓
                   [向量检索器]      [BM25检索器]
                          ↓               ↓
                          └───────┬───────┘
                                  ↓
                          [结果合并加权]
                                  ↓
                          [CrossEncoder重排序]
                                  ↓
                          [上下文压缩过滤]
                                  ↓
                          [格式化Prompt Context]
                                  ↓
                          [LLM生成回答]
                                  ↓
                          [更新访问记录]
                                  ↓
                          [返回答案]
```

---

## 🔐 安全与性能优化

### 安全性
1. **CORS配置**: 限制跨域访问来源
2. **MD5去重**: 防止重复文件占用存储空间
3. **临时文件清理**: 上传后立即删除临时文件
4. **输入验证**: Pydantic 模型验证请求参数

### 性能优化
1. **混合检索**: 向量检索 + BM25 关键词检索，提升召回率
2. **重排序优化**: CrossEncoder 对候选文档精排，提升准确率
3. **上下文压缩**: 过滤无关文档片段，减少 Token 消耗
4. **向量库刷新**: 增量更新而非全量重建
5. **懒加载**: 首次使用时才初始化服务实例

### 可扩展性
1. **插件式文档加载器**: 通过 `register_loader()` 动态注册新格式
2. **可配置清理策略**: JSON 配置文件控制保留期限
3. **模块化架构**: 各层职责清晰，易于替换组件

---

## 🚀 部署架构

### Docker 容器化部署
```yaml
服务组成:
  1. rag-knowledge-base (主应用容器)
     ├─ FastAPI 后端 (8000端口)
     ├─ Streamlit 前端 (8501端口)
     └─ 挂载卷: ./models:/app/models
  
  2. ollama-service (LLM服务容器)
     ├─ Ollama Server (11434端口)
     └─ 持久化卷: ollama_data:/root/.ollama

网络: rag-network (桥接网络)
```

### 环境变量
```bash
OLLAMA_HOST=http://ollama:11434  # Ollama 服务地址
TZ=Asia/Shanghai                  # 时区设置
```

---

## 📈 监控与日志

### 日志系统
- **空间管理日志**: `data/logs/space_manager.log`
- **日志级别**: INFO
- **日志格式**: `%(asctime)s - %(levelname)s - %(message)s`

### 统计指标
通过 `/api/stats` 接口获取:
- 文件总数、活跃文件数、总大小
- 会话总数、活跃会话数、总消息数
- ChromaDB 大小、聊天历史大小
- 存储空间总计

---

## 🛠️ 开发指南

### 添加新文档格式支持
```python
# 在 core/document_loader.py 中注册
from langchain_community.document_loaders import NewTypeLoader

FileLoaderFactory.register_loader(".newext", NewTypeLoader)
```

### 自定义检索策略
```python
# 在 core/rag.py 中修改 __get_chain() 方法
# 调整 EnsembleRetriever 权重
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, BM25_retriever], 
    weights=[0.7, 0.3]  # 调整权重比例
)
```

### 调整清理策略
```python
# 通过 API 或修改 data/config/cleanup_policy.json
{
  "file_retention_days": 60,      # 文件保留60天
  "session_retention_days": 15    # 会话保留15天
}
```

---

## 📝 版本历史

### v1.0.0 (2026-03-19)
- ✅ 初始版本发布
- ✅ Docker 容器化部署
- ✅ 混合检索功能（向量+BM25）
- ✅ CrossEncoder 重排序优化
- ✅ 会话管理功能
- ✅ 自动清理机制
- ✅ 多格式文档支持（PDF/Word/TXT）

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 代码规范
- 遵循 PEP 8 Python 编码规范
- 使用类型注解
- 添加必要的注释和文档字符串

### 提交流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License

---

## 🙏 致谢

感谢以下开源项目:
- [LangChain](https://github.com/langchain-ai/langchain) - AI 应用开发框架
- [FastAPI](https://github.com/tiangolo/fastapi) - 高性能 Web 框架
- [Streamlit](https://github.com/streamlit/streamlit) - 快速构建数据应用
- [Ollama](https://github.com/ollama/ollama) - 本地 LLM 服务
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [BAAI/bge-reranker](https://huggingface.co/BAAI/bge-reranker-v2-m3) - 重排序模型

---

**🎉 开始使用 RAG 知识库智能问答系统吧！**
