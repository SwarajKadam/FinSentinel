from typing import Dict

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class FinBERTModel:
    """Small wrapper around the FinBERT model from Hugging Face."""

    def __init__(self, model_name: str = "ProsusAI/finbert") -> None:
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()

    def predict(self, text: str) -> Dict:
        # Tokenize the input text so the model can read it.
        encoded_input = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=256,
        )

        # Turn off gradients because we only need inference.
        with torch.no_grad():
            output = self.model(**encoded_input)

        # Convert raw scores into probabilities.
        probabilities_tensor = torch.softmax(output.logits, dim=1)[0]

        label_scores: Dict[str, float] = {}
        for index, score in enumerate(probabilities_tensor):
            label_name = self.model.config.id2label.get(index, str(index)).lower()
            label_scores[label_name] = round(float(score.item()), 4)

        predicted_label = max(label_scores, key=label_scores.get)

        return {
            "label": predicted_label,
            "confidence": label_scores[predicted_label],
            "probabilities": label_scores,
        }
