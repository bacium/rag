import time
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
# from langchain.text_splitter import MarkdownTextSplitter 旧版本使用
from langchain_text_splitters import MarkdownTextSplitter  # 新版本langchain 1.0 以后使用这个
import os, sys
from datetime import datetime
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
                    # print(f"加载文件 {loaded_docs} 成功！")
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
    return document_list


def process_document(file_path="", parent_chunk_size=conf.PARENT_CHUNK_SIZE, child_chunk_size=conf.CHILD_CHUNK_SIZE,
                     chunk_overlap=conf.CHUNK_OVERLAP):
    document = load_document_from_dir(file_path)
    logger.info(f"加载文件的数量为：{len(document)}")
    parent_splitter = ChineseRecursiveTextSplitter(chunk_size=parent_chunk_size,
                                                   chunk_overlap=chunk_overlap)
    child_splitter = ChineseRecursiveTextSplitter(chunk_size=child_chunk_size, chunk_overlap=chunk_overlap)
    markdown_parent_splitter = MarkdownTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=chunk_overlap)
    markdown_child_splitter = MarkdownTextSplitter(chunk_size=child_chunk_size, chunk_overlap=chunk_overlap)

    child_chunks = []
    for i, doc in enumerate(document):
        # print(f"doc========>{doc}")
        file_extension = os.path.splitext(doc.metadata["file_path"])[1].lower()
        # print(f"文件扩展名为：{file_extension}")
        is_markdown = file_extension == ".md"
        parent_splitter_to_use = markdown_parent_splitter if is_markdown else parent_splitter  # 父块切分器
        child_splitter_to_use = markdown_child_splitter if is_markdown else child_splitter  # 子块切分器
        logger.info(
            f"处理文档: {doc.metadata['file_path']}, 使用切分器: {'Markdown' if is_markdown else 'ChineseRecursive'}")
        # 切分父块文档
        parent_chunks = parent_splitter_to_use.split_documents([doc])
        # print(f"parent_chunks========>{parent_chunks}")
        for j, parent_chunk in enumerate(parent_chunks):
            # print(f"parent_chunk========>{parent_chunk}")
            parent_chunk_id = f"doc_{j}_parent_chunk_{j}"
            # 切分子块文档
            sub_chunks = child_splitter_to_use.split_documents([parent_chunk])
            for k, sub_chunk in enumerate(sub_chunks):
                # print(f"sub_chunk========>{sub_chunk}")
                sub_chunk.metadata["parent_chunk_id"] = parent_chunk_id
                sub_chunk.metadata["id"] = f"{parent_chunk_id}_child_{k}"
                sub_chunk.metadata["parent_chunk_content"] = parent_chunk.page_content
                child_chunks.append(sub_chunk)
    # 记录子块总数日志
    logger.info(f"子块数量: {len(child_chunks)}")
    return child_chunks


if __name__ == '__main__':
    dir_path = "C:\\Users\\bai\\Desktop\\project\\rag\\integrated_qa_system\\rag_qa\\data\\ai_data"
    # dir_path="/Users/baidengchao/Desktop/project/Rag_code/integrated_qa_system/rag_qa/data/ai_data"
    # load_document_from_dir(dir_path)
    chunk_result = process_document(dir_path)
    # print(chunk_result[0])
