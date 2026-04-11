import logging
from retrieval.bm25_search import BM25Search

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    documents = ["我喜欢编程", "编程很有趣"]
    bm25_model = BM25Search(documents)
    query = "他喜欢编程"
    doc, score = bm25_model.search(query)
    print(doc, score)


if __name__ == "__main__":
    main()
