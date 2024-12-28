from transformers import LlamaTokenizer, LlamaForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalQAGenerator:
    def __init__(self, model_path, base_model_path):
        """
        Initializes the medical question answer generator
        
        Args:
            model_path: LoRA model path
            base_model_path: Base model path
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = LlamaTokenizer.from_pretrained(base_model_path)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        # Configure quantization parameters
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        
        # Load base model
        base_model = LlamaForCausalLM.from_pretrained(
            base_model_path,
            quantization_config=bnb_config,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        
        # Load trained LoRA weights
        self.model = PeftModel.from_pretrained(base_model, model_path)
        self.model.eval()

    def generate_answer(self, question, max_length=512):
        """
        Generates an answer to the given question
        
        Args:
            question: Input question
            max_length: Maximum length of the generated answer
            
        Returns:
            Generated answer
        """
        # Construct input
        prompt = f"Question: {question}\nAnswer: "
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate answer
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                num_beams=4,  # Use beam search
                temperature=0.7,  # Control the randomness of the generated text
                top_p=0.9,  # Use nucleus sampling
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        # Decode output
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer.split("Answer: ")[-1].strip()

def main():
    # Load model and tokenizer
    print("Loading model...")
    model_path = "model_new"  # Path to the trained model
    base_model_path = "D:/pythonn/codess/MedicalQAGeneration/models/chinese-llama-7b"
    generator = MedicalQAGenerator(model_path, base_model_path)
    
    # Interactive Q&A
    print("\nModel loaded! Enter 'q' to quit.")
    while True:
        try:
            question = input("\nQuestion: ")
            if question.lower() == 'q':
                break
            
            answer = generator.generate_answer(question)
            print(f"\nAnswer: {answer}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
