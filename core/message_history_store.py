import os, json

from app import config_data as config
from typing import Sequence
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict


def get_session_history(session_id: str):
    # 使用绝对路径：从core/目录向上一级到项目根目录，再进入data/chat_history
    base_path = os.path.join(config.BASE_DIR, 'data', 'chat_history')
    storage_path = os.path.abspath(base_path)  # 转换为规范绝对路径
    store = FileChatHistoryStore(session_id, storage_path=storage_path)

    # 调试输出
    print(f"创建会话存储：session_id={session_id}, storage_path={storage_path}, file_path={store.file_path}")

    return store

class FileChatHistoryStore(BaseChatMessageHistory):
    def __init__(self, session_id, storage_path):
        self.session_id = session_id # 会话id
        self.storage_path = storage_path # 不同会话id的存储路径
        os.makedirs(storage_path, exist_ok=True)

        # 清理 session_id，移除可能的非法字符
        safe_session_id = session_id.replace(':', '_').replace('-', '_')
        self.file_path = os.path.join(storage_path, safe_session_id)
        print(f"初始化文件路径：{self.file_path}")

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # Sequence序列，类似list、tuple
        all_messages = list(self.messages) # 已有的消息列表
        all_messages.extend(messages) # 新的和已有的融合成一个list

        new_messages = [message_to_dict(message) for message in all_messages] # 将消息列表转换成字典列表

        print(f"💾 [DEBUG] 保存 {len(new_messages)} 条消息到文件：{self.file_path}")
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f) # 将new_messages转换成JSON格式写入文件

        print(f"消息保存成功！文件大小：{os.path.getsize(self.file_path)} bytes")

    @property # @property装饰器，将方法变为成员属性
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f) # 返回值：list[dit]
                print(f"读取到 {len(messages_data)} 条消息")
                return messages_from_dict(messages_data)  # 将 messages_data 转换成字典列表

        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)