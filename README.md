# RAG Chatbot

This repository contains a simple RAG (Retrieval-Augmented Generation) chatbot built using LangChain, LangGraph, ChromaDB, LangSmith, OPenAI, and Flask.

Make sure you have python 3.12 or higher installed on your system.

## Project Setup

### Clone the Repository

```bash
git clone https://github.com/siddhi47/RAG-chatbot.git
```

### Setup OPenAI API Key

OpenAI API key is required to run the chatbot. You can set it as an environment in .env file. Refer to the `.env.example` file for the required variables. You can get your OpenAI API key from [OpenAI](https://platform.openai.com/account/api-keys).

### Setup LangSmith API Key [Optional]

Optionally, you can set up LangSmith API key to log the interactions with the chatbot. You can get your LangSmith API key from [LangSmith](https://smith.langchain.com/).

### Setup Virtual Environment

You can set up a virtual environment to run the project. You can use `venv` or `virtualenv` to create a virtual environment. Here is an example using `venv`:

```bash
venv venv
source venv/bin/activate
pip install -e .
```

### Run the Application

Once you have activated the environment, you can run the application using the following command:

```bash
python app.py
```

This will run the app on port 5000 by default. You can access the chatbot at `http://localhost:5000`.

## Run using Docker

Make sure you have Docker installed on your system. Refer to the [Docker documentation](https://docs.docker.com/get-docker/) for installation instructions.

Make sure you have the `.env` file in the root directory of the project with the required environment variables.

Run the following command to build the Docker image:

```bash
docker build -t rag-chatbot .
docker run -p 5000:5000 --env-file .env rag-chatbot
```
