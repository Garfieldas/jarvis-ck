from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from django.conf import settings


class AIIntegrationError(Exception):
    """Raised when Jarvis AI integration cannot complete."""


def _jarvis_ai_root() -> Path:
    return Path(settings.BASE_DIR) / "jarvis-ai"


def _ensure_jarvis_ai_import_path() -> None:
    jarvis_root = _jarvis_ai_root()
    if not jarvis_root.exists():
        raise AIIntegrationError(f"jarvis-ai directory not found at: {jarvis_root}")

    jarvis_root_str = str(jarvis_root)
    if jarvis_root_str not in sys.path:
        sys.path.insert(0, jarvis_root_str)


def train_cdk2_model(*, num_epochs: int) -> dict[str, Any]:
    """Run the full training pipeline and return a concise summary."""
    _ensure_jarvis_ai_import_path()

    try:
        from src.config import BEST_MODEL_PATH, DEVICE
        from src.data_fetcher import fetch_cdk2_data
        from src.data_preprocessing import preprocess_data
        from src.dataset import compute_pos_weight, create_data_loaders, create_data_splits
        from src.feature_engineering import smiles_list_to_fingerprints
        from src.model import create_model
        from src.train import train_model
    except Exception as exc:  # pragma: no cover - dependency/runtime guard
        raise AIIntegrationError(
            "Could not import jarvis-ai modules. Install dependencies from "
            "jarvis-ai/requirements.txt in your active virtual environment."
        ) from exc

    raw_df = fetch_cdk2_data()
    processed_df = preprocess_data(raw_df)

    fingerprints, valid_indices = smiles_list_to_fingerprints(
        processed_df["canonical_smiles"].tolist()
    )
    labels = processed_df["active"].values[valid_indices]

    if len(labels) < 10:
        raise AIIntegrationError(
            "Not enough valid molecular rows to train a stable model."
        )

    splits = create_data_splits(fingerprints, labels)
    train_loader, val_loader, _ = create_data_loaders(splits)
    pos_weight = compute_pos_weight(splits["y_train"])

    model = create_model(device=DEVICE)
    history = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        pos_weight=pos_weight,
        num_epochs=num_epochs,
        save_path=BEST_MODEL_PATH,
    )

    return {
        "num_rows": int(len(processed_df)),
        "num_valid_fingerprints": int(len(fingerprints)),
        "num_epochs": int(len(history.get("train_loss", []))),
        "best_val_auc": float(max(history.get("val_auc", [0.0]))),
        "model_path": os.path.relpath(BEST_MODEL_PATH, settings.BASE_DIR),
    }


def predict_smiles(*, smiles: str, threshold: float) -> dict[str, Any]:
    """Load a trained model and predict CDK2 activity for one molecule."""
    _ensure_jarvis_ai_import_path()

    try:
        from src.config import BEST_MODEL_PATH, DEVICE
        from src.predict import load_trained_model, predict_single
    except Exception as exc:  # pragma: no cover - dependency/runtime guard
        raise AIIntegrationError(
            "Could not import jarvis-ai modules. Install dependencies from "
            "jarvis-ai/requirements.txt in your active virtual environment."
        ) from exc

    if not os.path.exists(BEST_MODEL_PATH):
        raise AIIntegrationError(
            "No trained model found yet. Train the model first from the UI."
        )

    model = load_trained_model(BEST_MODEL_PATH, DEVICE)
    result = predict_single(model, smiles=smiles, device=DEVICE, threshold=threshold)

    if result is None:
        raise AIIntegrationError("Invalid SMILES string. Please provide a valid molecule.")

    return result
