# ResumeMatcher
See how your resume would stack up against an employer's ATS system! Quantify the text in your resume with NLP to calculate how good of a match you are for an internship position.

Having a good resume is the first step in landing an internship, without the right keywords and content in your sentences, you will likely not get past the first stage in the application process and not get an interview.

Utilize this program to improve your resume and add in the recommended keywords to boost your chances of getting hired!

### Note
  - This program is computationally intensive and requires much time to finish running, depending on the amount of job listings found. It is best to leave this program running and check back on it after some time.

# How to Run the Code
  - Clone the repository `git clone https://github.com/faizancodes/ResumeMatcher.git`
  
  - Navigate to the downloaded folder `cd ResumeMatcher`
  
  - Upload your resume in the ResumeMatcher folder and name it `resume.pdf`. Make sure it is saved as a pdf

  - Your folder should contain all these files:
  ![Screenshot 2020-12-30 125502](https://user-images.githubusercontent.com/43652410/103371757-46520280-4a9e-11eb-911e-e2c59b1e94c2.png)


  - Download all the dependencies`pip install -r requirements.txt`
    - If that gives you an error, try `python -m pip install -r requirements.txt` or `py -m pip install -r requirements.txt`

  - Download the NLP model `python -m spacy download en_core_web_lg`  
  
  - Run the code `resumematcher.py`
     - Try running `python resumematcher.py` if you encounter an error 
