"""
基于Streamlit完成WEB网页上传服务
"""
import streamlit as st
from knowleage_base import knowledgeBaseService

# --- 1. 使用 session_state 初始化并持久化服务对象 ---
# 这样即便页面重新运行，service 对象也只会被创建一次，避免重复加载模型和数据库连接
if 'service' not in st.session_state:
    st.session_state['service'] = knowledgeBaseService()

# 方便后续代码调用
service = st.session_state['service']

# 添加网页标题
st.title("知识库更新服务")

# 文件上传组件
file = st.file_uploader(
    "请上传 Txt 文件",
    type=["txt"],
    accept_multiple_files=False,   # 不接受多文件上传
)

# 只有当文件被成功上传时才显示详情和操作按钮
if file is not None:
    file_name = file.name
    file_type = file.type
    file_size = file.size / 1024   # KB为单位

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | 大小：{file_size:.2f} kB")
    
    # 获取文件内容
    text = file.getvalue().decode("utf-8")
    
    # 使用折叠面板预览内容，避免长文本占据过多页面空间
    with st.expander("点击预览文件内容"):
        st.text(text)

    # --- 2. 关键：使用按钮明确触发上传逻辑 ---
    # Streamlit 的运行机制决定了只有点击按钮时，if 块内的代码才会执行一次
    if st.button("🚀 开始向量化并存入知识库"):
        with st.spinner("正在向量化并写入数据库，请稍候..."):
            try:
                # 调用 service 进行向量化和存储
                result = service.upload_by_str(text, file_name)
                
                # 根据返回结果类型显示不同的提示框
                if "[成功]" in result:
                    st.success(result)
                elif "[跳过]" in result:
                    st.warning(result)
                else:
                    st.info(result)
            except Exception as e:
                st.error(f"处理过程中发生错误: {str(e)}")
