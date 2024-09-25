from transformers import MarianMTModel, MarianTokenizer

# Load the MarianMT model and tokenizer for English-to-Korean translation
model_name = 'Helsinki-NLP/opus-mt-ko-en'  # Ensure this is the correct model name
model = MarianMTModel.from_pretrained(model_name, use_auth_token=True)
tokenizer = MarianTokenizer.from_pretrained(model_name, use_auth_token=True)

# Define the translation function
def translate_en_to_ko(text: str) -> str:
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    
    # Generate translation
    translated_tokens = model.generate(**inputs)
    
    # Decode the translated text
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    
    return translated_text