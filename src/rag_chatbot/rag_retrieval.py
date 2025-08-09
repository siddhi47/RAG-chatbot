from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict, Optional
from langchain_core.documents import Document
from langchain import hub
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain_chroma import Chroma

class State(TypedDict):
    question: str
    local_context: List[Document]       # Retrieved from vector store
    web_context: Optional[List[Document]]  # Retrieved via web search
    merged_context: List[Document]      # Final set of docs passed to LLM
    answer: Optional[str]   

PROMPT = hub.pull("rlm/rag-prompt")
class RAGRetrieverGeneration:
    """
        REtrieves documents from a vector store and generates answers using an LLM.
        It can also search the web for additional information if needed.

    """
    def __init__(self, vector_store:Chroma, llm:str)->None:
        """
            param vector_store: Vector store to retrieve documents from
            llm: Language model to generate answers
        """
        self.vector_store = vector_store
        self.llm = llm

        # Web search tool
        search_tool = Tool(
            name="web_search",
            func=DuckDuckGoSearchRun().run,
            description="Search the web for current or missing information."
        )

        # Agent that can decide to search
        self.web_agent = initialize_agent(
            [search_tool],
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def retrieve(self, state) -> dict:
        """
            Retrieves relevant documents from the vector store based on the question.
        """
        retrieved_docs = self.vector_store.similarity_search(state["question"])
        return {"local_context": retrieved_docs}

    def search_web(self, state) -> dict:
        """
            Searches the web for additional information if local context is insufficient.
        """
        # Let the agent decide how to search
        search_result = self.web_agent.run(f"Search for: {state['question']}")
        doc = Document(page_content=search_result)
        return {"web_context": [doc]}

    
    def generate(self, state) -> dict:
        """
            Generates an answer using the retrieved documents.
        """
        summaries = [self.llm.invoke(f"Summarize:\n\n{doc.page_content}") 
             for doc in state.get("merged_context", [])]
        
        docs_content = "\n\n".join(summaries)
        message = PROMPT.invoke({
            "question": state["question"],
            "context": docs_content,
        })
        response = self.llm.invoke(message)
        return {"answer": response}

    def merge_contexts(self, state) -> dict:
        """
            Merges local and web contexts into a single list of documents.
        """
        merged_docs = state["local_context"] + (state.get("web_context") or [])
        return {"merged_context": merged_docs}

    def graph_builder(self)-> StateGraph:
        """
            Builds the state graph for the RAG retrieval and generation process.
        """
        graph_builder = StateGraph(State)
        graph_builder.add_sequence([self.retrieve, self.search_web,self.merge_contexts, self.generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        return graph

