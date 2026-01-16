# apps/posts/services/nutrition_ocr/preprocess.py
import cv2

def preprocess_soft(img_bgr):
    """
    표 OCR은 이진화 과하게 하면 오타가 늘어납니다.
    '확대 + 샤픈' 정도가 보통 더 안정적입니다.
    """
    img = cv2.resize(img_bgr, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (0, 0), 1.2)
    sharp = cv2.addWeighted(gray, 1.6, blur, -0.6, 0)

    return sharp  # gray
