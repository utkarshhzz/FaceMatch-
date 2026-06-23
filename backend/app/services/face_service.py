"""
Face recognition service — wraps InsightFace.

This is THE brain of the app. Three responsibilities:

  1. DETECT a face in an image (RetinaFace inside InsightFace).
  2. TURN that face into a 512-dim ArcFace EMBEDDING (the "fingerprint").
  3. MATCH an embedding against all stored ones using cosine distance.

Important patterns:
  - Singleton model: InsightFace is heavy to load, so we build it ONCE.
  - The public functions are SYNC (numpy/CPU work). Endpoints call them via
    `await asyncio.to_thread(...)` so the async server stays responsive.
"""
import json
import os
from typing import Optional

import numpy as np
import cv2

from app.core.config import settings


# ---------- Lazy singleton for the InsightFace model ----------
_app = None  # holds the FaceAnalysis instance once built


def _get_app():
    """Build (once) and return the InsightFace FaceAnalysis pipeline.

    `name="buffalo_l"` is the default model pack: RetinaFace (detection) +
    ArcFace (recognition) + landmarks. It auto-downloads ~250MB on first use.
    `ctx_id=-1` means run on CPU (no GPU required).
    `det_size=(320,320)` is the input resolution for detection — a balance of
    speed and accuracy. Raise it for small/far faces.
    """
    global _app
    if _app is not None:
        return _app

    try:
        from insightface.app import FaceAnalysis
    except ImportError as e:
        raise RuntimeError(
            "insightface is not installed. Run: pip install insightface onnxruntime"
        ) from e

    os.makedirs("data/temp", exist_ok=True)   # model cache dir hint
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(320, 320))
    _app = app
    return app


# ---------- Core operations ----------
def detect_face(image_bgr: np.ndarray) -> Optional[dict]:
    """Detect faces; return the LARGEST face's box + its embedding.

    Returns None when no face is found. Picking the largest face handles
    accidental group photos (we assume the closest/biggest one is the subject).
    """
    app = _get_app()
    faces = app.get(image_bgr)
    if not faces:
        return None

    # Biggest face by bounding-box area.
    def area(f):
        x1, y1, x2, y2 = f.bbox
        return max(0, x2 - x1) * max(0, y2 - y1)

    best = max(faces, key=area)
    return {
        "bbox": best.bbox.tolist(),
        "embedding": np.asarray(best.normed_embedding, dtype=np.float32),
        "det_score": float(best.det_score),
    }


def generate_embedding(image_bgr: np.ndarray) -> Optional[np.ndarray]:
    """Decode-level helper: return just the 512-dim embedding (or None)."""
    result = detect_face(image_bgr)
    if result is None:
        return None
    return result["embedding"]


def embedding_to_json(embedding: np.ndarray) -> str:
    """Store a numpy embedding as a JSON string (DB-friendly)."""
    return json.dumps(embedding.astype(float).tolist())


def json_to_embedding(text: str) -> np.ndarray:
    """Reverse of embedding_to_json."""
    return np.asarray(json.loads(text), dtype=np.float32)


# ---------- Matching math ----------
def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine DISTANCE in [0, 2]. 0 = identical direction, 2 = opposite.

    InsightFace embeddings are already L2-normalized (normed_embedding),
    so a·b is already cosine similarity, and distance = 1 - similarity.
    We normalise again defensively in case a stored vector drifted.
    """
    a = a / (np.linalg.norm(a) + 1e-10)
    b = b / (np.linalg.norm(b) + 1e-10)
    sim = float(np.dot(a, b))
    return float(1.0 - sim)


def match_against_all(
    query_embedding: np.ndarray,
    stored: list[tuple[int, str]],
    threshold: float | None = None,
) -> dict:
    """Find the closest stored embedding to `query_embedding`.

    Args:
        query_embedding: 512-dim vector from the incoming photo.
        stored: list of (encoding_id, embedding_json) from the DB.
        threshold: max cosine distance to accept as a match.

    Returns a dict with: best_encoding_id (or None), distance, confidence
    (0..1 = 1 - distance), and matched (bool).
    """
    if threshold is None:
        threshold = settings.MATCHING_THRESHOLD

    if not stored:
        return {"best_encoding_id": None, "distance": 1.0, "confidence": 0.0, "matched": False}

    best_id = None
    best_distance = float("inf")

    for enc_id, emb_json in stored:
        emb = json_to_embedding(emb_json)
        d = cosine_distance(query_embedding, emb)
        if d < best_distance:
            best_distance = d
            best_id = enc_id

    confidence = max(0.0, 1.0 - best_distance)
    matched = best_distance <= threshold
    return {
        "best_encoding_id": best_id,
        "distance": best_distance,
        "confidence": confidence,
        "matched": matched,
    }
