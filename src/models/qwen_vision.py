import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from PIL import Image
from transformers import (
    Qwen2_5_VLForConditionalGeneration,
    AutoProcessor,
)
from qwen_vl_utils import process_vision_info

from utils import get_available_gpu


class Qwen25Vision:
    def __init__(self):
        self.device = torch.device(get_available_gpu())

        self.model_id = "Qwen/Qwen2.5-VL-7B-Instruct"

        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            self.model_id,
            torch_dtype="auto",
            attn_implementation="flash_attention_2",
        ).to(self.device)

        min_pixels = 256 * 28 * 28
        max_pixels = 1280 * 28 * 28

        self.processor = AutoProcessor.from_pretrained(
            self.model_id, min_pixels=min_pixels, max_pixels=max_pixels
        )
        
        self.terminator_tokens = [
            self.processor.tokenizer.eos_token_id,
            self.processor.tokenizer.convert_tokens_to_ids("``"),
        ]

    def generate(
        self, role: str, prompt: str, image=None, max_new_token=1500, temperature=0.6
    ):
        """
        Generate text based on the prompt and optional image input.
        """
        messages = [
            {"role": "assistant", "content": role},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image if image is not None else None,
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        
        prompt_template = self.processor.apply_chat_template(
            messages, add_generation_prompt=True
        )
        
        image_inputs, video_inputs = process_vision_info(messages)
        
        inputs = self.processor(
            text=[prompt_template],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(self.device)
        
        output = self.model.generate(
            **inputs,
            do_sample=True,
            max_new_tokens=max_new_token,
            eos_token_id=self.terminator_tokens,
            temperature=temperature,
            top_p=0.9,
            pad_token_id=self.processor.tokenizer.eos_token_id,
        )
        
        output_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, output)
        ]
        output_text = self.processor.batch_decode(
            output_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        
        return output_text
    
    def __call__(
        self, role: str, prompt: str, image=None, max_new_token=1500, temperature=0.8
    ):
        return self.generate(role, prompt, image, max_new_token, temperature)
    
    
if __name__ == "__main__":
    llm = Qwen25Vision()

    image = Image.open("hkust.jpg")

    role = "You are a helpful assistant"

    prompt = "What is HKUST? Explain it with short and clear descriptions."

    res = llm(role, prompt, image)

    print(res)

