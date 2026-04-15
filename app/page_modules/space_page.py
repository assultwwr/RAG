import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000/api"


def space_page():
    st.title("⚙️ 空间管理")
    st.caption("自动清理策略与存储空间统计")
    st.divider()

    storage_stats()
    auto_cleanup()
    manual_cleanup()


def storage_stats():
    """存储统计"""
    st.subheader("📊 存储空间使用统计")

    try:
        api_response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        api_response.raise_for_status()
        stats = api_response.json().get("statistics", {})
    except Exception as e:
        st.error(f"获取统计信息失败：{str(e)}")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 文件存储", f"{stats.get('files', {}).get('total_size_kb', 0):.2f} KB")
        st.caption(f"文件数：{stats.get('files', {}).get('total_count', 0)}")
    with col2:
        st.metric("💬 会话存储", f"{stats.get('sessions', {}).get('total_messages', 0)} 条消息")
        st.caption(f"会话数：{stats.get('sessions', {}).get('total_count', 0)}")
    with col3:
        st.metric("💾 数据库", f"{stats.get('storage', {}).get('chroma_db_size_kb', 0):.2f} KB")
        st.caption(f"向量数据库大小")

    st.divider()


def auto_cleanup():
    """自动清理策略"""
    st.subheader("🤖 自动清理策略")
    col1, col2 = st.columns(2)

    with col1:
        st.info("📄 文件清理策略")
        enabled = st.toggle("启用文件自动清理", value=True, key="file_toggle")
        file_days = st.number_input("保留期限（天）", min_value=30, max_value=120, value=90, step=1,
                                    key="file_days_input")

        if st.button("💾 保存文件清理配置", key="save_file_config"):
            st.success("配置已保存（开发中）")

    with col2:
        st.info("💬 会话清理策略")
        session_enabled = st.toggle("启用会话自动清理", value=True, key="session_toggle")
        session_days = st.number_input("保留期限（天）", min_value=30, max_value=120, value=30, step=1,
                                       key="session_days_input")

        if st.button("💾 保存会话清理配置", key="save_session_config"):
            st.success("配置已保存（开发中）")

    st.divider()

    st.info("""
        📢 **自动清理说明**
        - 触发时机：每次打开应用时自动检查
        - 文件清理：超过指定天数未活跃的文件将被删除
        - 会话清理：超过指定天数的会话将被删除
        - 可自定义：下方可设置保留期限（30-120 天）
    """)

    st.divider()


def manual_cleanup():
    """手动清理"""
    st.subheader("🧹 手动清理")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("️ 立即清理过期文件", use_container_width=True):
            with st.spinner("正在清理过期文件..."):
                try:
                    api_response = requests.post(f"{API_BASE_URL}/cleanup", timeout=60)
                    api_response.raise_for_status()
                    result = api_response.json()

                    deleted_count = result.get('result', {}).get('files', {}).get('deleted_count', 0)
                    saved_space = result.get('result', {}).get('files', {}).get('saved_space_kb', 0)

                    st.success(f"清理完成！删除{deleted_count}个文件，释放{saved_space:.2f}KB 空间")
                    st.rerun()
                except Exception as e:
                    st.error(f"清理失败：{str(e)}")

    with col2:
        if st.button("🗑️ 立即清理过期会话", use_container_width=True):
            with st.spinner("正在清理过期会话..."):
                try:
                    api_response = requests.post(f"{API_BASE_URL}/cleanup", timeout=60)
                    api_response.raise_for_status()
                    result = api_response.json()

                    deleted_count = result.get('result', {}).get('sessions', {}).get('deleted_count', 0)

                    st.success(f"清理完成！删除{deleted_count}个会话")
                    st.rerun()
                except Exception as e:
                    st.error(f"清理失败：{str(e)}")
