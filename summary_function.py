from PyPDF2 import PdfReader
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import  FAISS
import openai
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
import streamlit as st

# Functions
def extract_raw_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    raw_text = ""
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_text += text
    return raw_text

def get_answer(docsearch, query):
    docs = docsearch.similarity_search(query, top_k=3)
        
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=st.session_state.get("OPENAI_API_KEY"))
    chain = load_qa_chain(llm=llm, chain_type= "stuff")
    with get_openai_callback() as callback:
        answer = chain.run(input_documents = docs, question = query)
    return callback, answer

def ask_question(paragraph):
    chat_history = [
        {'role': 'system', 'content': 'you are a helpful assistant.'},
        {'role': 'user', 'content': "Can you rephrase the texts shorter and in clear structure? " + '"""' +paragraph + '"""'},
        {'role': 'assistant', 'content': ""},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )

    answer = response.choices[0].message.content
    return answer

def ask_question2(original_summary, query, docsearch):
    openai.api_key = st.session_state.get("OPENAI_API_KEY")
    _, add_answer = get_answer(docsearch= docsearch, query = query)

    chat_history = [
        {'role': 'system', 'content': 'you are a helpful assistant.'},
        {'role': 'user', 'content': "Can you add this text" +  '"""' + add_answer +  '""" to' + original_summary + ' """"?'},
        {'role': 'assistant', 'content': ""},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )

    answer = response.choices[0].message.content
    return answer




def generate_summary(file_path, api_key):
    openai.api_key = st.session_state.get("OPENAI_API_KEY")

    # Read the PDF file
    raw_text = extract_raw_text_from_pdf(file_path)

    if "References" in raw_text:
        raw_text = re.sub(r'References.*$', '', raw_text)


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(raw_text)

    # download embeddings from OpenAI
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)

    docsearch = FAISS.from_texts(texts, embeddings)

    # read the questions from unconditional_Q.txt and store them in a list
    with open('unconditional_Q.txt', 'r') as f:
        questions = f.readlines()
    query_list = [q.strip() for q in questions]

    answer_list = []
    for query in query_list:
        _, ans = get_answer(docsearch, query)
        answer_list.append(ans)

    # join the answer together
    whole_answer = ' '.join(answer_list)
    print("get all the answers")
    

    openai.api_key = api_key
    try:
        answer = ask_question(whole_answer)
    except Exception as e:
        print(f"An error occurred while communicating with OpenAI: {e}")
    print("get the initial summary")
    return docsearch, answer



