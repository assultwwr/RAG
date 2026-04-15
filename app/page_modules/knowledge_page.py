import streamlit as st
from datetime import datetime
import requests

API_BASE_URL = "http://localhost:8000/api"


def knowledge_page():
    st.title("🗄️ 知识库管理")
    st.caption("查看已上传文件信息，支持删除操作")
    st.divider()

    # 从 API 获取文件列表
    try:
        api_response = requests.get(f"{API_BASE_URL}/files", timeout=10)
        api_response.raise_for_status()
        files_data = api_response.json().get("files", [])
    except Exception as e:
        st.error(f"获取文件列表失败：{str(e)}")
        files_data = []

    # 统计信息
    total_files = len(files_data)
    active_files = sum(1 for f in files_data if f.get("access_count", 0) > 0)
    total_size = sum(f.get("file_size", 0) for f in files_data)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 文件总数", total_files)
    with col2:
        st.metric("✅ 活跃文件", active_files)
    with col3:
        st.metric("💾 总大小", f"{total_size / 1024:.2f} KB")

    st.divider()

    # 文件列表
    st.subheader("📚 已上传文件列表")

    if files_data:
        for file in files_data:
            last_access = datetime.fromisoformat(file["last_access_time"][:19])
            days_since_access = (datetime.now() - last_access).days

            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"**📄 {file['filename']}**")
                    st.caption(f"类型：{file['file_type']} | 大小：{file['file_size'] / 1024:.2f} KB | "
                               f"分块数：{file['chunk_count']}")
                    st.caption(f"上传时间：{file['upload_time'][:19]} | "
                               f"最后访问：{file['last_access_time'][:19]} ({days_since_access}天前)")
                    st.caption(f"访问次数：{file['access_count']} | 状态：{file['status']}")

                with col2:
                    if file["access_count"] > 0:
                        st.success("活跃")
                    else:
                        st.warning("未引用")

                with col3:
                    if st.button("删除", key=f"del_{file['filename']}"):
                        try:
                            api_response = requests.delete(
                                f"{API_BASE_URL}/files/{file['filename']}",
                                timeout=10
                            )
                            api_response.raise_for_status()

                            st.success(f"✅ {file['filename']} 已删除")
                            st.rerun()
                        except Exception as e:
                            st.error(f"删除失败：{str(e)}")

                st.divider()
    else:
        st.info("暂无文件")

