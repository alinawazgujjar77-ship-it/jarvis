"""Vision system for JARVIS with camera, OCR, and image analysis."""

import os
from typing import Optional, Dict, List
from pathlib import Path
from core.logger import Logger

logger = Logger.get(__name__)

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None


class VisionSystem:
    """Handles camera, OCR, and image analysis."""

    def __init__(self) -> None:
        self.camera = None
        self._init_camera()

    def _init_camera(self) -> None:
        """Initialize camera."""
        if cv2:
            try:
                self.camera = cv2.VideoCapture(0)
                if self.camera.isOpened():
                    logger.info("Camera initialized")
                else:
                    logger.warning("Camera not available")
            except Exception as e:
                logger.warning(f"Camera initialization failed: {e}")

    def take_screenshot(self, save_path: Optional[str] = None) -> Optional[str]:
        """Capture screenshot."""
        if not cv2 or not np:
            logger.warning("OpenCV not available")
            return None

        try:
            from PIL import ImageGrab
            if not save_path:
                Path("data").mkdir(exist_ok=True)
                save_path = f"data/screenshot_{os.urandom(4).hex()}.png"
            
            img = ImageGrab.grab()
            img.save(save_path)
            logger.info(f"Screenshot saved: {save_path}")
            return save_path
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None

    def capture_camera_frame(self, save_path: Optional[str] = None) -> Optional[str]:
        """Capture frame from camera."""
        if not cv2 or not self.camera:
            logger.warning("Camera not available")
            return None

        try:
            ret, frame = self.camera.read()
            if ret:
                if not save_path:
                    Path("data").mkdir(exist_ok=True)
                    save_path = f"data/camera_{os.urandom(4).hex()}.png"
                
                cv2.imwrite(save_path, frame)
                logger.info(f"Camera frame saved: {save_path}")
                return save_path
            else:
                logger.warning("Failed to read camera frame")
                return None
        except Exception as e:
            logger.error(f"Camera capture error: {e}")
            return None

    def ocr_image(self, image_path: str) -> Optional[str]:
        """Extract text from image using OCR."""
        if not pytesseract or not Image:
            logger.warning("Tesseract or PIL not available")
            return None

        try:
            if not os.path.exists(image_path):
                logger.warning(f"Image not found: {image_path}")
                return None

            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            logger.info(f"OCR text extracted from {image_path}")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return None

    def detect_faces(self, image_path: str) -> Optional[List[Dict]]:
        """Detect faces in image."""
        if not cv2:
            logger.warning("OpenCV not available")
            return None

        try:
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            img = cv2.imread(image_path)
            if img is None:
                logger.warning(f"Image not found: {image_path}")
                return None

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            results = []
            for (x, y, w, h) in faces:
                results.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h)
                })

            logger.info(f"Detected {len(results)} face(s)")
            return results
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return None

    def detect_objects(self, image_path: str) -> Optional[List[str]]:
        """Detect objects in image using edge detection."""
        if not cv2 or not np:
            logger.warning("OpenCV not available")
            return None

        try:
            img = cv2.imread(image_path)
            if img is None:
                logger.warning(f"Image not found: {image_path}")
                return None

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            
            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_TREE,
                cv2.CHAIN_APPROX_SIMPLE
            )

            logger.info(f"Detected {len(contours)} objects")
            return [f"Object {i}" for i in range(len(contours))]
        except Exception as e:
            logger.error(f"Object detection error: {e}")
            return None

    def get_image_properties(self, image_path: str) -> Optional[Dict]:
        """Get image properties."""
        if not cv2:
            logger.warning("OpenCV not available")
            return None

        try:
            img = cv2.imread(image_path)
            if img is None:
                logger.warning(f"Image not found: {image_path}")
                return None

            h, w, c = img.shape
            return {
                "width": int(w),
                "height": int(h),
                "channels": int(c),
                "path": image_path
            }
        except Exception as e:
            logger.error(f"Failed to get image properties: {e}")
            return None

    def close(self) -> None:
        """Close camera."""
        if self.camera:
            self.camera.release()
            logger.info("Camera closed")
