from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.documents import Document
from langchain import hub


PROMPT = hub.pull("rlm/rag-prompt")


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


class RAGRetrieverGeneration:
    def __init__(self, vector_store, llm):
        self.vector_store = vector_store
        self.llm = llm

    def retrieve(self, state):
        # Retrieve documents from the vector store
        retrieved_docs = self.vector_store.similarity_search(state["question"])
        return {
            "context": retrieved_docs,
        }

    def generate(self, state):
        docs_content = "\n\n".join([doc.page_content for doc in state["context"]])
        message = PROMPT.invoke(
            {
                "question": state["question"],
                "context": docs_content,
            }
        )

        response = self.llm.invoke(message)

        return {
            "answer": response,
        }

    def graph_builder(self):
        graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        return graph
