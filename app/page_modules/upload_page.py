import streamlit as st
import requests
import tempfile
import os
from core.document_loader import FileLoaderFactory
from core.knowledge_base import get_string_md5

API_BASE_URL = "http://localhost:8000/api"

def upload_page():
    st.title("📁 文件上传")
    st.caption("上传文件到知识库，支持 txt、pdf、docx 格式")
    st.divider()

    uploaded_files = st.file_uploader(
        "选择文件上传",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("开始上传"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        success_count = 0
        error_count = 0

        for i, uploaded_file in enumerate(uploaded_files):
            try:
                file_name = uploaded_file.name
                file_type = uploaded_file.type
                file_size = uploaded_file.size / 1024

                status_text.text(f"正在处理文件 {i+1}/{len(uploaded_files)}: {file_name}")

                # 直接通过 API 上传
                files = {"files": (file_name, uploaded_file, file_type)}
                api_response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=120)
                api_response.raise_for_status()

                result = api_response.json()
                if result.get("results"):
                    file_result = result["results"][0]
                    if file_result.get("status") == "数据处理完成":
                        success_count += 1
                        st.success(f"✅ {file_name} 上传成功")
                    else:
                        error_count += 1
                        st.warning(f"{file_name}: {file_result.get('status')}")

                progress_bar.progress((i + 1) / len(uploaded_files))

            except requests.exceptions.Timeout:
                error_count += 1
                st.error(f"文件{file_name}处理超时")
            except Exception as e:
                error_count += 1
                st.error(f"文件{file_name}处理失败：{str(e)}")

        progress_bar.progress(1.0)
        status_text.text(f"上传完成！成功：{success_count}, 失败：{error_count}")

        if success_count > 0:
            st.session_state["rag"].refresh_vector_store()
            st.success("向量数据库已刷新")