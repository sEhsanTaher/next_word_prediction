# %%
import torch
import string

# from transformers import BertTokenizer, BertForMaskedLM
# bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# bert_model = BertForMaskedLM.from_pretrained('bert-base-uncased').eval()


# bert_tokenizer_mlm_uncased = BertTokenizer.from_pretrained('bert-base-multilingual-uncased')
# bert_model_mlm_uncased = BertForMaskedLM.from_pretrained('bert-base-multilingual-uncased').eval()

# bert_tokenizer_mlm_cased = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
# bert_model_mlm_cased = BertForMaskedLM.from_pretrained('bert-base-multilingual-cased').eval()



# from transformers import XLNetTokenizer, XLNetLMHeadModel
# xlnet_tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased')
# xlnet_model = XLNetLMHeadModel.from_pretrained('xlnet-base-cased').eval()

# from transformers import XLMRobertaTokenizer, XLMRobertaForMaskedLM
# xlmroberta_tokenizer = XLMRobertaTokenizer.from_pretrained('xlm-roberta-base')
# xlmroberta_model = XLMRobertaForMaskedLM.from_pretrained('xlm-roberta-base').eval()

# xlmroberta_tokenizer_large = XLMRobertaTokenizer.from_pretrained('xlm-roberta-large')
# xlmroberta_model_large = XLMRobertaForMaskedLM.from_pretrained('xlm-roberta-large').eval()


# from transformers import BartTokenizer, BartForConditionalGeneration
# bart_tokenizer = BartTokenizer.from_pretrained('bart-large')
# bart_model = BartForConditionalGeneration.from_pretrained('bart-large').eval()

# from transformers import ElectraTokenizer, ElectraForMaskedLM
# electra_tokenizer = ElectraTokenizer.from_pretrained('google/electra-small-generator')
# electra_model = ElectraForMaskedLM.from_pretrained('google/electra-small-generator').eval()

# from transformers import RobertaTokenizer, RobertaForMaskedLM
# roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
# roberta_model = RobertaForMaskedLM.from_pretrained('roberta-base').eval()

top_k = 10


def decode(tokenizer, pred_idx, top_clean):
    ignore_tokens = string.punctuation + '[PAD]'
    tokens = []
    for w in pred_idx:
        token = ''.join(tokenizer.decode(w).split())
        if token not in ignore_tokens:
            tokens.append(token.replace('##', ''))
    return '\n'.join(tokens[:top_clean])


def encode(tokenizer, text_sentence, add_special_tokens=True):
    text_sentence = text_sentence.replace('<mask>', tokenizer.mask_token)
    # if <mask> is the last token, append a "." so that models dont predict punctuation.
    if tokenizer.mask_token == text_sentence.split()[-1]:
        text_sentence += ' .'

    input_ids = torch.tensor([tokenizer.encode(text_sentence, add_special_tokens=add_special_tokens)])
    mask_idx = torch.where(input_ids == tokenizer.mask_token_id)[1].tolist()[0]
    return input_ids, mask_idx


def get_all_predictions(text_sentence, top_clean=5):
    # ========================= BERT =================================
    print(text_sentence)
    try:
        input_ids, mask_idx = encode(bert_tokenizer, text_sentence)
        with torch.no_grad():
            predict = bert_model(input_ids)[0]
        bert = decode(bert_tokenizer, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
    except:
      bert = ""  
    #### BERT MLM uncased:
    try:
        input_ids, mask_idx = encode(bert_tokenizer_mlm_uncased, text_sentence)
        with torch.no_grad():
            predict = bert_model_mlm_uncased(input_ids)[0]
        bert_mlm_uncased = decode(bert_tokenizer_mlm_uncased, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
    except:
        bert_mlm_uncased = ""
    #### BERT MLM cased:
    try:
        input_ids, mask_idx = encode(bert_tokenizer_mlm_cased, text_sentence)
        with torch.no_grad():
            predict = bert_model_mlm_cased(input_ids)[0]
        bert_mlm_cased = decode(bert_tokenizer_mlm_cased, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
    except:
        bert_mlm_cased = ""
    # ========================= XLNET LARGE =================================
    try:
        input_ids, mask_idx = encode(xlnet_tokenizer, text_sentence, False)
        perm_mask = torch.zeros((1, input_ids.shape[1], input_ids.shape[1]), dtype=torch.float)
        perm_mask[:, :, mask_idx] = 1.0  # Previous tokens don't see last token
        target_mapping = torch.zeros((1, 1, input_ids.shape[1]), dtype=torch.float)  # Shape [1, 1, seq_length] => let's predict one token
        target_mapping[0, 0, mask_idx] = 1.0  # Our first (and only) prediction will be the last token of the sequence (the masked token)

        with torch.no_grad():
            predict = xlnet_model(input_ids, perm_mask=perm_mask, target_mapping=target_mapping)[0]
        xlnet = decode(xlnet_tokenizer, predict[0, 0, :].topk(top_k).indices.tolist(), top_clean)
    except:
        xlnet = ""
    # ========================= XLM ROBERTA BASE =================================
    try:
        input_ids, mask_idx = encode(xlmroberta_tokenizer, text_sentence, add_special_tokens=True)
        with torch.no_grad():
            predict = xlmroberta_model(input_ids)[0]
        xlm = decode(xlmroberta_tokenizer, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
    except:
        xlm=""
    # ========================= XLM ROBERTA Large =================================
    try:
        input_ids, mask_idx = encode(xlmroberta_tokenizer_large, text_sentence, add_special_tokens=True)
        with torch.no_grad():
            predict = xlmroberta_model_large(input_ids)[0]
        xlmroberta_large = decode(xlmroberta_tokenizer_large, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
    except:
        xlmroberta_large = ""
    # ========================= BART =================================
    try:
        input_ids, mask_idx = encode(bart_tokenizer, text_sentence, add_special_tokens=True)
        with torch.no_grad():
            predict = bart_model(input_ids)[0]
        bart = decode(bart_tokenizer, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
    except:
        bart = ""
    # ========================= ELECTRA =================================
    try:
        input_ids, mask_idx = encode(electra_tokenizer, text_sentence, add_special_tokens=True)
        with torch.no_grad():
            predict = electra_model(input_ids)[0]
        electra = decode(electra_tokenizer, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
    except:
        electra=""
    # ========================= ROBERTA =================================
    try:
        input_ids, mask_idx = encode(roberta_tokenizer, text_sentence, add_special_tokens=True)
        with torch.no_grad():
            predict = roberta_model(input_ids)[0]
        roberta = decode(roberta_tokenizer, predict[0, mask_idx, :].topk(top_k).indices.tolist(), top_clean)
    except:
        roberta=""
    
    
    return {'bert': bert,
            'bert_mlm_uncased':bert_mlm_uncased,
            'bert_mlm_cased':bert_mlm_cased,
            'xlnet': xlnet,
            'xlm_roberta_base': xlm,
            'xlm_roberta_large' : xlmroberta_large,
            'bart': bart,
            'electra': electra,
            'roberta': roberta}
