import torch
from PIL import Image
from transformers import AutoProcessor, MllamaForConditionalGeneration

from src.utils import get_available_gpu


class LlamaVision:
    def __init__(self):
        self.device = torch.device(get_available_gpu())

        self.model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"
        self.model = MllamaForConditionalGeneration.from_pretrained(
            self.model_id, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True
        ).to(self.device)
        self.processor = AutoProcessor.from_pretrained(self.model_id)

    def generate(
        self, role: str, prompt: str, image=None, max_new_token=1500, temperature=0.6
    ) -> str:
        """
        Generate text based on the prompt and optional image input.
        """
        messages = [
            {"role": "assistant", "content": role},
            {
                "role": "user",
                "content": [
                    {"type": "image"} if image is not None else None,
                    {"type": "text", "text": prompt},
                ],
            },
        ]

        prompt_template = self.processor.apply_chat_template(
            messages, add_generation_prompt=True
        )

        inputs = self.processor(image, prompt_template, return_tensors="pt").to(
            self.device
        )
        terminators = [
            self.processor.tokenizer.eos_token_id,
            self.processor.tokenizer.convert_tokens_to_ids("``"),
        ]

        output = self.model.generate(
            **inputs,
            do_sample=True,
            max_new_tokens=max_new_token,
            eos_token_id=terminators,
            temperature=temperature,
            top_p=0.9,
            pad_token_id=self.processor.tokenizer.eos_token_id,
        )

        result = self.processor.decode(output[0, len(inputs["input_ids"][0]) : -1])

        return result

    def __call__(
        self, role: str, prompt: str, image=None, max_new_token=1500, temperature=0.8
    ):
        return self.generate(role, prompt, image, max_new_token, temperature)


if __name__ == "__main__":
    llm = LlamaVision()

    image = Image.open("hkust.jpg")

    role = "You are a helpful assistant"

    prompt = "What is HKUST? Explain it with short and clear descriptions."

    res = llm(role, prompt)

    print(res)
