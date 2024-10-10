import torch
from transformers import MllamaForConditionalGeneration, AutoProcessor

class LlamaVision:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"
        self.model = MllamaForConditionalGeneration.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            # device_map="auto",
        ).to(self.device)
        self.processor = AutoProcessor.from_pretrained(self.model_id)
    
    def __call__(self, sys_prompt: str, user_prompt: str, image=None, max_new_token=1500) -> str:
        conversation = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": sys_prompt,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                ],
            },
        ]
         
        prompt = self.processor.apply_chat_template(
            conversation, tokenize=False, add_generation_prompt=True
        )
        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("``"),
        ]
        inputs = self.processor(image, prompt, add_special_tokens=False, return_tensors="pt").to(self.device)
        output = self.model.generate(
            **inputs,
            max_new_tokens=max_new_token,
            do_sample=True,
            eos_token_id=terminators,
            temperature=0.1,
            top_p=0.9,
            pad_token_id=self.processor.tokenizer.eos_token_id,
        )

        result = self.processor.decode(output[0])[
            len(prompt) :
        ]
        
        return result

if __name__ == "__main__":
    llm = LlamaVision()
    
    res = llm("You are a helpful assistant", "What is HKUST")
    
    print(res)