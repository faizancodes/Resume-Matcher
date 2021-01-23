
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords 
from nltk import pos_tag
from nltk.corpus import wordnet as wn

import PyPDF2 
import numpy as np
import spacy
import collections
import pandas as pd
import matplotlib.pyplot as plt
import re

import requests
from bs4 import BeautifulSoup
from itertools import cycle
import csv 
import os
import warnings


warnings.filterwarnings("ignore")    
nlp = spacy.load("en_core_web_lg")


# Get Proxies 
def getProxies(inURL):
    
    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    terms = soup.find_all('tr')
    IPs = []

    for x in range(len(terms)):  
        
        term = str(terms[x])        
        
        if '<tr><td>' in str(terms[x]):
            pos1 = term.find('d>') + 2
            pos2 = term.find('</td>')

            pos3 = term.find('</td><td>') + 9
            pos4 = term.find('</td><td>US<')
            
            IP = term[pos1:pos2]
            port = term[pos3:pos4]
            
            if '.' in IP and len(port) < 6:
                IPs.append(IP + ":" + port)
                #print(IP + ":" + port)

    return IPs 


# Cycle through the proxies and get one to use 
proxyURL = "https://www.us-proxy.org/"
pxs = getProxies(proxyURL)
proxyPool = cycle(pxs)

resume = []
stopwords2 = []
resumeText = ''
resumeWords = ''
stwords = ''


def extractTextFromResume():
    
    global resume
    global stopwords2
    global resumeText
    global resumeWords
    global stwords
    
    # Parsing the resume and extracting the text from it

    pdfFileObj = open('resume.pdf', 'rb') 
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
    pageObj = pdfReader.getPage(0) 
    stwords = set(stopwords.words('english'))

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
            
        
    '''
    Load in the list of stopwords
    These are words we do not want to be included in the analysis
    '''

    j = open("stopwords2.txt", "r", encoding="utf8")

    for line in j:
        if len(line) > 1:
            stopwords2.append(line.replace('\n', ''))  


    resumeText = ' '.join(map(str, pageText)) 
    resumeWords = getWordCount(resumeText, 15, '')

    print('\nMost common words in your resume:\n')
    print(resumeWords)
    print()


'''
Key Word Similarity
Find the most common words in the corpus of text
'''

def getWordCount(lst, nPrint, companyName):
    
    # Instantiate a dictionary, and for every word in the file, 
    # Add to the dictionary if it doesn't exist. If it does, increase the count.
    wordcount = {}

    for word in lst.lower().split():

        finalStr = ''

        for c in word:
            if c.isalnum():
                finalStr += c
        
        if finalStr not in stwords and finalStr not in stopwords2 and len(finalStr) > 3 and finalStr != companyName:

            if finalStr not in wordcount:
                wordcount[finalStr] = 1

            else:
                wordcount[finalStr] += 1


    word_counter = collections.Counter(wordcount)

        
    lst = word_counter.most_common(nPrint)
    df = pd.DataFrame(lst, columns = ['Word', 'Count'])
    #df.plot.bar(x = 'Word', y = 'Count')
    
    return lst


'''
Sentence Similarity 
https://nlpforhackers.io/wordnet-sentence-similarity/
'''

def pennToWn(tag):
    
    # Convert between a Penn Treebank tag to a simplified Wordnet tag
    
    if tag.startswith('N'):
        return 'n'
 
    if tag.startswith('V'):
        return 'v'
 
    if tag.startswith('J'):
        return 'a'
 
    if tag.startswith('R'):
        return 'r'
 
    return None


def taggedToSynset(word, tag):
    
    wn_tag = pennToWn(tag)
    
    if wn_tag is None:
        return None
 
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None

    
def sentenceSimilarity(sentence1, sentence2):
    
    """ Compute the sentence similarity using Wordnet """
    
    # Tokenize and tag
    sentence1 = pos_tag(word_tokenize(sentence1))
    sentence2 = pos_tag(word_tokenize(sentence2))
 
    # Get the synsets for the tagged words
    synsets1 = [taggedToSynset(*taggedWord) for taggedWord in sentence1]
    synsets2 = [taggedToSynset(*taggedWord) for taggedWord in sentence2]
 
    # Filter out the Nones
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]
 
    score, count = 0.0, 0
    best_score = 0
 
    # For each word in the first sentence
    for synset in synsets1:
        
        scores = []
        
        # Get the similarity value of the most similar word in the other sentence
        for ss in synsets2:
            
            simi = synset.path_similarity(ss)
            
            if simi != None:
                scores.append(simi)
         
        if len(scores) >= 1:
            best_score = max(scores)
            score += best_score
            count += 1
 
    # Average the values
    
    if count != 0:
        score /= count
    else:
        score = 0
        
    return score


