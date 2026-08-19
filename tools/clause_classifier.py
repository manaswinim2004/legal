import json
from pathlib import Path

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


class ClauseClassifier:
    """
    Legal-BERT clause classifier.

    Returns:
        label
        confidence
        status

    status:
        classified -> sufficiently confident
        uncertain  -> needs fallback / further analysis
    """

    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.50,
    ):
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(self.model_path)
        )

        self.model.eval()

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model.to(self.device)

        self.id2label = self._load_labels()

    # ---------------------------------------------------------
    # Labels
    # ---------------------------------------------------------

    def _load_labels(self):
        """
        Load ID -> label mapping.
        """

        model_labels = getattr(
            self.model.config,
            "id2label",
            None,
        )

        if model_labels:
            return {
                int(key): value
                for key, value in model_labels.items()
            }

        label_file = self.model_path / "id2label.json"

        if label_file.exists():

            with open(
                label_file,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            return {
                int(key): value
                for key, value in data.items()
            }

        raise FileNotFoundError(
            "Could not find label mapping."
        )

    # ---------------------------------------------------------
    # Single clause
    # ---------------------------------------------------------

    def classify(self, text: str) -> dict:

        text = text.strip()

        if not text:
            return {
                "label": None,
                "confidence": 0.0,
                "status": "uncertain",
            }

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1,
        )

        confidence, predicted_id = torch.max(
            probabilities,
            dim=-1,
        )

        predicted_id = predicted_id.item()
        confidence = confidence.item()

        label = self.id2label.get(
            predicted_id,
            f"UNKNOWN_{predicted_id}",
        )

        confidence = round(
            confidence,
            4,
        )

        if confidence >= self.confidence_threshold:

            return {
                "label": label,
                "confidence": confidence,
                "status": "classified",
            }

        return {
            "label": None,
            "confidence": confidence,
            "status": "uncertain",
            "predicted_label": label,
        }

    # ---------------------------------------------------------
    # Multiple clauses
    # ---------------------------------------------------------

    def classify_clauses(
        self,
        clauses: list[dict],
    ) -> list[dict]:

        results = []

        for clause in clauses:

            result = self.classify(
                clause["text"]
            )

            results.append({
                "title": clause.get(
                    "title",
                    "Clause",
                ),
                "text": clause["text"],
                **result,
            })

        return results