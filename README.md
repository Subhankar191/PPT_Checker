# 🔍 PowerPoint Consistency Analyzer

An AI-powered tool that automatically detects inconsistencies in PowerPoint presentations, including **conflicting data**, **contradictory claims** and **timeline mismatches**.

Built using **Python**

---

## 🖼️ Screenshots

### 📋 Inconsistencies
![Result](./screenshot/Screenshot_1.png)


## ✨ Features

- **Multi-Slide Analysis**: Detects conflicts across entire presentations
- **Smart Checks**:
  - Conflicting numerical data (revenue, percentages)
  - Contradictory textual claims
  - Timeline mismatches
  - Logical inconsistencies
- **Multi-Modal Processing**: Analyzes both text and images (OCR)
- **AI-Powered**: Uses Gemini AI for nuanced contradiction detection

## ⚠️ Limitations

### OCR Accuracy
- Text extraction from images depends on image quality  
- Complex layouts (multi-column, stylized text) reduce OCR accuracy  
- Handwritten text is not supported

### Context Understanding
- Some contextual nuances may be missed  
- Requires clear contradictions to be detectable  
- Metaphors or sarcasm may be misinterpreted

### Performance
- Large presentations (>50 slides) may take longer to process  
- Image-heavy decks will be slower due to OCR requirements  
- Real-time analysis not supported for very large files

### Format Support
- Currently only supports PPTX format (no PPT/ODP)  
- Some complex slide layouts may not be fully parsed  
- Embedded Excel charts require manual verification

### AI Analysis
- Gemini API rate limits may affect large batch processing  
- Non-English content has reduced accuracy  
- Industry-specific jargon may require custom prompts

## 🚀 Quick Start

### Prerequisites
- VS Code
- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Google API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation
```bash
git clone https://github.com/Subhankar191/PPT_Checker.git
cd PPT_Checker

Install all the dependencies from "requirements.txt".

Finally run the below command in terminal
python analyzer.py NoogatAssignment.pptx --verbose 
