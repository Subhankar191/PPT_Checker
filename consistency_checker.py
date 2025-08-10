import re
from datetime import datetime
from collections import defaultdict

class ConsistencyChecker:
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.numeric_pattern = re.compile(r'\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?%?')
        self.date_pattern = re.compile(
            r'(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b)|'
            r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b)|'
            r'(\b\d{4}\b)|'
            r'(\bQ[1-4] \d{4}\b)'
        )
    
    def check_consistency(self, slides_data, threshold=0.7):
        inconsistencies = []
        
        # Extract all data for analysis
        all_texts = []
        for slide in slides_data:
            slide_text = f"Slide {slide['slide_number']}:\n"
            slide_text += slide['text'] + "\n"
            if slide['notes']:
                slide_text += "Notes: " + slide['notes'] + "\n"
            for img_text in slide['images_text']:
                slide_text += "Image text: " + img_text + "\n"
            all_texts.append((slide['slide_number'], slide_text))
        
        # Check numerical consistency
        inconsistencies.extend(self._check_numerical_consistency(slides_data, threshold))
        
        # Check date/timeline consistency
        inconsistencies.extend(self._check_timeline_consistency(slides_data, threshold))
        
        # Use Gemini for textual consistency checks
        inconsistencies.extend(self._check_textual_consistency(all_texts, threshold))
        
        # Remove duplicates and sort by confidence
        inconsistencies = self._deduplicate_inconsistencies(inconsistencies)
        inconsistencies.sort(key=lambda x: x['confidence'], reverse=True)
        
        return inconsistencies
    
    def _check_numerical_consistency(self, slides_data, threshold):
        numeric_data = defaultdict(list)
        
        # Extract all numeric values with context
        for slide in slides_data:
            text = slide['text'] + " " + slide['notes']
            for img_text in slide['images_text']:
                text += " " + img_text
            
            for match in self.numeric_pattern.finditer(text):
                value = match.group()
                context = text[max(0, match.start()-50):match.end()+50].replace("\n", " ")
                numeric_data[value].append({
                    'slide': slide['slide_number'],
                    'context': context
                })
        
        # Check for conflicts
        inconsistencies = []
        for value, occurrences in numeric_data.items():
            if len(occurrences) > 1:
                # Check if the same value appears in different contexts that might be conflicting
                contexts = [occ['context'] for occ in occurrences]
                conflict = self._check_numeric_context_conflict(value, contexts)
                
                if conflict:
                    slides = list({occ['slide'] for occ in occurrences})
                    inconsistencies.append({
                        'type': 'Numerical Conflict',
                        'description': f"Same value {value} appears in potentially conflicting contexts",
                        'slides': slides,
                        'confidence': 85  # Base confidence for numerical conflicts
                    })
        
        return inconsistencies
    
    def _check_numeric_context_conflict(self, value, contexts):
        # Simple check for different units or meanings
        units = set()
        keywords = set()
        
        for context in contexts:
            # Check for different units
            if '%' in value and '%' not in context:
                return True
            if '$' in value and '$' not in context:
                return True
            
            # Check for different keywords
            if 'revenue' in context.lower():
                keywords.add('revenue')
            if 'growth' in context.lower():
                keywords.add('growth')
            if 'cost' in context.lower():
                keywords.add('cost')
        
        return len(keywords) > 1
    
    def _check_timeline_consistency(self, slides_data, threshold):
        date_entries = defaultdict(list)
        
        # Extract all dates with context
        for slide in slides_data:
            text = slide['text'] + " " + slide['notes']
            for img_text in slide['images_text']:
                text += " " + img_text
            
            for match in self.date_pattern.finditer(text):
                date_str = match.group()
                try:
                    date_obj = self._parse_date(date_str)
                    context = text[max(0, match.start()-50):match.end()+50].replace("\n", " ")
                    date_entries[date_str].append({
                        'slide': slide['slide_number'],
                        'date_obj': date_obj,
                        'context': context
                    })
                except ValueError:
                    continue
        
        # Check for timeline conflicts
        inconsistencies = []
        processed_pairs = set()
        
        date_items = list(date_entries.items())
        for i in range(len(date_items)):
            date_str1, occurrences1 = date_items[i]
            for j in range(i+1, len(date_items)):
                date_str2, occurrences2 = date_items[j]
                
                pair_key = frozenset([date_str1, date_str2])
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)
                
                # Compare all occurrences of these two dates
                for occ1 in occurrences1:
                    for occ2 in occurrences2:
                        if occ1['date_obj'] != occ2['date_obj']:
                            # Check if they refer to the same event
                            if self._same_event(occ1['context'], occ2['context']):
                                slides = sorted({occ1['slide'], occ2['slide']})
                                inconsistencies.append({
                                    'type': 'Timeline Issue',
                                    'description': f"Different dates for same event: {date_str1} vs {date_str2}",
                                    'slides': slides,
                                    'confidence': 80  # Base confidence for timeline issues
                                })
        
        return inconsistencies
    
    def _parse_date(self, date_str):
        # Simple date parsing (would need enhancement for production)
        if date_str.startswith('Q'):
            quarter = int(date_str[1])
            year = int(date_str[3:])
            return (year, quarter)
        
        try:
            return datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%b %d, %Y')
                except ValueError:
                    return datetime.strptime(date_str, '%Y')
    
    def _same_event(self, context1, context2):
        # Simple check for same event in contexts
        common_terms = {'launch', 'release', 'event', 'meeting', 'deadline'}
        context1_terms = set(context1.lower().split())
        context2_terms = set(context2.lower().split())
        
        return len(common_terms.intersection(context1_terms, context2_terms)) > 0
    
    def _check_textual_consistency(self, all_texts, threshold):
        inconsistencies = []
        
        # Use Gemini to analyze the entire text for contradictions
        prompt = """Analyze the following slides from a PowerPoint presentation and identify any factual or logical inconsistencies across them. 
Look for:
1. Conflicting numerical data (e.g., different revenue figures)
2. Contradictory textual claims (e.g., "market is competitive" vs "no competition")
3. Timeline mismatches (e.g., conflicting dates)
4. Any other logical inconsistencies

For each inconsistency you find, provide:
- The type of inconsistency
- The slide numbers where it occurs
- A brief description of the inconsistency
- Your confidence level (0-100%)

Slides:\n"""
        
        for slide_num, text in all_texts:
            prompt += f"\n=== Slide {slide_num} ===\n{text}\n"
        
        prompt += "\nPlease list all inconsistencies you found in the following structured format:\n"
        prompt += "Type: [type of inconsistency]\nSlides: [comma-separated slide numbers]\nDescription: [description]\nConfidence: [confidence percentage]"
        
        response = self.gemini_client.generate_content(prompt)
        inconsistencies.extend(self._parse_gemini_response(response))
        
        return inconsistencies
    
    def _parse_gemini_response(self, response):
        inconsistencies = []
        current_item = {}
        
        for line in response.split('\n'):
            if line.startswith('Type:'):
                if current_item:
                    inconsistencies.append(current_item)
                current_item = {
                    'type': line[6:].strip(),
                    'slides': [],
                    'description': '',
                    'confidence': 0
                }
            elif line.startswith('Slides:') and current_item:
                slides = [int(s.strip()) for s in line[7:].split(',')]
                current_item['slides'] = slides
            elif line.startswith('Description:') and current_item:
                current_item['description'] = line[13:].strip()
            elif line.startswith('Confidence:') and current_item:
                try:
                    current_item['confidence'] = int(line[11:].strip().replace('%', ''))
                except ValueError:
                    current_item['confidence'] = 70  # Default if parsing fails
        
        if current_item:
            inconsistencies.append(current_item)
        
        return inconsistencies
    
    def _deduplicate_inconsistencies(self, inconsistencies):
        unique = []
        seen = set()
        
        for item in inconsistencies:
            key = (item['type'], tuple(sorted(item['slides'])), item['description'][:100])
            if key not in seen:
                seen.add(key)
                unique.append(item)
        
        return unique