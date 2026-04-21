from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from rag import RagService

# 本地 SQLite 数据库文件路径，用于长期存储
DB_PATH = "sqlite:///chat_history.db"

def get_session_history(session_id: str):
    """
    通过 SQLAlchemy 将对话历史持久化到 SQLite 数据库中。
    这样即使程序重启，记忆依然存在。
    """
    return SQLChatMessageHistory(
        session_id=session_id, 
        connection_string=DB_PATH
    )

class HistoryRagService(object):
    def __init__(self):
        # 1. 初始化核心 RAG 服务
        self.rag_service = RagService()
        
        # 2. 包装原始链条以支持【持久化】历史记忆
        # history_messages_key 对应 Prompt 中的 {history}
        # input_messages_key 对应用户提问 {input}
        self.with_history_chain = RunnableWithMessageHistory(
            self.rag_service.chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="history"
        )

    def ask(self, query: str, session_id: str = "default_user"):
        """
        进行多轮对话问答（长期记忆版）
        :param query: 用户问题
        :param session_id: 会话 ID。相同的 ID 会共享同一段长期记忆。
        """
        config = {"configurable": {"session_id": session_id}}
        return self.with_history_chain.invoke(
            {"input": query},
            config=config
        )

if __name__ == "__main__":
    # --- 测试长期记忆 ---
    # 第一次运行：提问并存储
    # 第二次运行：直接询问“我上次问了什么”，看它是否记得
    service = HistoryRagService()
    
    my_session = "user_123"
    print(f"\n--- 当前会话: {my_session} ---")
    
    q = "我叫小王，我身高175，体重140斤。"
    print(f"输入: {q}")
    print(f"响应: {service.ask(q, session_id=my_session)}")
    
    print("\n--- 模拟重启或新连接 ---")
    q2 = "你还记得我叫什么，多重吗？"
    print(f"输入: {q2}")
    print(f"响应: {service.ask(q2, session_id=my_session)}")
