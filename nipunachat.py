import streamlit as st
from openai import AzureOpenAI
import pandas as pd
import pdfplumber
import tempfile

# Azure OpenAI Client
client = AzureOpenAI(
    api_key="3SpmpodXBzKYWZnIBcAkxDR5DTFJfDBRFWlASKb1sY7Fe52e2CTbJQQJ99BDACYeBjFXJ3w3AAABACOGlumZ",
    api_version="2024-12-01-preview",
    azure_endpoint="https://pavani-day3.openai.azure.com/"
)

st.title("🧠 Multi Modal Chatbot")

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system",
        "content": "You are a helpful assistant. If a file is uploaded, summarize it or answer based on its content."
    }]

if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

# File Uploader (PDF and Excel only)
uploaded_file = st.file_uploader(
    "Upload PDF or Excel file",
    type=["pdf", "xlsx", "jpg", "png", "jpeg"],
    accept_multiple_files =True
)

file_text = []


for file in uploaded_file:
    file_type = file.type
    uploaded_file =file 

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    if "pdf" in file_type:
        with pdfplumber.open(tmp_path) as pdf:
            file_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    elif "excel" in file_type or "spreadsheet" in file_type:
        df = pd.read_excel(tmp_path)
        file_text = df.to_markdown()
    elif "image" in file_type:
        st.image(tmp_path, caption="Uploaded Image", use_column_width=True)
        file_text = "Image uploaded. Please describe the content or ask a question about it."

    if file_text:
        st.session_state.messages.append({
            "role": "user",
            "content": f"I've uploaded a file. Please analyze the following content:\n{file_text}"
        })
        st.session_state.file_uploaded = True

# Show Chat History
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    visible_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=visible_messages
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})