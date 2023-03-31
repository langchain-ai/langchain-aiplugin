"""Load html from files, clean up, split, ingest into Weaviate."""
import pickle

from langchain.document_loaders import SitemapLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS


def get_text(content):
    relevant_part = content.find("div", {"class": "markdown"})
    if relevant_part is not None:
        return relevant_part.get_text(separator=" ")
    else:
        return ""


def ingest_docs():
    """Get documents from web pages."""
    loader = SitemapLoader(
        web_path="https://docs.langchain.com/sitemap.xml", parsing_function=get_text
    )
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()
