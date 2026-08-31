import torch
import spacy
from transformers import AutoModelForSequenceClassification, AutoModel, AutoTokenizer

from dotenv import load_dotenv

load_dotenv()

from .find_news_article import find_news
from .extract_claims import get_claims
from .preprocessing import tokenize_claims, chunk
from .inference import run_inference

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


tokenizer_st = AutoTokenizer.from_pretrained("mixedbread-ai/mxbai-embed-large-v1")
model_st = AutoModel.from_pretrained("mixedbread-ai/mxbai-embed-large-v1").to(device)

tokenizer_nli = AutoTokenizer.from_pretrained("MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
model_nli = AutoModelForSequenceClassification.from_pretrained("MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli").to(device)

max_tokens_st = tokenizer_st.model_max_length

if max_tokens_st>10000:
    max_tokens_st=512

max_tokens_nli = tokenizer_nli.model_max_length

if max_tokens_nli>10000:
    max_tokens_nli=512



spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm", exclude=["tagger", "ner", "lemmatizer", "attribute_ruler"])



def get_score(user_input):

    article = find_news(user_input)
    
    article_tokenized = tokenizer_nli(article, return_offsets_mapping=True)
    article_token_length = len(article_tokenized["input_ids"])

    if article_token_length < max_tokens_nli:

        input_tokenized = tokenizer_nli(user_input)
        input_token_length = len(input_tokenized["input_ids"])


        if article_token_length + input_token_length <= max_tokens_nli:

            score = run_inference(input_tokenized["input_ids"][1:-1], article_tokenized["input_ids"][1:-1], device, run_sentence_transformer=False, tokenized_inputs=True, model_nli=model_nli, tokenizer_nli=tokenizer_nli)

            return score

    doc_input = nlp(user_input)
    sentences_input = [sentence.text.strip() for sentence in doc_input.sents]

    claims_mapped_list = get_claims(sentences_input)
    claims, biggest_token_amount_nli = tokenize_claims(claims_mapped_list, tokenizer_st, max_tokens_st, tokenizer_nli, max_tokens_nli)

    doc_article = nlp(article)
    chunks = chunk(doc_article, tokenizer_st, max_tokens_st, article_tokenized["offset_mapping"][1:-1], max_tokens_nli-biggest_token_amount_nli-2)

    score = run_inference(claims, chunks, device, model_st=model_st, tokenizer_st=tokenizer_st, model_nli=model_nli, tokenizer_nli=tokenizer_nli)

    return score

    

    

    

    