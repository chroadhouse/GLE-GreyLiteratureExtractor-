# So I have all the text now, I want to presnt it in a better format. 
import csv
import json 
import numpy as np
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.parsing.preprocessing import STOPWORDS
import os
import matplotlib.pyplot as plt
import pandas as pd 
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import stopwords


def read_data():
    with open('output.json', 'r') as file:
    # Load the JSON data into a list of dictionaries
        data = json.load(file)
    return data


def generate_textfiles(data):
    output_directory = 'text_files'

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Loop through each dictionary in the list
    for row in data:
        # Extract the column values
        file_name = row['ID']  # Assuming 'filename' is the column name you want to use for the file name
        text_content = row['Text']   # Assuming 'text' is the column you want to write to the text file
    
        # Create a new text file and write the content
        with open(os.path.join(output_directory, str(file_name) + '.txt'), 'w') as file:
            file.write(text_content)

def save_as_csv(data, topic):
    # Saving the topic list 
    headers = ['ID','Query','URL','Topic','Date','Time']
    with open('annotating_doc.csv', 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    
    topic_list = []
    for t in topic:
        temp = t.split(':')
        topicNumber = temp[0]
        topicWords = temp[1].replace('"','')
        topic_list.append({'Topic':topicNumber, 'Words':topicWords})
    
    with open('topic_list.csv', 'w+', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Topic','Words'])
        writer.writeheader()
        for row in topic_list:
            writer.writerow(row)
    

class TopicModelling():

    def __init__(self, data):
        self.data = data

    def preprocess(self, text):
        stemer = PorterStemmer()
        lemmatizer = WordNetLemmatizer()

        tokens = nltk.word_tokenize(text)
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
        stemmed_tokens = [stemer.stem(token) for token in lemmatized_tokens]
        
        stop_words = set(stopwords.words('english'))
        preprocessed_tokens = [token for token in stemmed_tokens if token not in stop_words and len(token) > 2]
        return preprocessed_tokens

    def train_model(self):
        tokenized_data = [self.preprocess(doc) for doc in self.data]
        dictionary = corpora.Dictionary(tokenized_data)
        bow_corpus = [dictionary.doc2bow(doc) for doc in tokenized_data]

        lda_model = LdaModel(bow_corpus, num_topics=10, id2word=dictionary, passes=250, random_state=1)
        topic_list = []
        for topic_num, topic_words in lda_model.print_topics(num_topics=1000):
       
            topic_list.append('Topic {}: {}'.format(topic_num, topic_words))
        doc_topic_model_likely = []
        document_topic_list = []

        for i, doc in enumerate(tokenized_data):
            doc_bow = dictionary.doc2bow(doc)
            doc_topics = lda_model.get_document_topics(doc_bow)

            doc_topic_model_likely.append(max(doc_topics, key=lambda x: x[1]))
            document_topic_list.append(doc_topic_model_likely[-1][0])
        return document_topic_list, topic_list
    


def main():
    data = read_data()
    text_list = [row['Text'] for row in data]
    text_list = [t.lower() for t in text_list]
    tp = TopicModelling(data=text_list)
    document_topic_list, topic_list = tp.train_model()
    temp = []
    for i, row in enumerate(data):
        temp.append({'ID':row['ID'], 'Query':row['Query'], 'URL':row['URL'], 'Topic': document_topic_list[i],'Date':row['Date'], 'Time':row['Time']})
        print(temp)
    
    save_as_csv(temp, topic_list)
    generate_textfiles(data)
   

    

if __name__ =='__main__':
    main()