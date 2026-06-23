"""
Image helpers: decode an uploaded file into an OpenCV array + run quality checks.

Concept — why "quality checks" matter for face matching:
  A blurry or very dark photo produces a BAD embedding, so the match score
  is unreliable. We reject obviously-bad images BEFORE wasting time on the
  AI model. Two cheap, classic checks:

  - Blur:   variance of the Laplacian of a grayscale image. Sharp images have
            many rapid intensity changes (high variance); blurry ones are
            smooth (low variance). < 100 usually means "too blurry".
  - Brightness: mean pixel value of the grayscale image. 80-200 is usable;
            outside that, it's too dark or washed-out.

OpenCV (cv2) is THE image library. `imdecode` turns raw bytes into a numpy
array of shape (height, width, 3) in BGR order.
"""
import numpy as np
import cv2


def decode_image(file_bytes: bytes) -> np.ndarray | None:
    """Convert raw image bytes (what an upload/HTTP body contains) into an
    OpenCV BGR image array. Returns None if the bytes aren't a valid image."""
    # np.frombuffer -> raw byte array. cv2.imdecode reads it as an image.
    # 1 = IMREAD_COLOR (force 3-channel BGR).
    arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


def assess_quality(image: np.ndarray) -> dict:
    """Return blur + brightness metrics and whether the image is acceptable."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Laplacian = second derivative; its variance = how "edgy" the image is.
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    brightness = float(gray.mean())

    acceptable = blur_score >= 100.0 and 40.0 <= brightness <= 230.0

    return {
        "blur_score": blur_score,
        "brightness": brightness,
        "acceptable": acceptable,
    }


def is_acceptable_quality(q: dict) -> bool:
    """Convenience wrapper."""
    return bool(q.get("acceptable", False))
