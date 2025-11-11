from math import ceil
from dotenv import load_dotenv

from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter, util as util_limiter
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sentence_transformers import SentenceTransformer, util
import worldnewsapi
from worldnewsapi.rest import ApiException
import random

from transformers import pipeline

from nltk.tokenize import sent_tokenize

import torch.nn.functional as F

import os

load_dotenv()

nli_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
nli_model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")




configuration = worldnewsapi.Configuration(
        host = "https://api.worldnewsapi.com"
)

configuration.api_key['headerApiKey'] = os.getenv("NEWS_KEY")

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

model_similarity = SentenceTransformer('all-mpnet-base-v2')



bert_tokenizer = AutoTokenizer.from_pretrained(
    "v0lt/News_Reliability_BERT_fine_tuned",
)
bert_model = AutoModelForSequenceClassification.from_pretrained(
    "v0lt/News_Reliability_BERT_fine_tuned",
    
)

max_chunk_length = 2000




id2label = bert_model.config.id2label

app = Flask(__name__, template_folder="./templates", static_folder="./static")

CORS(app)

limiter = Limiter(
   util_limiter.get_remote_address, 
   app = app    

)


def get_bert_prediction(text):
    inputs = bert_tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    with torch.no_grad():
        outputs = bert_model(**inputs)
        predictions = outputs.logits
        probabilities = torch.softmax(predictions, dim=1)
      

    return ceil(probabilities[0][1].item() * 100)

from transformers import AutoTokenizer


summarizer_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")


def summarize(text, max_length = 2048, for_fetch_news = False):
        if len(text) > max_length:
            
           
            sentences = sent_tokenize(text)
            chunks = []
            current_chunk = ""

            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= max_chunk_length:
                    current_chunk += " " + sentence
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
            if current_chunk:
                chunks.append(current_chunk.strip())
                


           
            all_summaries = []

            length = int(2048 / len(chunks))

            for i, chunk in enumerate(chunks):
                if len(chunk) > length:
                    summary = summarizer(chunk, max_length=int(length/4), min_length = int((length*0.9)/4),  do_sample=False)
                    
                else:
                    summary = summarizer(chunk, max_length=int((length*0.9)/4), min_length = int((length*0.8)/4),  do_sample=False)
                all_summaries.append(summary[0]['summary_text'])
                   

                

            
            text = "\n".join(all_summaries)
            
        if for_fetch_news and len(text)>20*4:
            summary_text = summarizer(text, max_length=20, min_length=10, do_sample=False, num_beams=5)[0]['summary_text']
            if len(summary_text)>100:
                
                summary_text = summary_text[:101]
                position = int(summary_text.rfind(" "))
                summary_text = summary_text[:position]

        elif len(text)>25*4:

            summary_text = summary_text = summarizer(text, max_length=int((len(text) * 0.8)/4), min_length=int((len(text) * 0.7)/4), do_sample=False, num_beams=5)[0]['summary_text']
        else:
            summary_text = text
          
        return summary_text




def fetch_news(text):


    final_summary = summarize(text, max_length=4096, for_fetch_news=True)


    with worldnewsapi.ApiClient(configuration) as api_client:

        api_instance = worldnewsapi.NewsApi(api_client)
 
        try:
        
            api_response = api_instance.search_news(final_summary, number=1, language = 'en')
        


            return api_response.news[0].text + "\n" + api_response.news[0].title
        except ApiException as e:
            print("Exception when calling NewsApi->extract_news: %s\n" % e)

def calculate_nli_similarity(text):

   inputs = nli_tokenizer(text[0], text[1], return_tensors="pt", truncation=True)
   outputs = nli_model(**inputs)
   probs = F.softmax(outputs.logits, dim=1)

   labels = ['contradiction', 'neutral', 'entailment']
   probs = dict(zip(labels, probs[0].tolist()))

   return probs
   
def calculate_semantic_similarity(text):
 
    embedding1 = model_similarity.encode(text[0], convert_to_tensor=True)
    embedding2 = model_similarity.encode(text[1], convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(embedding1, embedding2)
    return int(similarity_score.item() * 100)



@app.route("/")
def hello_world():
    return render_template("index.html")
    
@app.route("/verifyNews", methods=['POST'])
@limiter.limit("1 per 1 second")
def predict_news():
    if request.is_json:

        data = request.get_json()
        news = data.get('news')
        

        try:
            real_news = fetch_news(news)
            news = summarize(news)

            sentences = [real_news, news]
         
            nli_score = calculate_nli_similarity(sentences)
           
            nli_score_contradiction = int(nli_score["contradiction"] * 100)
            nli_score_neutral = int(nli_score["neutral"] * 100)
            similarity_score = calculate_semantic_similarity(sentences)
            if similarity_score<0:
                similarity_score = 0
         
            if nli_score_neutral >=95:
                reliability_score = int((similarity_score + get_bert_prediction(news)) /2)
            else:

                if similarity_score - nli_score_contradiction > 0:
                    reliability_score = similarity_score - nli_score_contradiction
                
                else:
                    reliability_score = random.randint(1, 5)
                
            
            
        except IndexError:
            reliability_score = get_bert_prediction(news)
            if reliability_score - 15>=0:
                reliability_score = reliability_score - 15
        
   
        return jsonify({"prediction": reliability_score})
            
      
