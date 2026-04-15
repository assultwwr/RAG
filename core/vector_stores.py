import logging
from langchain_chroma import Chroma
from app import config_data as config
from langchain_core.documents import Document
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class VectorStoreService(object):
    def __init__(self, embedding):
        self.embedding = embedding
        self.logger = logging.getLogger(__name__)
        self.vector_store = Chroma(
            persist_directory=config.persist_directory,
            embedding_function=self.embedding,
            collection_name=config.collection_name,
            client_settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True,
                persist_directory=config.persist_directory
            )
        )

    def get_retriever(self):
        """返回向量检索器，方便加入chain"""
        return self.vector_store.as_retriever(search_kwargs={"k": config.similarity_threshold})

    def get_all_documents(self):
        """从ChromaDB获取所有文档并转换为Document对象列表"""
        all_docs = self.vector_store.get()

        if not all_docs or 'ids' not in all_docs or len(all_docs['ids']) == 0:
            self.logger.warning("ChromaDB 中没有任何文档")
            return []
        if 'documents' not in all_docs:
            self.logger.warning("ChromaDB返回数据但没有documents字段")
            return []

        documents = []
        for i, doc_id in enumerate(all_docs['ids']):
            page_content = all_docs['documents'][i] if 'documents' in all_docs else ''
            metadata = all_docs['metadatas'][i] if 'metadatas' in all_docs else {}

            if page_content and page_content.strip():
                documents.append(Document(page_content=page_content, metadata=metadata))
        self.logger.info(f"成功加载 {len(documents)} 个文档")
        return documents