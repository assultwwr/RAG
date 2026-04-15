import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app import config_data as config


# 在项目根目录创建 database 文件夹
database_dir = os.path.join(config.BASE_DIR, "data", "database")
os.makedirs(database_dir, exist_ok=True)

class DatabaseManager:
    """数据库管理器：管理已上传的文件信息"""

    def __init__(self):
        self.db_file = os.path.join(config.BASE_DIR, "data", "database", "file_metadata.json")
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库文件"""
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_data(self) -> List[Dict]:
        """加载数据库"""
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _save_data(self, data: List[Dict]):
        """保存数据库"""
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_file_record(self, filename: str, file_size: int, file_type: str, chunk_count: int = 0, file_md5: str = None):
        """添加文件记录"""
        data = self._load_data()

        record = {
            "filename": filename,
            "file_size": file_size,
            "file_type": file_type,
            "file_md5": file_md5,
            "upload_time": datetime.now().isoformat(),
            "last_access_time": datetime.now().isoformat(),
            "access_count": 0,
            "chunk_count": chunk_count,
            "status": "active"
        }

        data.append(record)
        self._save_data(data)
        return record

    def get_all_files(self) -> List[Dict]:
        """获取所有文件记录"""
        return self._load_data()

    def get_file_by_name(self, filename: str) -> Optional[Dict]:
        """根据文件名获取记录"""
        data = self._load_data()
        for record in data:
            if record["filename"] == filename:
                return record
        return None

    def update_access_time(self, filename: str):
        """更新文件访问时间"""
        data = self._load_data()
        updated = False
        for record in data:
            if record["filename"] == filename:
                record["last_access_time"] = datetime.now().isoformat()
                record["access_count"] += 1
                updated = True
                break

        if updated:
            self._save_data(data)

    def delete_file(self, filename: str) -> bool:
        """删除文件记录"""
        data = self._load_data()
        original_count = len(data)
        data = [r for r in data if r["filename"] != filename]

        if len(data) < original_count:
            self._save_data(data)
            return True
        return False

    def get_expired_files(self, days: int = 90) -> List[Dict]:
        """获取超过指定天数未访问的文件"""
        data = self._load_data()
        cutoff_date = datetime.now() - timedelta(days=days)

        expired = []
        for record in data:
            last_access = datetime.fromisoformat(record["last_access_time"])
            if last_access < cutoff_date and record["status"] == "active":
                expired.append(record)

        return expired

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        data = self._load_data()

        if not data:
            return {
                "total_files": 0,
                "total_size": 0,
                "active_files": 0
            }

        return {
            "total_files": len(data),
            "total_size": sum(r["file_size"] for r in data),
            "active_files": sum(1 for r in data if r["status"] == "active")
        }
