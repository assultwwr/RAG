import logging

from core.message_history_store import get_session_history
from core.vector_stores import VectorStoreService
from langchain_community.retrievers import BM25Retriever
from app import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.output_parsers import StrOutputParser
from managers.database_manager import DatabaseManager
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder


class RagService(object):
    def __init__(self):
        self.embedding = OllamaEmbeddings(
            model=config.embeddings_model_name,
            base_url=config.OLLAMA_BASE_URL,
            num_ctx=4096
        )
        self.vector_store_service = VectorStoreService(embedding=self.embedding)
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        self.promtpt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个专业的智能助手，以我提供的参考资料{context}为准，简洁的回答用户问题，如果没有参考资料没有合适内容就回答不知道，不要进行发散"),
                MessagesPlaceholder(variable_name="history"),
                ("user", "请回答我的问题：{input}")
            ]
        )

        self.chat_model = ChatOllama(model=config.chat_model_name)

        self.chain = self.__get_chain()

    def refresh_vector_store(self):
        """刷新向量数据库连接，确保获取最新数据"""
        self.vector_store_service = VectorStoreService(
            embedding=OllamaEmbeddings(model=config.embeddings_model_name))
        self.chain = self.__get_chain()

    def __get_chain(self):
        """获取最终的执行链"""
        vector_retriever = self.vector_store_service.get_retriever()

        documents = self.vector_store_service.get_all_documents()
        if not documents or len(documents) == 0:
            retriever = vector_retriever
            self.logger.info("未找到文档，仅启用向量检索")
        else:
            BM25_retriever = BM25Retriever.from_documents(documents)
            BM25Retriever.k = config.similarity_threshold
            ensemble_retriever = EnsembleRetriever(retrievers=[vector_retriever, BM25_retriever], weights=[0.5, 0.5])

            self.logger.info("已启用混合检索")

            reranker_model = HuggingFaceCrossEncoder(model_name=config.RERANKER_MODEL_PATH,
                                                     model_kwargs={"device": config.RERANKER_DEVICE}) # 有GPU可以用cuda，没有就用cpu
            compressor = CrossEncoderReranker(model=reranker_model, top_n=5)
            self.logger.info("已启用交叉编码reranker")

            retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=ensemble_retriever
            )
            self.logger.info("已启用上下文压缩")

        def format_document(docs: list[Document]):
            if not docs:
                self.logger.info("未检索到任何文档")
                return "无相关参考资料"

            formatted_str = ""
            source_files = set()

            self.logger.info(f"检索到{len(docs)}个文档")
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
                # 提取文件名
                if "source" in doc.metadata:
                    filename = doc.metadata["source"]
                    source_files.add(filename)
                    self.logger.info(f"文档来源：{filename}")

            # 更新文件访问记录
            for filename in source_files:
                try:
                    self.db_manager.update_access_time(filename)
                    self.logger.info(f"已更新文件访问记录：{filename}")

                except Exception as e:
                    self.logger.info(f"更新访问记录失败：{filename}, {str(e)}")

            return formatted_str

        def format_for_retriever(value: dict) -> str:
            query = value["input"]
            self.logger.info(f"检索关键词：{query}")
            return query

        def format_for_prompt_template(value):
            # 为了提示词的接收格式{input, context, history}进行调整
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value

        basic_chain = (
            {
                "input": RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever) | retriever | RunnableLambda(format_document)
            } | RunnableLambda(format_for_prompt_template) | self.promtpt_template | self.chat_model | StrOutputParser()
        )

        chain = RunnableWithMessageHistory(
            runnable=basic_chain,  # 基础的链
            get_session_history=get_session_history,  # 获取历史记录的函数
            input_messages_key="input",  # 输入消息的键
            history_messages_key="history"  # 历史消息的键
        )

        return chain