import torch
from transformers import MllamaForConditionalGeneration, AutoProcessor

from utils import get_available_gpu_idx

available_gpu_index = get_available_gpu_idx()
if available_gpu_index is None:
    raise RuntimeError("No available GPU found")

available_cuda = f"cuda:{available_gpu_index}"

class LlamaVision:
    def __init__(self):
        self.device = torch.device(available_cuda if torch.cuda.is_available() else "cpu")
        self.model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"
        self.model = MllamaForConditionalGeneration.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True
        ).to(self.device)
        self.processor = AutoProcessor.from_pretrained(self.model_id)
    
    def generate(self, prompt: str, image=None, max_new_token=1500) -> str:
        prompt_template = "<|begin_of_text|>{}".format(prompt)
        
        if image is not None:
            prompt_template  = "<|image|>" + prompt_template
         
        inputs = self.processor(image, prompt_template, return_tensors="pt").to(self.device)

        output = self.model.generate(**inputs, do_sample=True, max_new_tokens=max_new_token, temperature=0.8, top_p=0.9)
        
        result = self.processor.decode(output[0])[len(prompt_template) : ]
        
        return result

    def __call__(self, prompt: str, image=None, max_new_token=1500):
        return self.generate(prompt, image, max_new_token)

if __name__ == "__main__":
    llm = LlamaVision()
    
    res = llm("What is HKUST? Explain it with short and clear descriptions.")
    
    print(res)