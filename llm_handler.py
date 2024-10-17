import logging
from llama_cpp import Llama
from typing import List, Dict, Any
import time
from collections import defaultdict

class LLMHandler:
    def __init__(self, model_path: str):
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        self.logger.info(f"Initializing LLMHandler with model: {self.model_path}")
        
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=512,  # Further reduced context size
            n_threads=16,  # Reduced to 1 thread
            n_gpu_layers=0,  # CPU-only inference
            low_vram=True,
            seed=42
        )
        self.logger.info("Model loaded successfully")

        self.conversation_history = defaultdict(list)
        self.max_history = 3  # Further reduced to 3
        self.max_history_age = 3600  # 1 hour in seconds

    def format_messages(self, messages: List[Dict[str, str]]) -> str:
        return "".join(f"<|{m['role']}|> {m['content']}<|end|>" for m in messages) + "<|assistant|>"

    def prune_conversation_history(self):
        current_time = time.time()
        for user, history in self.conversation_history.items():
            self.conversation_history[user] = [
                msg for msg in history[-self.max_history*2:]
                if current_time - msg.get('timestamp', 0) < self.max_history_age
            ]

    def generate_response(self, prompt: str, user: str, max_tokens: int = 100):
        self.prune_conversation_history()
        history = self.conversation_history[user]
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Provide concise responses."},
            *history,
            {"role": "user", "content": prompt}
        ]
        
        formatted_prompt = self.format_messages(messages)
        
        try:
            output = self.llm(
                formatted_prompt,
                max_tokens=max_tokens,
                stop=["<|end|>"],
                echo=False,
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                repeat_penalty=1.1
            )
            response = output['choices'][0]['text'].strip()

            history.append({"role": "user", "content": prompt, "timestamp": time.time()})
            history.append({"role": "assistant", "content": response, "timestamp": time.time()})
            self.conversation_history[user] = history[-self.max_history*2:]

            return response
        except Exception as e:
            self.logger.error(f"Error during generation: {str(e)}")
            return "I'm sorry, but I encountered an error while processing your request."

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_path.split('/')[-1],
            "device": "CPU",
            "model_parameters": "3.8B",
        }
