import os
from app import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
from chromadb.config import Settings

def check_md5(md5_str: str):
    """检查传入的md5字符串是否被处理过了"""
    if not os.path.exists(config.md5_path):
        open(config.md5_path, "w", encoding="utf-8").close()
        return False
    else:
        for line in open(config.md5_path, "r", encoding="utf-8").readlines():
            line = line.strip()
            if line == md5_str:
                return True
        return  False

def save_md5(md5_str: str):
    """将传入的md5字符串，记录到文件内保存"""
    with open(config.md5_path, "a", encoding="utf-8") as f:
        f.write(md5_str + "\n")

def get_string_md5(input_str: str, encoding="utf-8"):
    """将传入的字符串转换为md5字符串"""
    str_bytes = input_str.encode(encoding=encoding) # 将字符串转换为字节串
    md5_obj = hashlib.md5() # 获取md5对象
    md5_obj.update(str_bytes) # 更新md5对象
    md5_hex = md5_obj.hexdigest() # 获取md5的十六进制字符串
    return md5_hex


def delete_md5(md5_str: str) -> bool:
    """从 MD5 记录文件中删除指定的 MD5 字符串"""
    if not os.path.exists(config.md5_path):
        return False

    try:
        # 读取所有 MD5 记录
        with open(config.md5_path, "r", encoding="utf-8") as f:
            md5_list = [line.strip() for line in f.readlines()]

        # 移除目标MD5
        if md5_str in md5_list:
            md5_list.remove(md5_str)

            # 写回文件
            with open(config.md5_path, "w", encoding="utf-8") as f:
                f.write("\n".join(md5_list))
                if md5_list:  # 如果还有记录，保留末尾换行
                    f.write("\n")
            return True
        else:
            return False

    except Exception as e:
        print(f"删除MD5记录失败：{str(e)}")
        return False

class KnowledgeBaseService(object):

    def __init__(self):
        os.makedirs(config.persist_directory, exist_ok=True) # 验证文件夹是否存在，如果不存在则创建，如果存在则无事发生
        self.embedding = OllamaEmbeddings(
            model=config.embeddings_model_name,
            base_url=config.OLLAMA_BASE_URL,
            num_ctx=4096
        )
        self.chroma = Chroma(
            collection_name=config.collection_name, # 数据库表名
            persist_directory=config.persist_directory, # 数据库本地存储文件夹
            embedding_function=self.embedding,
            client_settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True,
                persist_directory=config.persist_directory
            )
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
        )

    def delete_by_filename(self, filename: str) -> bool:
        """根据文件名删除向量数据库中的文档"""
        try:
            # 先查询是否存在该文件的所有向量
            existing_docs = self.chroma.get(
                where={"source": filename}
            )

            if not existing_docs or len(existing_docs.get('ids', [])) == 0:
                print(f"警告：未找到文件 {filename} 的向量数据")
                return False

            # 使用delete方法，通过filter删除对应source的所有向量
            result = self.chroma.delete(
                where={"source": filename}
            )

            # 验证是否删除成功
            remaining_docs = self.chroma.get(
                where={"source": filename}
            )

            if remaining_docs and len(remaining_docs.get('ids', [])) > 0:
                print(f"警告：删除后仍剩余 {len(remaining_docs['ids'])} 个向量")
                return False

            return True

        except Exception as e:
            print(f"删除向量数据失败：{str(e)}")
            return False

    def upload_by_str(self, data: str, filename):
        """将传入的字符串进行向量化，存入向量数据库中"""
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "数据已存在"

        if len(data) > config.min_split_char_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        metadatas = {"source": filename,
                     "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.chroma.add_texts(texts=knowledge_chunks, metadatas=[metadatas for _ in knowledge_chunks])

        save_md5(md5_hex)

        return "数据处理完成"

    def delete_by_filename_with_md5(self, filename: str, file_md5: str = None) -> bool:
        """删除文件时同步清理MD5记录"""
        # 先删除向量数据
        vector_deleted = self.delete_by_filename(filename)

        # 如果提供了 MD5，删除对应的 MD5 记录
        if file_md5:
            delete_md5(file_md5)

        return vector_deleted


