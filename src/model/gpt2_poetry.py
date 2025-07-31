from transformers import GPT2LMHeadModel, GPT2Tokenizer
from pathlib import Path

MODEL_DIR = str(Path(__file__).resolve().parent / "gpt2-poetry")

class GPT2Poetry:
    __instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of GPT2Poetry."""
        if not cls.__instance:
            cls.__instance = super(GPT2Poetry, cls).__new__(cls)
        return cls.__instance

    def __init__(self, model_name=MODEL_DIR):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.eval()
    
    def generate_poem(self, prompt, max_length=50, temperature=0.8, top_k=50, top_p=0.95, repetition_penalty=1.2):
        """
        Generate a poem based on the given prompt.
        Args:
            prompt (str): The initial line of the poem.
            max_length (int): Maximum length of the generated poem.
            temperature (float): Sampling temperature.
            top_k (int): Top-k sampling parameter.
            top_p (float): Top-p (nucleus) sampling parameter.
            repetition_penalty (float): Penalty for repeated tokens.
        Returns:
            str: The generated poem.
        """

        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        input_ids = inputs["input_ids"].to(self.model.device)

        punctuation_list = [
            ".", ",", "!", "?", ";", ":", "\"", "'", "“", "”", "‘", "’", "(", ")", "[", "]", "{", "}", "~", "`", "-", "_", "*", "/", "\\", "|", "<", ">", "=", "+"
        ]
        
        bad_words = [
            self.tokenizer.encode(p, add_special_tokens=False) for p in punctuation_list
        ]
        
        bad_words_ids = [bw for bw in bad_words if len(bw) > 0]

        output_ids = self.model.generate(
            input_ids=input_ids,
            do_sample=True,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            pad_token_id=self.tokenizer.eos_token_id,
            bad_words_ids=bad_words_ids
        )

        generated_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return generated_text

if __name__ == "__main__":
    model = GPT2Poetry()
    prompt = "Em cười như nắng mai"
    poem = model.generate_poem(prompt)
    print(poem)