import tiktoken

def get_tokenizer(model_name: str):
    try:
        return tiktoken.encoding_for_model(model_name)
    except:
        return tiktoken.get_encoding("cl100k_base")