'''
Calculate Overall Match Score 
Combines Key Word Similarity & Sentence Similarity 
'''

def getResumeMatchScore(job, resume, positionText, resumeWords, positionWords):

    '''
    Key Word Similarity Calculation

    Iterate through the most common words in your resume 
    and calculate the similarity scores for each word 
    in relation to the most common words in the job description

    Find the max similarity score of each word and calculate
    the average of the scores in the end
    '''

    print(job[1], job[0])
    print(job[-1])
    print()
    print(positionWords)

    overallSimilarity = 0
    maxSims = []

    for i, word in enumerate(resumeWords):

        sims = []

        for j, word2 in enumerate(positionWords):

            sim = nlp(resumeWords[i][0]).similarity(nlp(positionWords[j][0]))

            if sim == 1: sim = sim * 1.5
            sims.append(sim)

            #print(sim, resumeWords[i][0], positionWords[j][0])

        maxSims.append(max(sims))


    keyWordSimilarity = round(sum(maxSims) / len(maxSims) * 100, 2)
    overallSimilarity = keyWordSimilarity

    print('\nKey Word Similarity:', keyWordSimilarity)


    '''
    Sentence Similarity Calculation

    Iterate through each line of your resume and find the sentence 
    that is most similar to it in the job description 

    Find the similarity values of the 15 most similar sentences and
    calculate the average of those values 
    '''

    maxSentSims = []

    for line in resume:

        if len(line) >= 30:

            sentSims = []
            sents = []

            for sent in positionText:

                if len(sent) >= 10:

                    s = sentenceSimilarity(line, sent)
                    sentSims.append(s)
                    sents.append(line + ' ' + sent)

            maxSentSims.append(max(sentSims))


    maxSentSims.sort(reverse=True)
    sentSimilarity = round(sum(maxSentSims[0:15]) / len(maxSentSims[0:15]) * 100, 2)
    
    overallSimilarity += sentSimilarity 


    print('Sentence Similarity:', sentSimilarity)

    print('\nOverall Score:', overallSimilarity)
    print()
    
    return keyWordSimilarity, sentSimilarity, overallSimilarity


def recommendKeyWords(positionWords):
    
    '''
    Recommend key words you should add to your resume
    '''
    
    resumeWordsList = [item for sublist in resumeWords for item in sublist if type(item) == str]
    recommendedWords = [] 

    for word in positionWords:
        if word[0] not in resumeWordsList:
            recommendedWords.append(word[0])

    recWordsStr = ' '.join(map(str, recommendedWords))
    
    return recWordsStr


def extractJobListings(url):
    
    '''
    Extract each individual job listing from the designated web page, indicated by the url
    For each individual listing, extract the title of the position, company, company rating,
    location, summary of the position, and the direct link to apply for the position
    '''

    page = requests.get(url, proxies = {"http": next(proxyPool)})
    soup = BeautifulSoup(page.text, 'html.parser')

    jobs = soup.find(id='resultsCol')
    job_elems = jobs.find_all('div', class_='jobsearch-SerpJobCard')
    
    # For Excel File 
    rows = []

    for desc in job_elems:

        # Extract only the job title 
        title = desc.find('h2', class_='title').text 


        # Get rid of uncessary whitespace and the word 'new'
        title = title.replace('new', '').replace('\n', '') 


        # Company name 
        company = desc.find('span', class_='company').text
        company = company.replace('\n', '')


        # Not all companies have a rating 
        try:
            rating = desc.find('span', class_='ratingsContent').text
            rating = rating.replace('\n', '')
        except:
            rating = '-'


        # Not all job postings have a listed location
        try:
            location = desc.find('span', class_='location').text
        except:
            location = '-'


        # Details of the job responsibilites 
        summary = desc.find('div', class_='summary').text
        summary = summary.replace('\n', '')


        # Extract direct URL to the job listing 
        rawLink = desc.find('a', class_='jobtitle')
        jobLink = rawLink.get('href')
        jobLink = jobLink[jobLink.find('?') + 1 : ]
        jobLink = ('https://www.indeed.com/viewjob?' + jobLink).replace('\n', '')

    
        # Some URLs are different 

        if 'jk=' not in jobLink:
            rawLink = str(rawLink.get('href'))
            
            try:
                jobLink = 'https://www.indeed.com/viewjob?cmp=' + company + '&t=' + rawLink[rawLink.find('jobs') + 5 : rawLink.rindex('-')] + '&jk=' + rawLink[rawLink.rindex('-') + 1 : rawLink.find('?')]
            except:
                jobLink = rawLink
        
        
        jobLink = jobLink.replace(' ', '')
        

        if len(jobLink) < 200:
            
            #print(jobLink)

            rows.append([title, company, rating, location, summary, jobLink])
    

    return rows


