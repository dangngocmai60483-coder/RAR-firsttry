from operator import itemgetter
from langchain_community.chat_models import ChatTongyi
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)

    return prompt

class RagService(object):
    def __init__(self):
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一位专业的客服助理。请结合【对话历史】和【参考资料】简洁专业的回答。要求：优先参考资料，若资料未提及则礼貌告知。\n\n【参考资料】：{context}\n\n【对话历史】：{history}"),
                ("user", "{input}")
            ]
        )
        self.chat_model = ChatTongyi(model=config.chat_model_name)
        self.chain = self.__get_chain()

    def __get_chain(self):
        """获取最终的执行链"""
        retriever = self.vector_service.get_retriever()
        
        # 修正后的链条：
        # 1. 使用 itemgetter("input") 确保检索器只拿到用户问题的字符串
        # 2. 使用 RunnableParallel 显式保留 input 和 history 字段供 Prompt 使用
        chain = (
            {
                "context": itemgetter("input") | retriever,
                "input": itemgetter("input"),
                "history": itemgetter("history")
            }
            | self.prompt_template              # 此时输入字典包含 context, input, history
            | print_prompt
            | self.chat_model
            | StrOutputParser()
        )
        return chain

if __name__ == "__main__":
    # 注意：直接运行 rag.py 时，因为没有 history_service 包装，
    # 手动调用需要提供 {"input": "...", "history": ""} 格式
    service = RagService()
    res = service.chain.invoke({"input": "我的体重120斤，尺码推荐", "history": ""})
    print(res)