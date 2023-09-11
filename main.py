import streamlit as st
import os
import base64
import summary_function
import openai

# Add a title to your web application
st.title("Summarize For You")

# get the api key from the user
st.session_state.api_key = st.text_input("Enter your OpenAI API key", value="", type="password")

# create a .env file and add the api key to it
with open(".env", "w") as f:
    f.write(f"OPENAI_API_KEY={st.session_state.api_key}")


# check if 'file_uploaded' is in st.session_state
if 'file_uploaded' not in st.session_state:
    # Initialize session state variables
    st.session_state.file_uploaded = False
    st.session_state.file_name = None
    st.session_state.answer = ""
    st.session_state.docsearch = None
    st.session_state.question = None

# if file_uploaded is False, then ask the user to upload a file
if st.session_state.file_uploaded is False:
    # Add a file uploader and a submit button
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    submit_button = st.button("Submit")

    # Provide feedback when the PDF file is uploaded successfully
    if submit_button and uploaded_file is not None:
        st.session_state.file_uploaded = True
        st.write("File uploaded successfully!")
        # Get the name of the uploaded file
        st.session_state.file_name = uploaded_file.name

        # save the uploaded pdf file to data folder
        with open(os.path.join("data", st.session_state.file_name), "wb") as f:
            f.write(uploaded_file.getbuffer())

        # read the pdf file from data folder
        file = open(os.path.join("data", st.session_state.file_name), "rb")

        # display the pdf file with markdown
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")
        pdf_display_placeholder = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="800" style="border: none;"></iframe>'
        st.markdown(pdf_display_placeholder, unsafe_allow_html=True)
        st.markdown(" ")
        st.markdown(" ")

        # Generate the summary and store it in session state
        try:
            with st.spinner("Generating summary..."):
                st.session_state.docsearch, st.session_state.answer = summary_function.generate_summary(os.path.join("data", st.session_state.file_name), st.session_state.api_key)
            # Display the summary
            st.markdown("<h3>Here Is The Original Summary:</h3>", unsafe_allow_html=True)
            st.text_area("Summary", value=st.session_state.answer, height=400)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        # if the summary is generated successfully then ask questions
        if st.session_state.answer != "":
            st.session_state.question = st.text_input("Do you have questions about the summary?", value="", type="default")
            
        # if the summary is generated successfully then show the 'satisfied' button
        if st.session_state.answer != "":
            satisfied_button  = st.button("Satisfied, Go for the next paper!")
            if satisfied_button:
                # delete all session state variables except api_key
                del st.session_state.file_uploaded 
                st.experimental_rerun()
                

        




elif st.session_state.file_uploaded is True and st.session_state.question is not None:
    st.write("Let's improve the summary!")
    st.session_state.new_answer = ""

    # display the pdf file with markdown
    file = open(os.path.join("data", st.session_state.file_name), "rb")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="800" style="border: none;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")

    # generate new summary
    openai.api_key = st.session_state.api_key
    with st.spinner("Generating improved summary..."):
        st.session_state.new_answer = summary_function.ask_question2(st.session_state.answer, st.session_state.question, st.session_state.docsearch)
    # Add the text with a larger font size using Markdown
    st.markdown("<h3>Here Is The Improved Summary:</h3>", unsafe_allow_html=True)
    st.text_area("Summary",value=st.session_state.new_answer, height=400)

    # if the summary is generated successfully then ask questions
    if st.session_state.answer != "":
        st.session_state.question = st.text_input("Do you have questions about the summary?", value="", type="default")
        
    # if the summary is generated successfully then show the 'satisfied' button
    if st.session_state.answer != "":
        satisfied_button = st.button("Satisfied, Go for the next paper!")
        if satisfied_button:
            # delete all session state variables except api_key
            del st.session_state.file_uploaded 
            st.experimental_rerun()




