#chroma

md5_path = "./md5.text"
collection_name = "rag"
persist_directory="./chroma_db"
#spliter
chunk_size=1000
chunk_overlap=100
separators=["\n\n" , "." , "\n" , "。" , " " , "" , "?" , "!" , "？" , "！"]
max_split_char_number = 1000    #文本分割的阈值

#
similarity_threshold= 2

# 修正模型名称：必须严格区分大小写
embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen-max"
