import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


model_name = "MoritzLaurer/deberta-v3-base-zeroshot-v2.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

token_max_length = tokenizer.model_max_length - 15

labels=["is a factual statement", "contains someone's personal opinion", "quotes someone or something"]




hypothesis_template = "This text {}"

def run_zero_shot(sentences):

    inputs_input_ids=[]
    inputs_attention_mask=[]

    acceptable_sentences_indexes=[]

    skip_sentence=False

    for index, sentence in enumerate(sentences):
        skip_sentence=False
        ids = []
        attention_masks=[]

        for label in labels:        

            pair_tokenized = tokenizer(
                sentence, hypothesis_template.format(label), return_tensors="pt"
            )

            if pair_tokenized["input_ids"].shape[1]<=token_max_length:
                ids.append(pair_tokenized["input_ids"].tolist()[0])
                attention_masks.append(pair_tokenized["attention_mask"].tolist()[0])
            else:
                skip_sentence=True
                break

        if skip_sentence:
            continue

        inputs_input_ids.extend(ids)
        inputs_attention_mask.extend(attention_masks)

        acceptable_sentences_indexes.append(index)


    inputs = tokenizer.pad(
        {"input_ids": inputs_input_ids, "attention_mask": inputs_attention_mask},
        padding=True,          
        return_tensors="pt"    
    )

    with torch.no_grad():
        outputs = model(**inputs)




    entailment_logits = outputs.logits[:, 0]

    reshaped_logits = entailment_logits.view(len(acceptable_sentences_indexes), 3)

    probs = torch.softmax(reshaped_logits, dim=-1)

    label_indexes = torch.argmax(probs, dim=-1, keepdim=False).tolist()



    results = {sentence_index: labels[label_index] for sentence_index, label_index in zip(acceptable_sentences_indexes, label_indexes)}

    return results

       


def get_claims(sentences):
    scores = run_zero_shot(sentences)

    mapped_list = [0] * len(sentences)

    for index, label in scores.items():

        if label == "is a factual statement" or label == "quotes someone or something":
            mapped_list[index]=sentences[index]
  
    return mapped_list

