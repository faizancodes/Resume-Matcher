import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
import collections
from nltk import tokenize
from operator import itemgetter
from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer, util
import math

stop_words = set(stopwords.words('english'))
model = SentenceTransformer('distilbert-base-nli-mean-tokens')

stop_words2 = []
sw2 = open("stopwords2.txt", "r", encoding="utf8")

for line in sw2:
    if len(line) > 1:
        stop_words2.append(line.replace('\n', ''))  


def getWordCount(lst, nPrint, companyName):
    
    # Instantiate a dictionary, and for every word in the file, 
    # Add to the dictionary if it doesn't exist. If it does, increase the count.
    wordcount = {}

    for word in lst.lower().split():

        finalStr = ''

        for c in word:
            if c.isalnum():
                finalStr += c
        
        if finalStr not in stop_words and finalStr not in stop_words2 and len(finalStr) > 3 and finalStr != companyName:

            if finalStr not in wordcount:
                wordcount[finalStr] = 1
            else:
                wordcount[finalStr] += 1


    word_counter = collections.Counter(wordcount)
    lst = word_counter.most_common(nPrint)

    return lst


def sentence_similarity(s1, s2):
    return float(util.pytorch_cos_sim(model.encode(s1), model.encode(s2))[0][0])



def get_tf_idf(doc, n):

    # Step 1 : Find total words in the document
    total_words = doc.split()
    total_word_length = len(total_words)

    # Step 2 : Find total number of sentences
    total_sentences = tokenize.sent_tokenize(doc)
    total_sent_len = len(total_sentences)

    # Step 3: Calculate TF for each word
    tf_score = {}
    for each_word in total_words:
        each_word = each_word.replace('.','')
        if each_word not in stop_words and each_word.isalpha() and len(each_word) >= 3:
            if each_word in tf_score:
                tf_score[each_word] += 1
            else:
                tf_score[each_word] = 1


    # Dividing by total_word_length for each dictionary element
    tf_score.update((x, y/int(total_word_length)) for x, y in tf_score.items())


    # Check if a word is there in sentence list
    def check_sent(word, sentences): 
        final = [all([w in x for w in word]) for x in sentences] 
        sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
        return int(len(sent_len))


    # Step 4: Calculate IDF for each word
    idf_score = {}
    for each_word in total_words:
        each_word = each_word.replace('.','')
        if each_word not in stop_words:
            if each_word in idf_score:
                idf_score[each_word] = check_sent(each_word, total_sentences)
            else:
                idf_score[each_word] = 1

    # Performing a log and divide
    idf_score.update((x, math.log(int(total_sent_len)/y)) for x, y in idf_score.items())

    # Step 5: Calculating TF*IDF
    tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()} 

   
    result = dict(sorted(tf_idf_score.items(), key = itemgetter(1), reverse = True)[:n]) 
    return result
    