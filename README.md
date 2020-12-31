# Resume Matcher
  - See how your resume would stack up against an employer's ATS system! Quantify the text in your resume with natural language processing to calculate how good of a match you are for an internship position.

  - Having a good resume is the first step in landing an internship, without the right keywords and content in your sentences, you will likely not get past the first stage in the application process and not get an interview.

  - The code for this project is built off of a previous project of mine found [here](https://github.com/faizancodes/Job-Listing-Scraper) which mainly gets you the job listings and links to apply, etc. This program contains a lot of the same code, but with NLP techniques, it is meant to help you assess how good of a match you are for a job position, and help you improve your resume by recommending keywords you should add in. 

- This program works by comparing the contents of your resume to the contents of the full job description found for each job posting on [Indeed](https://www.indeed.com/) and calculating how similar the text is using [spaCy](https://spacy.io/) and [Wordnet](https://github.com/nihitsaxena95/sentence-similarity-wordnet-sementic).

 # Similarity Metrics 
 
  - **In the attached `Software Engineer Intern Job Postings.csv` file, there are 4 columns in particular to review:**
  
    **The values in the csv file are based on my resume and the description of the values listed below are based on my findings**
    
      - **Keyword Similarity:** This is a calculation of how similar the most common words in your resume are with the most common words in the job description. 
          - Values > 60 mean you have very effective keywords for the particular position
          - Values 50 <= x <= 60 mean you have good keywords for the position
          - Values < 50 mean you should update your resume before applying
         
         
      - **Sentence Similarity:** This is a calculation of how similar the sentences in your resume are with the sentences in the job description. 
          - Values 45 <= x <= 50 mean the content of your resume is a great fit for the position
          - Values 40 <= x <= 45 mean the content of your resume is a good fit for the position
          - Values < 40 mean you should revise your resume before applying
      
      
      - **Overall Similarity:** This is the sum of the Keyword Similarity and Sentence Similarity 
          - Values >= 90 mean you are an excellent match
          - Values 80 <= x <= 90 mean you are a good match
          - Values < 80 mean you should revise your resume before applying, add in the suggested keywords 
      
      - **Recommended Words:** These are the most common words in the job description and you should add them to your resume
  
# How to Run the Code
  
  - If you do not have **git** installed, download it [here](https://git-scm.com/downloads)
  - If you do not have **pip** installed, download it [here](https://pip.pypa.io/en/stable/installing/)
  
  - Clone the repository `git clone https://github.com/faizancodes/Resume-Matcher.git`
  
  - Navigate to the downloaded folder `cd Resume-Matcher`
  
  - Upload your resume in the Resume-Matcher folder and name it `resume.pdf`. Make sure it is saved as a pdf

  - Your folder should contain all these files:
  
 ![image](https://user-images.githubusercontent.com/43652410/103389566-b03dcc80-4add-11eb-866c-830e68b28f6b.png)
   
  - Create and activate a virtual environment
      
      - **Windows:**
        ```
        py -3.6 -m venv env
        env\Scripts\activate
        ```
      - **Mac & Linux**
        ```
        python3.6 -m venv env
        source env/bin/activate
        ```   

  - Download all the dependencies`pip install -r requirements.txt`
  
    - If that gives you an error, try
    
      - `python -m pip install -r requirements.txt` or
      
      - `pip3 install -r requirements.txt` if you are on Mac
     

  - Download the NLP model `python -m spacy download en_core_web_lg` (850 MB necessary)
  
  - Run the code `resumematcher.py`
     - Try running `python resumematcher.py` if you encounter an error 
     
# Note 

   - This program is computationally intensive and requires a decent amount time to finish running, depending on the amount of job postings found. It took around 20 minutes to finish running through 115 job postings, seen in the attached csv file 

  - When the program starts running, it will print the most common words in your resume, indicated by `(word, frequency)`. Then the program starts iterating through the job postings and calculating the corresponding similarity scores 
    
     - The program outputs the most common words for each job description and the direct link to apply for each job posting (as seen in the screenshot below), which you can simply copy paste into your browser, so you do not have to wait until the entire program is finished running.
     
     - When the program is finished running, it puts all the data into a csv file which you can open with Excel. From there, you can sort the 'Overall Similarity' column to find the jobs you matched the best with.  
  
  ![image](https://user-images.githubusercontent.com/43652410/103391985-c782b700-4ae9-11eb-95ff-f721239014ab.png)

