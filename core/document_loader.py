from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader
)
from typing import Optional, Dict, Type
from langchain_core.document_loaders import BaseLoader
import os


class FileLoaderFactory:
    """文件加载器工厂类：根据文件类型返回对应的LangChain加载器"""
    # 文件类型与加载器的映射关系
    LOADER_MAPPING: Dict[str, Type[BaseLoader]] = {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
    }

    # MIME类型到文件扩展名的映射（可选）
    MIME_TYPE_MAPPING = {
        "text/plain": ".txt",
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    }

    @classmethod
    def get_loader(cls, file_path: str, file_type: Optional[str] = None, **kwargs):
        """根据文件路径或类型获取对应的加载器"""
        # 1. 确定文件扩展名
        if file_type:
            # 如果提供了file_type，尝试从MIME类型映射或直接使用
            ext = cls.MIME_TYPE_MAPPING.get(file_type, file_type)
            if not ext.startswith('.'):
                ext = f'.{ext.lower()}'
        else:
            # 否则从文件路径获取扩展名
            ext = os.path.splitext(file_path)[1].lower()

        # 2. 查找对应的加载器类
        loader_class = cls.LOADER_MAPPING.get(ext)

        if not loader_class:
            supported_types = list(cls.LOADER_MAPPING.keys())
            raise ValueError(f"不支持的文件类型: {ext}。支持的类型: {supported_types}")

        # 3. 特殊处理某些加载器的参数
        if loader_class == TextLoader and 'encoding' not in kwargs:
            kwargs['encoding'] = 'utf-8'

        # 4. 创建并返回加载器实例
        return loader_class(file_path, **kwargs)

    @classmethod
    def register_loader(cls, extension: str, loader_class: Type[BaseLoader]):
        """动态注册新的文件类型支持"""
        if not extension.startswith('.'):
            extension = f'.{extension}'
        cls.LOADER_MAPPING[extension] = loader_class
        return loader_class


