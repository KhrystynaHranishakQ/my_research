import streamlit as st
from streaming import StreamHandler
from chat_example import ProductDataChatbot


st.title("Chatbot")

chatbot = ProductDataChatbot()
qa_chain = chatbot.set_up_qa_chain()
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Вітаю Вас у **Koch-Chemie**! Чим я можу допомогти?"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User-provided prompt
if user_query := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        st_cb = StreamHandler(st.empty())
        response = qa_chain.run(user_query, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
