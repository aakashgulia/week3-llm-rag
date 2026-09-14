import streamlit as st
import requests

API_URL = "http://localhost:8501/ask-services"

st.set_page_config(
    page_title="Hybrid LLM Assistant",
    page_icon="🤖",
    layout="centered"
)

with st.sidebar:
    st.header("⚙️ System Info")

    model = st.selectbox(
        "Choose Model",
        ["Code Llama 7B", "StarCoder2 3B", "Phi-3 Mini"]
    )

    model_map = {
        "Code Llama 7B": "codellama:7b-instruct",
        "StarCoder2 3B": "starcoder2:3b",
        "Phi-3 Mini": "phi3:mini"
    }

    selected_model = model_map[model]

    st.write(f"**LLM:** {model}")
    st.write("**Retrieval:** BGE Small")
    st.write("**Backend:** FastAPI + Ollama")
    st.write("**RAG:** Enabled")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 Hybrid LLM Inference Assistant")
st.caption("RAG-powered assistant using the existing FastAPI + Ollama pipeline")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a question about the knowledge base...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.get(
                    API_URL,
                    params={
                        "question": question,
                        "model": selected_model
                    },
                    timeout=600
                )

                if response.status_code == 200:
                    data = response.json()

                    answer = data.get(
                        "answer",
                        "No answer returned."
                    )
                    source = data.get(
                        "source_document",
                        "Unknown"
                    )
                    similarity = data.get(
                        "similarity_score",
                        0
                    )

                    st.markdown(answer)

                    st.caption(
                        f"📄 Source: {source} | "
                        f"🔍 Similarity: {similarity:.4f}"
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                else:
                    st.error(
                        f"Backend error: {response.status_code}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
