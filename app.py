import streamlit as st
from knowleage_base import knowledgeBaseService
from history_service import HistoryRagService, get_session_history
from langchain_core.messages import HumanMessage, AIMessage

# --- 页面配置 ---
st.set_page_config(
    page_title="RAG 智能客服系统",
    page_icon="🤖",
    layout="wide"
)

# --- 全局状态管理 ---
if 'kb_service' not in st.session_state:
    st.session_state.kb_service = knowledgeBaseService()

if 'rag_service' not in st.session_state:
    st.session_state.rag_service = HistoryRagService()

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# --- 辅助函数：从数据库同步历史记录到 UI ---
def sync_history_to_ui(sid):
    """从 SQLite 加载历史消息到 streamlit 的 session_state 中"""
    history = get_session_history(sid)
    ui_messages = []
    for msg in history.messages:
        if isinstance(msg, HumanMessage):
            ui_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            ui_messages.append({"role": "assistant", "content": msg.content})
    st.session_state.chat_messages = ui_messages

# --- 侧边栏导航 ---
with st.sidebar:
    st.title("导航菜单")
    page = st.radio("请选择功能模块", ["💬 智能对话问答", "📂 知识库管理"])
    
    st.divider()
    if page == "💬 智能对话问答":
        st.subheader("会话设置")
        # 如果 Session ID 改变，立即同步历史
        current_sid = st.text_input("用户 ID (Session ID)", value="user_123")
        
        # 初始化或切换 ID 时加载历史
        if 'last_sid' not in st.session_state or st.session_state.last_sid != current_sid:
            sync_history_to_ui(current_sid)
            st.session_state.last_sid = current_sid

        if st.button("清空页面显示 (不删数据库)"):
            st.session_state.chat_messages = []
    
    st.info("提示：对话历史会自动持久化到本地 SQLite 数据库中。")

# --- 模块一：知识库管理 ---
if page == "📂 知识库管理":
    # ... (保持不变)
    st.title("📂 知识库管理")
    st.write("通过上传 TXT 文件来增强机器人的专业知识。")
    
    uploaded_file = st.file_uploader("选择 TXT 文件", type=["txt"])
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        content = uploaded_file.getvalue().decode("utf-8")
        
        with st.expander("预览文件内容"):
            st.text(content)
            
        if st.button("🚀 开始向量化并存入知识库"):
            with st.spinner("正在处理中，请稍候..."):
                try:
                    res = st.session_state.kb_service.upload_by_str(content, file_name)
                    if "[成功]" in res:
                        st.success(res)
                    else:
                        st.warning(res)
                except Exception as e:
                    st.error(f"发生错误：{str(e)}")

# --- 模块二：智能对话问答 ---
else:
    st.title("💬 智能对话问答")
    
    # 显示当前会话的聊天气泡
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 聊天输入框
    if prompt := st.chat_input("请输入您的问题..."):
        # 1. 用户输入显示
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # 2. AI 响应处理
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    # 调用后端服务
                    response = st.session_state.rag_service.ask(prompt, session_id=session_id)
                    
                    # 显示并存入状态
                    st.markdown(response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"获取回答失败：{str(e)}")
