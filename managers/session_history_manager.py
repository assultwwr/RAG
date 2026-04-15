import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app import config_data as config
from langchain_core.messages import messages_from_dict, messages_to_dict


class SessionHistoryManager:
    """会话历史管理器：管理用户会话记录"""
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            # 使用绝对路径：从当前文件位置向上一级到项目根目录，再进入data/chat_history
            base_path = os.path.join(config.BASE_DIR, 'data', 'chat_history')
            storage_path = os.path.abspath(base_path)

        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.metadata_file = os.path.join(storage_path, "session_metadata.json")
        self._init_metadata()

    def _init_metadata(self):
        """初始化元数据文件"""
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_metadata(self) -> List[Dict]:
        """加载元数据"""
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _save_metadata(self, data: List[Dict]):
        """保存元数据"""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_session_record(self, session_id: str, first_message: str):
        """添加会话记录"""
        metadata = self._load_metadata()

        # 检查是否已存在该会话
        for record in metadata:
            if record["session_id"] == session_id:
                # 会话已存在，不重复创建
                return

        record = {
            "session_id": session_id,
            "create_time": datetime.now().isoformat(),
            "last_activity_time": datetime.now().isoformat(),
            "message_count": 1,
            "first_message": first_message[:100],  # 只保存前 100 字符
            "status": "active"
        }

        metadata.append(record)
        self._save_metadata(metadata)

    def update_session_activity(self, session_id: str, message_count: int):
        """更新会话活动"""
        metadata = self._load_metadata()

        for record in metadata:
            if record["session_id"] == session_id:
                record["last_activity_time"] = datetime.now().isoformat()
                record["message_count"] = message_count
                break

        self._save_metadata(metadata)

    def get_all_sessions(self) -> List[Dict]:
        """获取所有会话记录"""
        return self._load_metadata()

    def get_session_by_id(self, session_id: str) -> Optional[Dict]:
        """根据 ID 获取会话"""
        metadata = self._load_metadata()
        for record in metadata:
            if record["session_id"] == session_id:
                return record
        return None

    def delete_session(self, session_id: str) -> bool:
        """删除会话记录（包括文件）"""
        # 删除元数据
        metadata = self._load_metadata()
        original_count = len(metadata)
        metadata = [r for r in metadata if r["session_id"] != session_id]

        if len(metadata) < original_count:
            self._save_metadata(metadata)

        # 删除实际文件
        session_id = session_id.replace(':', '_').replace('-', '_')
        session_file = os.path.join(self.storage_path, session_id)
        if os.path.exists(session_file):
            os.remove(session_file)
            return True

        return len(metadata) < original_count

    def get_expired_sessions(self, days: int = 30) -> List[Dict]:
        """获取过期的会话记录"""
        metadata = self._load_metadata()
        cutoff_date = datetime.now() - timedelta(days=days)

        expired = []
        for record in metadata:
            last_activity = datetime.fromisoformat(record["last_activity_time"])
            if last_activity < cutoff_date and record["status"] == "active":
                expired.append(record)

        return expired

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        metadata = self._load_metadata()

        if not metadata:
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "total_messages": 0
            }

        return {
            "total_sessions": len(metadata),
            "active_sessions": sum(1 for r in metadata if r["status"] == "active"),
            "total_messages": sum(r["message_count"] for r in metadata)
        }

    def cleanup_expired(self, days: int = 30) -> int:
        """清理过期会话，返回删除数量"""
        expired = self.get_expired_sessions(days)
        count = 0

        for session in expired:
            if self.delete_session(session["session_id"]):
                count += 1

        return count
