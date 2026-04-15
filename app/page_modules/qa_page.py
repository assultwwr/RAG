import streamlit as st
import uuid
import requests


API_BASE_URL = "http://localhost:8000/api"

def chat_page():
    st.title("💬 智能问答")
    st.caption("基于知识库的智能问答系统")

    st.divider()

    # 显示历史消息
    for message in st.session_state["message"]:
        st.chat_message(message["role"]).write(message["content"])

    # 在页面最下方提供用户输入栏
    prompt = st.chat_input()

    if prompt:
        # 在页面输出用户的提问
        st.chat_message("user").write(prompt)
        st.session_state["message"].append({"role": "user", "content": prompt})

        # 如果是第一次提问，创建会话记录
        if not st.session_state.get("session_recorded", False):
            session_manager = st.session_state["session_manager"]
            session_manager.add_session_record(
                session_id=st.session_state["session_id"],
                first_message=prompt[:100]  # 保存用户第一个问题
            )
            st.session_state["session_recorded"] = True

        with st.spinner("思考中..."):
            try:
                api_response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={
                        "message": prompt,
                        "session_id": st.session_state["session_id"],
                        "history": st.session_state["message"]
                    },
                    timeout=60
                )
                api_response.raise_for_status()
                data = api_response.json()
                answer = data["answer"]

                st.chat_message("assistant").write(answer)
                st.session_state["message"].append({"role": "assistant", "content": answer})

            except requests.exceptions.Timeout:
                st.error("请求超时，请重试")
            except requests.exceptions.RequestException as e:
                st.error(f"请求失败：{str(e)}")