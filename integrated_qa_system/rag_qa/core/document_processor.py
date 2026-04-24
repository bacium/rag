import time
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownTextSplitter
from datetime import datetime
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from edu_text_spliter import AliTextSplitter, ChineseRecursiveTextSplitter
from edu_document_loaders import OCRPDFLoader, OCRDOCLoader, OCRPPTLoader, OCRIMGLoader
from base import Config, logger

conf = Config()
document_loaders = {
    # 文本文件使用 TextLoader
    ".txt": TextLoader,
    # PDF 文件使用 OCRPDFLoader
    ".pdf": OCRPDFLoader,
    # Word 文件使用 OCRDOCLoader
    ".docx": OCRDOCLoader,
    # PPT 文件使用 OCRPPTLoader
    ".ppt": OCRPPTLoader,
    # PPTX 文件使用 OCRPPTLoader
    ".pptx": OCRPPTLoader,
    # JPG 文件使用 OCRIMGLoader
    ".jpg": OCRIMGLoader,
    # PNG 文件使用 OCRIMGLoader
    ".png": OCRIMGLoader,
    # Markdown 文件使用 UnstructuredMarkdownLoader
    ".md": UnstructuredMarkdownLoader
}


def load_document_from_dir(dir_path):
    document_list = []
    supported_file_types = document_loaders.keys()
    # print(f"支持的文件类型为：{supported_file_types}")
    source = os.path.basename(dir_path).replace("_data", "")
    # print(f"数据源为：{source}")
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_type = os.path.splitext(file_path)[1].lower()
            if file_type in supported_file_types:
                loader_class = document_loaders[file_type]
                try:
                    if file_type == ".txt":
                        loader = loader_class(file_path, encoding="utf-8")
                    else:
                        loader = loader_class(file_path)
                    loaded_docs = loader.load()
                    print(f"加载文件 {loaded_docs} 成功！")
                    for doc in loaded_docs:
                        # 为文档添加学科类别元数据
                        doc.metadata["source"] = source
                        # 为文档添加文件路径元数据
                        doc.metadata["file_path"] = file_path
                        # 为文档添加当前时间戳元数据
                        doc.metadata["timestamp"] = datetime.now().isoformat()
                        # 将加载的文档添加到总列表中
                    document_list.extend(loaded_docs)
                except Exception as e:
                    logger.error(f"加载文件 {file_path} 时出错：{e}")
                    continue
            else:
                logger.warning(f"不支持的文件类型：{file_type}")
    return  document_list

def process_document(file_path="", parent_chunk_size=conf.PARENT_CHUNK_SIZE, child_chunk_size=conf.CHILD_CHUNK_SIZE,
                     chunk_overlap=conf.CHUNK_OVERLAP):
    document = load_document_from_dir(file_path)
    logger.info(f"加载文件的数量为：{len(document)}")
    parent_splitter = ChineseRecursiveTextSplitter(parent_chunk_size=parent_chunk_size,
                                                   parent_chunk_overlap=chunk_overlap)
    child_splitter = ChineseRecursiveTextSplitter(child_chunk_size=child_chunk_size, child_chunk_overlap=chunk_overlap)

    markdown_parent_splitter = MarkdownTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=chunk_overlap)
    markdown_child_splitter = MarkdownTextSplitter(chunk_size=child_chunk_size, chunk_overlap=chunk_overlap)


if __name__ == '__main__':
    dir_path = "C:\\Users\\bai\\Desktop\\project\\rag\\integrated_qa_system\\rag_qa\\data\\ai_data"
    load_document_from_dir(dir_path)
