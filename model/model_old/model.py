from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

def generate_response(prompt):
    tokenizer = GPT2Tokenizer.from_pretrained('C:/Users/Sarb/OneDrive - Lambton College/Term 3/AML-3406 - AI & ML Capstone project/gradeGpt/model')
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    model = GPT2LMHeadModel.from_pretrained('C:/Users/Sarb/OneDrive - Lambton College/Term 3/AML-3406 - AI & ML Capstone project/gradeGpt/model')
    # Create the attention mask and pad token id
    attention_mask = torch.ones_like(input_ids)
    pad_token_id = tokenizer.eos_token_id

    output = model.generate(
        input_ids,
        num_beams=3,
        max_length=250,
        num_return_sequences=1,
        attention_mask=attention_mask,
        pad_token_id=pad_token_id
    )

    return tokenizer.decode(output[0], skip_special_tokens=True)