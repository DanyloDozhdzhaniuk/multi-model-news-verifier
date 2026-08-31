import torch

from sentence_transformers.util import cos_sim


def pooling(outputs, inputs,  strategy='mean') :
    if strategy == 'mean':
        outputs = torch.sum(
                    outputs * inputs["attention_mask"][:, :, None], dim=1) / torch.sum(inputs["attention_mask"], dim=1, keepdim=True)
    elif strategy == 'cls':
        outputs = outputs[:, 0]
    else:
        raise NotImplementedError
    return outputs.detach()


def run_inference(claims, chunks, device, run_sentence_transformer=True, model_st=None, tokenizer_st=None, model_nli=None, tokenizer_nli=None, tokenized_inputs=False):

    def get_max_similarity():

            claims_end_index=len(claims) 

            combined_list = claims+chunks

      
            inputs = tokenizer_st(combined_list, padding=True, return_tensors='pt').to(device)

            with torch.no_grad():
                
                outputs = model_st(**inputs).last_hidden_state

            embeddings = pooling(outputs, inputs)

            

            similarities = cos_sim(embeddings[:claims_end_index], embeddings[claims_end_index:])

            similar_chunks = torch.argmax(similarities, dim=1).cpu().tolist()

            similar_chunks = [chunks[i] for i in similar_chunks]

            return similar_chunks


    def get_nli_score(similar_chunks):

        
        if tokenized_inputs:

            input_ids = tokenizer_nli.build_inputs_with_special_tokens(chunks, claims)

            token_type_ids = tokenizer_nli.create_token_type_ids_from_sequences(chunks, claims)

            attention_mask = [1] * len(input_ids)

           
            inputs = {
                "input_ids": torch.tensor([input_ids]).to(device),
                "token_type_ids": torch.tensor([token_type_ids]).to(device),
                "attention_mask": torch.tensor([attention_mask]).to(device)
            }


        else:
            inputs = tokenizer_nli(similar_chunks, claims, padding=True, return_tensors="pt").to(device)

        with torch.no_grad():

            output = model_nli(**inputs)

        prediction = torch.softmax(output["logits"], -1)    

        score = torch.sum(prediction[:,0], dim=0) / prediction.shape[0]
        score = score.item()

        return score



    
    if run_sentence_transformer:

        similar_chunks = get_max_similarity()

        return get_nli_score(similar_chunks)

    return get_nli_score(chunks)

