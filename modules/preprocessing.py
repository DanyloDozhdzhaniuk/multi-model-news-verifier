def get_token_index(index, offsets, start_offset_index):

    if index > offsets[-1][1]:

        return len(offsets) - 1

    for i, token_index_range in enumerate(offsets[start_offset_index:]):
        if token_index_range[0] <= index <= token_index_range[1]:
            token_index = i + start_offset_index
            return token_index

        

def tokenize_claims(mapped_list, tokenizer_st, max_tokens_st, tokenizer_nli, max_tokens_nli, query_start="Represent this sentence for searching relevant passages:", max_tokens_coef=1.25):

    if query_start == "Represent this sentence for searching relevant passages: ":
        query_start_length=15
        query_start_length_nli=15
    else:
        query_start_length = len(tokenizer_st(query_start)["input_ids"])
        query_start_length_nli = len(tokenizer_nli(query_start)["input_ids"])


    max_tokens = max_tokens_st - query_start_length
    max_tokens_nli =  (max_tokens_nli // max_tokens_coef) - query_start_length_nli

    if max_tokens <=0 or max_tokens_nli<=0:
        return None

    mapped_list_length = len(mapped_list)

    claims_list = [claim for claim in mapped_list if claim != 0 and len(claim.strip())>0]
    if len(claims_list) <= 0:
        return None

    concatenated_claims = "".join(claims_list)

    offsets = tokenizer_st(concatenated_claims, return_offsets_mapping = True)["offset_mapping"][1:-1]
    offsets_nli = tokenizer_nli(concatenated_claims, return_offsets_mapping = True)["offset_mapping"][1:-1]
    
    sentence_end_index = -1

    start_token_index = 0
    start_token_index_nli = 0

    last_token_length = None
  
    token_length_sum = 0

    biggest_token_amount_nli = 0

    first_in_sequence=False
    first_triplet=False
    skip_claim = False

    claim_snippets = set()    

    for index, claim in enumerate(mapped_list):
        
        if claim != 0 and not skip_claim:

            

            token_length_sum = 0
            token_length_sum_nli=0

            current_claim=[query_start]

            sentence_end_index+=len(mapped_list[index])


            if last_token_length:

                if first_in_sequence:
                    first_triplet = True
                else:
                    first_triplet = False

                first_in_sequence = False

                token_length_sum += last_token_length
                token_length_sum += current_token_length

                token_length_sum_nli += last_token_length_nli
                token_length_sum_nli+=current_token_length_nli

                if token_length_sum>max_tokens or token_length_sum_nli>max_tokens_nli:

                    if current_token_length>max_tokens or current_token_length_nli>max_tokens_nli:
                        last_token_length=False
                        continue

                    first_in_sequence = True

                    token_length_sum -= last_token_length
                    token_length_sum_nli -= last_token_length_nli

                    current_claim.append(claim)

                else:
                    current_claim.extend([mapped_list[index-1], claim])

            else:             

                first_in_sequence = True
             
                end_token_index = get_token_index(sentence_end_index, offsets, start_token_index)
                end_token_index_nli = get_token_index(sentence_end_index, offsets_nli, start_token_index_nli)

                if not end_token_index:
                    continue

                current_token_length = end_token_index - start_token_index
                current_token_length_nli = end_token_index_nli - start_token_index_nli

                if current_token_length>max_tokens or current_token_length_nli>max_tokens_nli:
                    continue

                token_length_sum += current_token_length
                token_length_sum_nli += current_token_length_nli


                current_claim.append(claim)

            

            last_token_length = current_token_length
            last_token_length_nli = current_token_length_nli

            if index+1<mapped_list_length and mapped_list[index+1] != 0:
               
                sentence_end_index += len(mapped_list[index+1])

                start_token_index = end_token_index
                start_token_index_nli = end_token_index_nli

                end_token_index = get_token_index(sentence_end_index, offsets, start_token_index)
                end_token_index_nli = get_token_index(sentence_end_index, offsets_nli, start_token_index_nli)

                current_token_length = end_token_index - start_token_index
                current_token_length_nli = end_token_index_nli - start_token_index_nli

                sentence_end_index -= len(mapped_list[index+1])
                            
                if token_length_sum + current_token_length > max_tokens or token_length_sum_nli + current_token_length_nli > max_tokens_nli:

                    if first_in_sequence: 
                        last_token_length=None

                    elif not first_triplet:
                        continue
                else:

                    if first_in_sequence:
                        continue

                    current_claim.append(mapped_list[index+1])

                    if index + 2 >= len(mapped_list) or mapped_list[index+2]==0:

                        skip_claim = True

                        last_token_length = None


            else:
                last_token_length=False

          
            claim_snippets.add(" ".join(current_claim))

            if token_length_sum_nli>biggest_token_amount_nli:
                biggest_token_amount_nli = token_length_sum_nli

            continue

        skip_claim = False


    claim_snippets = list(claim_snippets)

    return claim_snippets, biggest_token_amount_nli









def find_closest_sent(token_index_range, sentences, doc):


    span = doc.char_span(token_index_range[0], token_index_range[1], alignment_mode="expand")
    sentence = span.sent
    sentence_index = sentences.index(sentence) 
    
                              
                

    return sentence, sentence_index



def find_closest_word(doc, token_index):

    token_end = token_index[1]
    current_token = None

    for token in doc:

        if not token.is_space:

            if token_end - (token.idx + len(token.text)) >= 0:
                current_token = token
            else:
                break
    
    return current_token

def chunk(doc, tokenizer_st, max_tokens_st, offsets_nli, max_tokens_nli):

    chunks = set()

    article = doc.text
    sentences = list(doc.sents)



    max_tokens_st = max_tokens_st - 2

    
    offsets_st = tokenizer_st(article, return_offsets_mapping = True)["offset_mapping"][1:-1]


    if len(offsets_st)<=max_tokens_st and len(offsets_nli)<=max_tokens_nli:
        return [article]

    max_intersection = int(max_tokens_st // 2.5)

    start_index_st = 0
    start_index_nli = 0

    start_sentence_index = 0

 


    
    while True:

        try:


         
            start_index_nli = get_token_index(offsets_st[start_index_st][1], offsets_nli, start_index_nli) 
            

            if start_index_st + max_tokens_st >= len(offsets_st) and start_index_nli + max_tokens_nli >= len(offsets_nli):
                break

            
            
            sample = offsets_st[start_index_st:start_index_st+max_tokens_st]
                    
            
     
        
            
                  
            nli_token_index = get_token_index(sample[-1][1], offsets_nli, start_index_nli)

            if nli_token_index > start_index_nli + max_tokens_nli:

                nli_token_difference = nli_token_index - (start_index_nli + max_tokens_nli)
                nli_to_sentence_index = get_token_index(offsets_nli[nli_token_index-nli_token_difference][1], offsets_st, start_index_st)
                sample = offsets_st[start_index_st:nli_to_sentence_index]

            sentence_range_start = sentences[start_sentence_index].start_char


            decrease = -1
            token_index_range = sample[decrease]

            while token_index_range == (0, 0):
                decrease -= 1
                token_index_range = sample[decrease]
                    
            sentence, sentence_index = find_closest_sent(token_index_range, sentences, doc)
        

            if sentence_index == start_sentence_index:
        
                
                closest_word= find_closest_word(doc, sample[decrease])
                if not closest_word:
                    start_index_st = (start_index_st + max_tokens_st) + decrease
                    chunk = article[sentence_range_start:offsets_st[start_index_st][0]]
                    chunks.add(chunk)

                    continue
                
                    
                word_token_index = get_token_index((closest_word.idx + len(closest_word)), offsets_st, start_index_st)
                

                if word_token_index > start_index_st:
                    start_index_st = word_token_index + 1
                    chunk = article[sentence_range_start:offsets_st[word_token_index][1]]
                    chunks.add(chunk)

                    continue

                else:

                    start_index_st = nli_to_sentence_index - decrease + 1
                    chunk = article[sentence_range_start:offsets_st[start_index_st][1]]
                    chunks.add(chunk)

                    continue
                    

            
            chunk_raw = sentences[start_sentence_index:sentence_index]

            
            sentence_range_end = chunk_raw[-1].end_char


                

            token_index = get_token_index(sentence_range_end, offsets_st, start_index_st)

            chunk = article[sentence_range_start:sentence_range_end]
            chunks.add(chunk)

        
            

        
                
            for difference in range(0, max_intersection+1, max_intersection//4):
                
                intersection = max_intersection - difference

                if intersection <= 0:

                    start_sentence_index += len(chunk_raw)
                    start_index_st = token_index + 1

                

                    break

                

                if token_index - intersection > start_index_st:
                

                    intersection_token_index = token_index - intersection


                    
                    if offsets_st[intersection_token_index] == (0, 0):
                    
                        continue           

                    sentence, sentence_index = find_closest_sent(offsets_st[intersection_token_index], sentences, doc)

                    if sentence_index > start_sentence_index:
                

                        start_sentence_index = sentence_index
                        start_index_st = get_token_index(sentence.start_char, offsets_st, start_index_st)
                    
                        break

                
        except IndexError:
            chunk = article[sample[0][0]:sample[0][1]]

            if len(chunk)>0:
                chunks.add(chunk)
                
   
    chunk = article[offsets_st[start_index_st][0]:]
   
    chunks.add(chunk)

    return list(chunks)