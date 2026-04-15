import os
import json
import streamlit as st
from langchain_core.messages import messages_from_dict
from datetime import datetime
import requests

API_BASE_URL = "http://localhost:8000/api"

def session_page():
    if st.session_state.get("show_session_detail", False) and "viewing_session" in st.session_state:
        session_detail()
    else:
        session_list()

def session_list():
    """会话列表"""
    st.title("💭 会话历史")
    st.caption("查看和管理历史会话记录")
    st.divider()

    # 从 API 获取会话列表
    try:
        api_response = requests.get(f"{API_BASE_URL}/sessions", timeout=10)
        api_response.raise_for_status()
        sessions = api_response.json().get("sessions", [])
    except Exception as e:
        st.error(f"获取会话列表失败：{str(e)}")
        sessions = []

    if sessions:
        for session in sessions:
            create_time = datetime.fromisoformat(session["create_time"][:19])
            days_since_creation = (datetime.now() - create_time).days

            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"**💬 {session['first_message'][:50]}...**")
                    st.caption(f"创建时间：{session['create_time'][:19]} | "
                               f"消息数：{session['message_count']} | "
                               f"状态：{session['status']}")
                    st.caption(f"距今天数：{days_since_creation}天")

                with col2:
                    st.success("活跃") if session["status"] == "active" else st.warning("已归档")

                with col3:
                    if st.button("查看", key=f"view_{session['session_id']}"):
                        st.session_state["viewing_session"] = session
                        st.session_state["show_session_detail"] = True
                        st.rerun()

                    if st.button("删除", key=f"del_{session['session_id']}"):
                        try:
                            api_response = requests.delete(
                                f"{API_BASE_URL}/sessions/{session['session_id']}",
                                timeout=10
                            )
                            api_response.raise_for_status()

                            st.rerun()
                        except Exception as e:
                            st.error(f"删除失败：{str(e)}")

                st.divider()
    else:
        st.info("暂无会话记录")

def session_detail():
    """会话详情"""
    viewing = st.session_state["viewing_session"]
    st.title(f"📝 会话内容详情 - {viewing['session_id']}")
    st.caption(f"创建时间：{viewing['create_time'][:19]} | 消息数：{viewing['message_count']}")
    st.divider()

    safe_session_id = viewing["session_id"].replace(':', '_').replace('-', '_')
    session_file_path = os.path.join(st.session_state["session_manager"].storage_path, safe_session_id)

    if not os.path.exists(session_file_path):
        session_file_path_json = session_file_path + ".json"
        if os.path.exists(session_file_path_json):
            session_file_path = session_file_path_json

    if os.path.exists(session_file_path):
        try:
            with open(session_file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
                messages = messages_from_dict(messages_data)
                for msg in messages:
                    role = "user" if hasattr(msg, 'type') and msg.type == 'human' else "assistant"
                    st.chat_message(role).write(msg.content)
        except Exception as e:
            st.error(f"无法加载会话内容：{str(e)}")
    else:
        st.warning("会话内容文件不存在")

    st.divider()
    if st.button("← 返回列表"):
        st.session_state["show_session_detail"] = False
        st.rerun()