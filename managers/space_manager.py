import os
import json
import logging
from app import config_data as config
from datetime import datetime
from managers.database_manager import DatabaseManager
from managers.session_history_manager import SessionHistoryManager
from core.knowledge_base import KnowledgeBaseService

log_path = os.path.join(config.BASE_DIR, 'data', 'logs')
os.makedirs(log_path, exist_ok=True)

# 配置路径

os.makedirs(os.path.dirname(config.config_file), exist_ok=True)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_path, "space_manager.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SpaceManager:
    """空间管理器：自动清理过期数据"""
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session_manager = SessionHistoryManager()
        self.knowledge_service = KnowledgeBaseService()

        # 加载配置
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(config.config_file):
                with open(config.config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    self.file_retention_days = config_data.get("file_retention_days", 90)
                    self.session_retention_days = config_data.get("session_retention_days", 30)
            else:
                # 默认配置
                self.file_retention_days = 90
                self.session_retention_days = 30
                self._save_config()
        except Exception as e:
            logger.error(f"加载配置文件失败：{str(e)}，使用默认配置")
            self.file_retention_days = 90
            self.session_retention_days = 30

    def _save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                "file_retention_days": self.file_retention_days,
                "session_retention_days": self.session_retention_days
            }
            with open(config.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            logger.info("✅ 配置文件已保存")
        except Exception as e:
            logger.error(f"保存配置文件失败：{str(e)}")

    def update_file_retention(self, days: int):
        """更新文件保留期限"""
        self.file_retention_days = max(0, min(120, days))  # 限制在 0-120 天
        self._save_config()
        logger.info(f"文件保留期限已更新为：{self.file_retention_days} 天")

    def update_session_retention(self, days: int):
        """更新会话保留期限"""
        self.session_retention_days = max(0, min(120, days))  # 限制在 0-120 天
        self._save_config()
        logger.info(f"会话保留期限已更新为：{self.session_retention_days} 天")

    def check_and_cleanup_files(self) -> dict:
        """检查并清理过期文件"""
        logger.info("开始检查过期文件...")

        expired_files = self.db_manager.get_expired_files(self.file_retention_days)
        deleted_count = 0
        saved_space = 0

        for file_record in expired_files:
            try:
                filename = file_record["filename"]
                file_size = file_record["file_size"]
                last_access = file_record["last_access_time"]
                file_md5 = file_record.get("file_md5")

                logger.warning(f"文件 {filename} 已超过 {self.file_retention_days} 天未访问 "
                               f"(最后访问：{last_access})，准备删除...")

                # 从向量数据库删除
                if self.knowledge_service.delete_by_filename_with_md5(filename, file_md5):
                    # 从数据库删除记录
                    if self.db_manager.delete_file(filename):
                        deleted_count += 1
                        saved_space += file_size
                        logger.info(f"已删除文件：{filename} ({file_size / 1024:.2f} KB)")

            except Exception as e:
                logger.error(f"删除文件 {file_record['filename']} 失败：{str(e)}")

        result = {
            "checked_count": len(expired_files),
            "deleted_count": deleted_count,
            "saved_space_kb": saved_space / 1024
        }

        logger.info(f"文件清理完成：检查{len(expired_files)}个，删除{deleted_count}个，"
                    f"释放空间{saved_space / 1024:.2f} KB")

        return result

    def check_and_cleanup_sessions(self) -> dict:
        """检查并清理过期会话"""
        logger.info("开始检查过期会话...")

        deleted_count = self.session_manager.cleanup_expired(self.session_retention_days)

        result = {
            "deleted_count": deleted_count
        }

        logger.info(f"会话清理完成：删除{deleted_count}个过期会话")

        return result

    def get_storage_statistics(self) -> dict:
        """获取存储空间统计"""
        file_stats = self.db_manager.get_statistics()
        session_stats = self.session_manager.get_statistics()

        # 计算实际磁盘使用
        chroma_size = self._get_directory_size(config.persist_directory)
        chat_size = self._get_directory_size(self.session_manager.storage_path)

        return {
            "files": {
                "total_count": file_stats["total_files"],
                "active_count": file_stats["active_files"],
                "total_size_kb": file_stats["total_size"] / 1024
            },
            "sessions": {
                "total_count": session_stats["total_sessions"],
                "active_count": session_stats["active_sessions"],
                "total_messages": session_stats["total_messages"]
            },
            "storage": {
                "chroma_db_size_kb": chroma_size / 1024,
                "chat_history_size_kb": chat_size / 1024,
                "total_size_kb": (chroma_size + chat_size) / 1024
            },
            "retention_policy": {
                "file_retention_days": self.file_retention_days,
                "session_retention_days": self.session_retention_days
            }
        }

    def _get_directory_size(self, path: str) -> int:
        """计算目录总大小（字节）"""
        total_size = 0

        if not os.path.exists(path):
            return 0

        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)

        return total_size

    def run_auto_cleanup(self) -> dict:
        """执行自动清理任务"""
        logger.info("=" * 60)
        logger.info("开始执行清理任务")
        logger.info("=" * 60)
        logger.info(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"文件保留期限：{self.file_retention_days} 天")
        logger.info(f"会话保留期限：{self.session_retention_days} 天")
        logger.info("-" * 60)

        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "files": self.check_and_cleanup_files(),
                "sessions": self.check_and_cleanup_sessions()
            }

            logger.info("=" * 60)
            logger.info("清理任务执行完成")
            logger.info(f"删除文件数量：{results['files']['deleted_count']} 个")
            logger.info(f"删除会话数量：{results['sessions']['deleted_count']} 个")
            logger.info(f"释放存储空间：{results['files']['saved_space_kb']:.2f} KB")
            logger.info("=" * 60)

        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"清理任务执行失败：{str(e)}", exc_info=True)
            logger.error("=" * 60)
            results = {
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }

        logger.info("清理任务结束")
        logger.info("=" * 60)

        return results