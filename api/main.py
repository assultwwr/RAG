from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from app import config_data as config
import os
import sys
import tempfile
import logging
# 添加项目根目录到路径
sys.path.insert(0, config.BASE_DIR)

from core.rag import RagService
from core.knowledge_base import KnowledgeBaseService, get_string_md5
from managers.database_manager import DatabaseManager
from managers.session_history_manager import SessionHistoryManager
from managers.space_manager import SpaceManager
from core.document_loader import FileLoaderFactory
from langchain_core.messages import HumanMessage, AIMessage


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG知识库API", version="1.0.0")

# CORS配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
rag_service = RagService()
knowledge_service = KnowledgeBaseService()
db_manager = DatabaseManager()
session_manager = SessionHistoryManager()
space_manager = SpaceManager()

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    session_id: str
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    """聊天响应模型"""
    answer: str
    session_id: str
    sources: List[str] = []

@app.get("/")
async def root():
    return {"message": "RAG知识库API服务正常", "version": "1.0.0"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """智能问答接口"""
    try:
        # 转换历史消息格式
        history_messages = []
        for msg in request.history:
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history_messages.append(AIMessage(content=msg["content"]))

        # 更新会话活动
        session_manager.update_session_activity(
            request.session_id,
            len(request.history) + 1
        )

        # 调用 RAG 服务获取回答
        response = rag_service.chain.invoke(
            {"input": request.message, "history": history_messages},
            config={"configurable": {"session_id": request.session_id}}
        )

        # 提取引用来源（从日志或响应中获取）
        sources = []

        return ChatResponse(
            answer=response,
            session_id=request.session_id,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """文件上传接口"""
    results = []
    try:
        logger.info(f"开始上传文件，数量：{len(files)}")

        for file in files:
            file_ext = os.path.splitext(file.filename)[1]
            logger.info(f"处理文件：{file.filename}, 类型：{file_ext}")

            # 保存临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name
                logger.info(f"临时文件路径：{tmp_path}")

            try:
                logger.info(f"开始加载文档：{file.filename}")
                # 加载文档
                loader = FileLoaderFactory.get_loader(file_path=tmp_path)
                documents = loader.load()
                logger.info(f"文档加载成功，文档数量：{len(documents)}")
                text = "\n".join([doc.page_content for doc in documents])

                # 计算MD5并上传
                file_md5 = get_string_md5(text)
                logger.info(f"计算 MD5: {file_md5}")
                result = knowledge_service.upload_by_str(text, file.filename)
                logger.info(f"知识库上传结果：{result}")

                # 记录到数据库
                if result == "数据处理完成":
                    db_manager.add_file_record(
                        filename=file.filename,
                        file_size=len(content) / 1024,
                        file_type=file.content_type,
                        chunk_count=len(documents),
                        file_md5=file_md5
                    )
                    logger.info(f"数据库记录添加成功")

                results.append({
                    "filename": file.filename,
                    "status": result,
                    "md5": file_md5
                })
            except Exception as e:
                logger.error(f"处理文件 {file.filename} 时出错：{str(e)}", exc_info=True)
                raise
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                        logger.info(f"临时文件已删除：{tmp_path}")
                    except Exception:
                        logger.error(f"无法删除临时文件 {tmp_path}")

        # 刷新向量库
        logger.info("刷新向量库")
        rag_service.refresh_vector_store()

        logger.info("上传完成")
        return {"message": "上传完成", "results": results}
    except Exception as e:
        logger.error(f"上传接口错误：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files")
async def get_files():
    """获取文件列表"""
    try:
        files = db_manager.get_all_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/files/{filename}")
async def delete_file(filename: str):
    """删除文件"""
    try:
        file_record = db_manager.get_file_by_name(filename)

        # 检查文件是否存在
        if not file_record:
            raise HTTPException(status_code=404, detail=f"文件 {filename} 不存在")

        file_md5 = file_record.get("file_md5") if file_record else None

        # 删除向量数据和MD5记录
        vector_deleted = knowledge_service.delete_by_filename_with_md5(filename, file_md5)
        record_deleted = db_manager.delete_file(filename)

        if vector_deleted and record_deleted:
            rag_service.refresh_vector_store()
            return {"message": f"文件{filename}已删除"}
        else:
            raise HTTPException(status_code=404, detail="删除失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
async def get_sessions():
    """获取会话列表"""
    try:
        sessions = session_manager.get_all_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        # 检查会话是否存在
        session = session_manager.get_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"会话{session_id}不存在")

        # 删除会话（包括文件）
        deleted = session_manager.delete_session(session_id)

        if deleted:
            return {"message": f"会话{session_id}已删除"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_statistics():
    """获取统计信息"""
    try:
        stats = space_manager.get_storage_statistics()
        return {"statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cleanup")
async def cleanup():
    """执行自动清理"""
    try:
        result = space_manager.run_auto_cleanup()
        rag_service.refresh_vector_store()
        return {"message": "清理完成", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
