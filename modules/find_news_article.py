import os

import yake
import worldnewsapi

from dotenv import load_dotenv

load_dotenv()



kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=10)

configuration = worldnewsapi.Configuration(
        host = "https://api.worldnewsapi.com"
)


API_KEY = os.environ["WORLD_NEWS_API_KEY"]
configuration.api_key['headerApiKey'] = API_KEY


def extract_keyword(text):

    keywords_list = kw_extractor.extract_keywords(text)

    
    result = ""
  
    for keyword, score in keywords_list:

        if len(result) + len(keyword) >= 100:
            break

        result += keyword+" "

    return result.strip()
        

def get_article(query):

    with worldnewsapi.ApiClient(configuration) as api_client:

        api_instance = worldnewsapi.NewsApi(api_client)
  
     
      
        api_response = api_instance.search_news(text=query, language="en", number=1)
        

        if len(api_response.news)<=0:

           raise Exception("Could Not Verify the Text")


        article = f"{api_response.news[0].title}\n{api_response.news[0].text}"

        return article
            


def find_news(text):

    keywords = extract_keyword(text)

    if len(keywords.split()) <= 1:

        raise Exception("Provide a Complete Text")
    
    
    article = get_article(keywords)

    return article