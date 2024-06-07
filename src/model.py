from mlx_lm import load, generate
import ollama

class Model:
    """A class to represent an MLX language model."""
    def __init__(self, model_name: str):
        self.model, self.tokenizer = load(model_name, tokenizer_config={"eos_token": "<|im_end|>"})

    def generate(
            self,  
            messages: list[dict],
            verbose: bool, 
            top_p: float = 0.8, 
            temp: float = 0.7, 
            repetition_penalty: float = 1.05, 
            max_tokens: int = 64
        ):
        # Check if the messages are empty
        if not messages:
            raise ValueError("Messages cannot be empty.")
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        return generate(self.model, self.tokenizer, prompt=text, verbose=verbose, top_p=top_p, temp=temp, repetition_penalty=repetition_penalty, max_tokens=max_tokens)
    
class OllamaModel:
    """A class to represent an Ollama language model."""
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, messages: list[dict], max_tokens: int = 32):
        return ollama.chat(
            model=self.model_name,
            messages=messages,
            options= {"num_predict": max_tokens}
        )["message"]["content"]