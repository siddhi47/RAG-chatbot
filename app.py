from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

load_dotenv()
import shutil
from rag_chatbot.rag_retrieval import RAGRetrieverGeneration
from rag_chatbot.rag_indexing import RAGIndexing
from langchain_chroma import Chroma
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
import warnings
from flask import request, jsonify
import os
import loguru


warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

llm = init_chat_model("gpt-3.5-turbo", model_provider="openai")
chroma = Chroma(
    collection_name="PDFRAG",
    persist_directory="./chroma_langchain_db",
    embedding_function=OpenAIEmbeddings(
        model="text-embedding-ada-002",
    ),
)

rag_indexing = RAGIndexing(
    model="text-embedding-ada-002",
    persist_directory="./chroma_langchain_db",
    logger=loguru.logger,
)
rag_retrieval = RAGRetrieverGeneration(chroma, llm)
retriever = rag_retrieval.graph_builder()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    url = request.form.get("url")

    if file:
        filename = file.filename
        save_path = os.path.join("uploads", filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(save_path)
        rag_indexing.create_index(save_path)
        return jsonify({"status": "success", "type": "file", "filename": filename})

    if url:
        rag_indexing.create_index(url)
        return jsonify({"status": "success", "type": "url", "url": url})

    return jsonify({"status": "error", "message": "No file or URL provided"}), 400


@app.route("/delete", methods=["POST"])
def delete():
    try:
        shutil.rmtree("uploads")
        shutil.rmtree("./chroma_langchain_db")
        return jsonify({"status": "success", "message": "Files deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("user_message")
def handle_user_message(data):
    user_msg = data.get("message", "")
    print(f"User: {user_msg}")

    retrieved_docs = retriever.invoke({"question": user_msg})
    bot_reply = retrieved_docs["answer"].content

    emit("bot_reply", {"message": bot_reply})


if __name__ == "__main__":
    socketio.run(app, debug=True)
