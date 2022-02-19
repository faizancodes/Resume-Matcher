
from PIL import Image
import numpy as np
import streamlit as st

from nltk.tokenize import word_tokenize, sent_tokenize
import base64
import tempfile
import math

import PyPDF2 
import numpy as np
import pandas as pd
from pathlib import Path
import warnings
from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer, util
import utils as ut

model = SentenceTransformer('distilbert-base-nli-mean-tokens')
warnings.filterwarnings("ignore")    


hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """
            

def show_pdf(file_path:str):
    """Show the PDF in Streamlit
    That returns as html component
    Parameters
    ----------
    file_path : [str]
        Uploaded PDF file path
    """

    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)



 
def sentence_similarity(s1, s2):
    return float(util.pytorch_cos_sim(s1, model.encode(s2))[0][0])



resume = []
stopwords2 = []
resumeText = ''
resumeWords = ''
stwords = ''

st.write("""
         # Resume Analyzer
         """
         )


uploaded_file = st.file_uploader("Upload your Resume", type=["pdf"])

if uploaded_file is not None:
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        fp = Path(tmp_file.name)
        fp.write_bytes(uploaded_file.getvalue())
        st.write(show_pdf(tmp_file.name))
        print(tmp_file.name)
    
    pdfFileObj = open(tmp_file.name, 'rb') 
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
    pageObj = pdfReader.getPage(0) 
    
    rawPageText = pageObj.extractText().replace('\n', '')
    rawPageText = rawPageText.split('  ')
    pageText = [] 


    for line in rawPageText:

        if len(line) > 0:
            pageText.append(line)
            

    for line in pageText:
        
        tokens = sent_tokenize(line)
        
        for line in tokens:
            
            if len(line) > 1 and line[0] == ' ': line = line[1:]
            resume.append(line)
        
        
    j = open("stopwords2.txt", "r", encoding="utf8")

    for line in j:
        if len(line) > 1:
            stopwords2.append(line.replace('\n', ''))  


    resumeText = ' '.join(map(str, resume)) 
    resumeWords = ut.getWordCount(resumeText, 15, '')

    print('\nMost common words in your resume:\n')
    print(resumeWords)
    print()
    

st.markdown("***")

if len(resumeWords) > 0:
    
    title = st.header('Most Common Words:')

    resume_col1, resume_col2 = st.columns(2)
    resume_col1.table(pd.DataFrame(resumeWords, columns=['Word', 'Freq']))
    resume_col2.table(pd.DataFrame(ut.get_tf_idf(resumeText, 15).items(), columns=['Word', 'TF-IDF']))

    st.markdown("***")
    
    job_desc_header = st.header('Paste Job Description')
    job_desc = st.text_area('')
    
    if len(job_desc) > 0:
        
        job_desc_tokens = []
        for line in sent_tokenize(job_desc):
            for word in line.split(' '):
                job_desc_tokens.append(word)
        
        
        st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.table(pd.DataFrame(ut.getWordCount(' '.join(map(str, job_desc_tokens)) , 15, ''), columns=['Word', 'Freq']))
        col2.table(pd.DataFrame(ut.get_tf_idf(job_desc, 15).items(), columns=['Word', 'TF-IDF']))
        
        maxSentSims = []
        all_sents = []
        
        with st.spinner('Wait for it...'):
            
            for line in resume:

                if len(line) >= 40:

                    sentSims = []
                    s1 = model.encode(line)

                    for sent in sent_tokenize(job_desc):

                        if len(sent) >= 40:

                            s = sentence_similarity(s1, sent)
                            sentSims.append(s)
                            all_sents.append([s, line, sent])
                    
                    maxSentSims.append(max(sentSims))


        maxSentSims.sort(reverse=True)
        sentSimilarity = round(sum(maxSentSims[0:10]) / len(maxSentSims[0:10]) * 100, 2)
        st.header('Your resume is ' + str(sentSimilarity) + '% similar to the job description')
        
        st.markdown("Matching Sentences:")

        all_sents.sort(key=lambda x: x[0], reverse=True)
        
        df = pd.DataFrame(all_sents, columns=['Similarity', 'Resume Sentence', 'Job Description Sentence'])
        st.table(df)
     
        