# Get the total amount of pages to scrape through for all job listings found 
def getNumListings(url):
    
    '''
    Calculate the total number of jobs found and how many
    pages of results there are
    '''

    page = requests.get(url, proxies = {"http": next(proxyPool)})
    soup = BeautifulSoup(page.text, 'html.parser')

    rawNumJobs = soup.find(id='searchCountPages').text.replace('\n', '')
    numJobs = rawNumJobs[rawNumJobs.find('of') + 3 : rawNumJobs.find('jobs')]
    
    numJobs = numJobs.replace(' ', '').replace(',', '')

    pages = (int(numJobs) // 15) + 1
    return numJobs, pages    



# Data for each row of the excel file will be stored in this 
csvRows = []

def clean(stng):
    
    # We want to get rid of these characters 
    bad_chars = ['[', ']', '"', ','] 

    for i in bad_chars : 
        stng = stng.replace(i, '') 
        
    return stng


def scrapeListings(position):
    
    '''
    Extract all the job listings found for the entered job position
    Iterate through all the pages of results and scrape the necessary information
    '''

    position_ = position.replace(' ', '+')
    page = 0
    
    totalJobs, pages = getNumListings('https://www.indeed.com/jobs?q=' + position_ + '&jt=internship')

    print('\n' + totalJobs + ' jobs found!', str(pages) + ' pages of results for ' + position + '\n')
    
    userPages = float(input('\nHow many pages of results would you like to go through? '))
    
    #Go through the specified amount of pages 
    for x in range(pages):

        url = 'https://www.indeed.com/jobs?q=' + position_ + '&jt=internship&start=' + str(page) 
        jobInfo = extractJobListings(url)

        csvRows.append(jobInfo)

        page += 10
        

allData = []

def findResumeMatches():
    
    '''
    Go through the job listings and extract the text that represents the job description
    Calculate the corresponding similarity score to determine how well of a match
    your resume is to that job position 
    '''

    print('\nIterating through job postings...\n')

    for row in csvRows:
        
        for job in row:
            
            page = requests.get(job[-1], proxies = {"http": next(proxyPool)})
            soup = BeautifulSoup(page.text, 'html.parser')
            
            positionDesc = soup.find('div', class_='jobsearch-jobDescriptionText')
            
            try:
                positionDesc = positionDesc.text
        
                positionDesc = positionDesc.replace('\n', '')
                positionDesc = sent_tokenize(positionDesc)

                positionText = []
                

                for line in positionDesc:
                    
                    if '-' in line:
                        
                        ls = line.split('-')

                        for l in ls:
                            if len(l) > 1:
                                positionText.append(l)
                                
                    else:
                        if len(line) > 1:
                            positionText.append(line)
                    

                p = ' '.join(map(str, positionText)) 
                positionWords = getWordCount(p, 15, job[1].lower())
            
                
                keywordSimi, sentSimi, overallSimi = getResumeMatchScore(job, resume, positionText, resumeWords, positionWords)
                recWords = recommendKeyWords(positionWords)
                
                allData.append([job[0], job[1], job[2], job[3], job[4], job[5], keywordSimi, sentSimi, overallSimi, recWords])
            
            except:
                print('Error', job[1], job[0])
                print(job[-1])


    # Column Names in the excel file  
    fields = 'Title, Company, Rating, Location, Summary, Job Link, KeyWord Similarity, Sentence Similarity, Overall Similarity, Recommended Words\n' 

    # Name of Excel file  
    fileName = position + " Job Postings.csv"
    
    #Write to excel file 
    MyFile = open(fileName, 'w', encoding="utf-8")

    MyFile.write(fields)
    
    #Append the data to the rows of the file 
    for job in allData:
        MyFile.write(clean(job[0]) + ',' + clean(job[1]) + ',' + clean(job[2]) + ',' + clean(job[3]) + ',' + clean(job[4]) + ',' + clean(job[5]) + ',' + str(job[6]) + ',' + str(job[7]) + ',' + str(job[8]) + ',' + str(job[9]))
        MyFile.write('\n')

    MyFile.close()

    path = os.getcwd()
    print('\nSaved as ' + path + '\\' + fileName)



position = input('Enter the job position you are searching for: ')
scrapeListings(position)

extractTextFromResume()
findResumeMatches()
