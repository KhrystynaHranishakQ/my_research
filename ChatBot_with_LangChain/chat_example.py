import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from retrieve_context import CustomEmbeddingRetriever
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import prompts
from langchain import PromptTemplate
import streamlit as st

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4-1106-preview"

retriever = CustomEmbeddingRetriever(n=3)


class ProductDataChatbot:

    def __init__(self):
        self.openai_model = MODEL
        self.retriever = retriever

    @st.cache_resource
    def set_up_qa_chain(_self):

        prompt = PromptTemplate(template=prompts.system_prompt, input_variables=["context", "question"])
        updated_question_prompt = PromptTemplate.from_template(prompts.update_question)

        # Setup memory for contextual conversation
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True
        )

        # Setup LLM and QA chain
        llm = ChatOpenAI(model_name=_self.openai_model, temperature=0, streaming=True)

        qa_chain = ConversationalRetrievalChain.from_llm(llm,
                                                         retriever=_self.retriever,
                                                         memory=memory,
                                                         condense_question_prompt=updated_question_prompt,
                                                         verbose=True,
                                                         condense_question_llm=ChatOpenAI(model_name=_self.openai_model, temperature=0),
                                                         return_source_documents=False,
                                                         combine_docs_chain_kwargs={'prompt': prompt}
                                                         )
        return qa_chain
