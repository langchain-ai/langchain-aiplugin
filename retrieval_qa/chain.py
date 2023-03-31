from pathlib import Path
from langchain.llms import OpenAI
import pickle
from langchain.chains import RetrievalQA

DIR_PATH = Path(__file__).parent


def get_chain():
    with open(DIR_PATH / "vectorstore.pkl", "rb") as f:
        vectorstore = pickle.load(f)
    return RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0),
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
    )
