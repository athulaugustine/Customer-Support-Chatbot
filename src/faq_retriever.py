import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_text_splitters import HTMLSectionSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from uuid import uuid4
from langchain_core.tools import tool


def get_faq_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    try:
        vector_store = FAISS.load_local("./src/faq_faiss_index", embeddings, allow_dangerous_deserialization=True)
        print("Loaded existing FAISS index.")
    except:
        print("Creating new FAISS index.")
        loader = UnstructuredExcelLoader("./faqs/customer_support_chatbot_faqs.xlsx", mode="elements")
        docs = loader.load()
        html_string = "\n".join([doc.metadata['text_as_html'] for doc in docs])
        headers_to_split_on = [
            ("tr", "FAQ"),
        ]
        html_splitter = HTMLSectionSplitter(headers_to_split_on)
        html_header_splits = html_splitter.split_text(html_string)
        uuids = [str(uuid4()) for _ in range(len(html_header_splits))]

        index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

        vector_store.add_documents(documents=html_header_splits, ids=uuids)
        vector_store.save_local("./src/faq_faiss_index")
        print("FAISS index Saved.")

    retriever = vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.2, "k": 1})

    return retriever


@tool
def faq_tool(original_query: str) -> str:
    """Searches the FAQ documents and returns the most relevant answer. Always pass the original user query."""
    retriever = get_faq_retriever()
    docs = retriever.invoke(original_query)
    if docs:
        return docs[0].page_content
    else:
        return "I'm sorry, I couldn't find an answer to your question in the FAQ."