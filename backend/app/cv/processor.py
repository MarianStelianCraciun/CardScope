import cv2
import numpy as np
import pytesseract
from PIL import Image
import io

class CVProcessor:
    def __init__(self):
        # Tesseract configuration could be set here
        pass

    def process_image(self, image_bytes):
        # Convert bytes to opencv image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None
            
        # 1. Card Detection & Perspective Correction
        warped = self._get_card_perspective(img)
        if warped is None:
            warped = img # Fallback to original if warp fails
            
        processed_img = self._preprocess_for_ocr(warped)
        
        # 2. OCR
        text = pytesseract.image_to_string(processed_img)
        
        return {
            "text": text,
            "image": warped
        }

    def _get_card_perspective(self, img):
        # Find card contour and warp
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 75, 200)
        
        cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
        
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            if len(approx) == 4:
                # Warp logic would go here (simplified)
                return self._four_point_transform(img, approx.reshape(4, 2))
        return None

    def _four_point_transform(self, image, pts):
        # Simplified placeholder for perspective transform
        # In a real app, use cv2.getPerspectiveTransform and cv2.warpPerspective
        return image 

    def _preprocess_for_ocr(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Thresholding, noise reduction, etc.
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return thresh

    def extract_card_code(self, img):
        # Failsafe path: Focus on typical card code locations (bottom/corners)
        h, w = img.shape[:2]
        # Heuristic: Card codes are often in the bottom 20%
        bottom_region = img[int(h*0.80):h, 0:w]
        
        gray = cv2.cvtColor(bottom_region, cv2.COLOR_BGR2GRAY)
        # Binarize for better OCR
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        text = pytesseract.image_to_string(thresh, config='--psm 6') # Assume sparse text
        
        return text
