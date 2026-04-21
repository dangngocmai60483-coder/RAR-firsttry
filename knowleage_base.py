"""
知识库
"""
import os

from sqlalchemy import false
import hashlib

from sqlalchemy.testing.suite.test_reflection import metadata
from zipp.glob import separate

import config_data as config
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

#实现检测重复
def check_md5(md5_str: str):
    """用md5的重复性来验证传入的字符是否被处理过"""
    if not os.path.exists(config.md5_path ):
        # if表示文件不存在，那肯定没有处理过
        open(config.md5_path,'w',encoding='utf-8').close()
        return False
    else:
        with open(config.md5_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()     #处理字符串中的空格和回车
                if line == md5_str:
                    return True
        return False

#保存没有重复的
def save_md5(md5_str: str):
    """将传入md5字符串记录到文件内保存"""
    with open(config.md5_path,'a',encoding='utf-8') as f:
        f.write(md5_str + "\n")

def get_md5(input_str: str,encoding='utf-8'):
    """将传入的字符串转化成md5字符串"""
    #将字符串转化为byte[]字节数组
    str_bytes = input_str.encode(encoding)
    md5_obj = hashlib.md5()  #创建md5对象
    md5_obj.update(str_bytes) #传入
    md5_hex = md5_obj.hexdigest() #得到md5的十六进制字符串
    return md5_hex

class knowledgeBaseService(object):
    def __init__(self):
        #文件夹不存在则创建
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name,  #数据库表名
            embedding_function=DashScopeEmbeddings(model='text-embedding-v4'),
            persist_directory=config.persist_directory   #数据库本地存储文件夹

        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,   #分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap,  #连续文本段之间的字符重叠数量
            separators=config.separators,   #自然段落划分的符号
            length_function=len          #py自带的len函数
        )


    def upload_by_str(self  ,data: str,filename):
        """将传入的字符串向量化并传入向量数据库"""
        md5_hex = get_md5(data)
        if check_md5(md5_hex):
            return "[跳过]内容已经存在在知识库中"

        if len(data) > config.max_split_char_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]
        metadata={
            "source" : filename,
            #2025-01-01 10:00:00
            "create_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "小卢"
        }
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks],

        )
        save_md5(md5_hex)

        return "[成功]内容已成功载入向量库"


if __name__ == '__main__':
    #
    service = knowledgeBaseService()
    r=service.upload_by_str("黄心怡","test1")
    print(r)
