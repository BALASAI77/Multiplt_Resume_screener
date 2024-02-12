import pandas as pd
import numpy as np
import streamlit as st
import os
import PyPDF2
import re
import google.generativeai as genai

# Configure Google API key

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#print(("GOOGLE_API_KEY"))

# Function to extract text chunks from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    extracted_text = ""
    for page_num in range(len(pdf_reader.pages)):
        page_text = pdf_reader.pages[page_num].extract_text()
        cleaned_text = re.sub(r'\s+', ' ', page_text).strip()
        extracted_text += cleaned_text
    return extracted_text

# Function to generate response using Gemini
def get_gemini_response(propmt,text,input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt,text,input])
    return response.text

# Streamlit app
st.set_page_config(page_title="Multipe Resume Screener")
st.title("Multipe Resume Screener")
st.subheader('Upload the resumes : ')
uploaded_files = st.file_uploader("Upload multiple PDF files", type=["pdf"], accept_multiple_files=True)
st.text('Enter the question :')
input = st.text_input("Enter your question")

if st.button("Generate Response"):
    if uploaded_files:
        # Extract text from each PDF and concatenate it
        concatenated_text = ""
        total_pdfs = len(uploaded_files)
        df = pd.DataFrame(columns=["PDF Text"])
        for i, uploaded_file in enumerate(uploaded_files, 1):
            text = extract_text_from_pdf(uploaded_file)
            pdf_prefix = f"PDF {i} out of {total_pdfs}: "
            concatenated_text += pdf_prefix + text + ". "
            df.loc[i-1]=concatenated_text

        
        text_to_process = df['PDF Text'].str.cat(sep=' ')
        # Generate response using Gemini model
        prompt='You will receive the text about different candidates about their resumes.Consider each line till a full stop encountered as a candidate. you need to read all the text and just give answer as per the users demand.Remainder: Just give the answer to the users request. '
        response = get_gemini_response(prompt,text_to_process,input)
        st.subheader("Response:")
        st.write(response)
    else:
        st.warning("Please upload PDF files")

