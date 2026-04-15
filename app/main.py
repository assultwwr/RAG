import streamlit as st
import uuid
import sys
import os
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)

from core.rag import RagService
from core.knowledge_base import KnowledgeBaseService
from managers.database_manager import DatabaseManager
from managers.session_history_manager import SessionHistoryManager
from managers.space_manager import SpaceManager

from page_modules.qa_page import chat_page
from page_modules.upload_page import upload_page
from page_modules.knowledge_page import knowledge_page
from page_modules.history_page import session_page
from page_modules.space_page import space_page

# 页面配置
st.set_page_config(
    page_title="RAG 智能知识库",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话 ID
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
    st.session_state["new_session"] = True

# 会话状态保留
if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "你好，有什么可以帮助你？"}]

if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if "db_manager" not in st.session_state:
    st.session_state["db_manager"] = DatabaseManager()

if "session_manager" not in st.session_state:
    st.session_state["session_manager"] = SessionHistoryManager()

if "session_recorded" not in st.session_state:
    st.session_state["session_recorded"] = False

# 每次启动应用时自动检查并清理过期数据（只运行一次）
if "cleanup_done" not in st.session_state:
    st.session_state["cleanup_done"] = False

if not st.session_state["cleanup_done"]:
    try:
        # 创建空间管理器
        space_manager = SpaceManager()

        # 获取统计信息（清理前）
        old_stats = space_manager.get_storage_statistics()
        old_file_count = old_stats['files']['total_count']
        old_session_count = old_stats['sessions']['total_count']

        # 执行清理
        with st.spinner("🧹 正在检查并清理过期数据..."):
            result = space_manager.run_auto_cleanup()

        # 获取统计信息（清理后）
        new_stats = space_manager.get_storage_statistics()

        # 显示清理结果
        deleted_files = result['files']['deleted_count']
        deleted_sessions = result['sessions']['deleted_count']
        saved_space = result['files']['saved_space_kb']

        if deleted_files > 0 or deleted_sessions > 0:
            st.success(
                f"已清理过期数据：删除{deleted_files}个文件、{deleted_sessions}个会话，释放{saved_space:.2f}KB空间")
            # 刷新向量数据库连接，确保检索时使用最新数据
            st.session_state["rag"].refresh_vector_store()

        else:
            st.info("没有需要清理的过期数据")

        # 标记已完成清理
        st.session_state["cleanup_done"] = True

    except Exception as e:
        st.error(f"清理过程出错：{str(e)}")
        st.session_state["cleanup_done"] = True

# 侧边栏
with st.sidebar:
    st.title("🤖 RAG 知识库")

    # 清空会话按钮
    if st.button("新 会 话", use_container_width=True):
        st.session_state["message"] = [{"role": "assistant", "content": "你好，有什么可以帮助你？"}]
        # 标记为新会话，下次会重新创建记录
        st.session_state["new_session"] = True
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["session_recorded"] = False
        st.rerun()

    st.divider() # 分割线

    # 导航菜单
    menu = ["💬 智能问答", "📁 文件上传", "🗄️ 知识库管理", "💭 会话历史", "⚙️ 空间管理"]
    choice = st.radio("选择功能", menu, label_visibility="collapsed")
    st.divider()
    # 实时统计
    st.subheader("📊 实时统计")

    db_manager = st.session_state["db_manager"]
    file_stats = db_manager.get_statistics()

    st.metric("📄 文件总数", file_stats["total_files"])
    st.metric("📝 活跃文件", file_stats["active_files"])

# 根据选择显示不同页面
if choice == "💬 智能问答":
    chat_page()
elif choice == "📁 文件上传":
    upload_page()
elif choice == "🗄️ 知识库管理":
    knowledge_page()
elif choice == "💭 会话历史":
    session_page()
elif choice == "⚙️ 空间管理":
    space_page()