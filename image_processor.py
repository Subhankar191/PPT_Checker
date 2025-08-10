from PIL import Image
import pytesseract
import numpy as np

class ImageProcessor:
    def __init__(self):
        # Configure Tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
        pass
    
    def extract_text_from_image(self, image):
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        img_array = np.array(image)
        img_array = self._enhance_contrast(img_array)
        enhanced_img = Image.fromarray(img_array)
        
        # Use Tesseract to extract text
        text = pytesseract.image_to_string(enhanced_img)
        return text
    
    def _enhance_contrast(self, img_array):
        # Simple contrast enhancement
        min_val = np.min(img_array)
        max_val = np.max(img_array)
        
        if max_val - min_val > 0:
            img_array = 255 * (img_array - min_val) / (max_val - min_val)
        
        return img_array.astype(np.uint8)