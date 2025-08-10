#!/usr/bin/env python3
import argparse
from ppt_processor import PPTProcessor
from consistency_checker import ConsistencyChecker
from gemini_client import GeminiClient
import json
import os
from dotenv import load_dotenv

load_dotenv()

class PowerPointAnalyzer:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.gemini_client = GeminiClient()
        self.consistency_checker = ConsistencyChecker(self.gemini_client)
        
    def analyze(self, pptx_path, output_format='text', verbose=False):
        # Process the PowerPoint file
        processor = PPTProcessor()
        slides_data = processor.process(pptx_path, verbose=verbose)
        
        # Check for inconsistencies
        inconsistencies = self.consistency_checker.check_consistency(slides_data, threshold=self.threshold)
        
        # Generate output
        if output_format == 'json':
            return json.dumps(inconsistencies, indent=2)
        else:
            return self._format_text_output(pptx_path, inconsistencies)
    
    def _format_text_output(self, filename, inconsistencies):
        output = [f"Analyzing presentation: {filename}\n"]
        
        if not inconsistencies:
            output.append("No inconsistencies found.")
            return "\n".join(output)
        
        output.append("=== Inconsistencies Found ===")
        
        for i, issue in enumerate(inconsistencies, 1):
            output.append(f"\n{i}. {issue['type']} (Slides {', '.join(map(str, issue['slides']))})")
            output.append(f"   - {issue['description']}")
            output.append(f"   Confidence: {issue['confidence']}%")
        
        output.append(f"\nAnalysis complete. {len(inconsistencies)} issues found.")
        return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description='PowerPoint Consistency Analyzer')
    parser.add_argument('pptx_path', help='Path to the PowerPoint file')
    parser.add_argument('--output-format', choices=['text', 'json'], default='text',
                       help='Output format (text or json)')
    parser.add_argument('--threshold', type=float, default=0.7,
                       help='Confidence threshold for flagging issues (0.0-1.0)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed processing information')
    args = parser.parse_args()
    
    analyzer = PowerPointAnalyzer(threshold=args.threshold)
    result = analyzer.analyze(args.pptx_path, args.output_format, args.verbose)
    print(result)

if __name__ == "__main__":
    main()