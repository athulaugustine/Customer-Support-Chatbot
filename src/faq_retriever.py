import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import UnstructuredExcelLoader

loader = UnstructuredExcelLoader("./faqs/customer_support_chatbot_faqs.xlsx", mode="elements")
docs = loader.load()


# index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

# vector_store = FAISS(
#     embedding_function=embeddings,
#     index=index,
#     docstore=InMemoryDocstore(),
#     index_to_docstore_id={},
# )

# # Initialize the ensemble retriever
# ensemble_retriever = EnsembleRetriever(
#     retrievers=[bm25_retriever, vector_store_retriever], weights=[0.5, 0.5]
# )