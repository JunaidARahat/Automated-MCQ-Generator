import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import required modules
from mcq_generator.utils import read_file, get_table_data
from mcq_generator.logger import logging
from langchain.globals import set_verbose
from langchain_community.callbacks import get_openai_callback
from mcq_generator.mcq_generator import generate_and_evaluate_quiz

import streamlit as st

# Enable verbose logging for LangChain
set_verbose(True)

# Load response JSON
with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# STREAMLIT PART

# Fetch the API key
st_key = os.getenv("OPEN_AI_KEY")

# Streamlit App Title
st.title("MCQ Generator")

# Input Form
with st.form("user_inputs"):
    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF or text file")
    
    # Other user inputs
    mcq_count = st.number_input("No of Questions", min_value=3, max_value=50)
    subject = st.text_input("Insert the Subject", max_chars=20)
    tone = st.text_input("Complexity level of Questions", max_chars=20, placeholder="Simple")
    button = st.form_submit_button("Create MCQs")
    
    # Check for button click and valid inputs
    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("Loading..."):
            try:
                # Read the uploaded file
                text = read_file(uploaded_file)
                
                # Call the LLM and track token usage
                with get_openai_callback() as cb:
                    response = generate_and_evaluate_quiz(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")
            else:
                # Display token usage statistics
                print(f"Total Tokens: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost: {cb.total_cost}")
                
                # Handle the response
                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            # Display the quiz in a table
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            
                            # Display review text area
                            st.text_area(label="Review", value=response["review"])
                        else:
                            st.error("Error in the table data")
                    else:
                        st.error("Quiz generation failed.")
                else:
                    st.write(response)
