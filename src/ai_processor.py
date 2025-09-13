"""
AI-Powered Document Intelligence for Doc2LaTeX
Uses OpenAI GPT-4 for document analysis and intelligent formatting
"""

import os
import json
import re
from typing import Dict, List, Tuple, Optional
from openai import OpenAI
from dataclasses import dataclass
from enum import Enum

class DocumentType(Enum):
    OFFICE_MEMORANDUM = "office_memorandum"
    CIRCULAR = "circular"
    NOTIFICATION = "notification"
    RESEARCH_PAPER = "research_paper"
    REPORT = "report"
    LETTER = "letter"
    POLICY_DOCUMENT = "policy_document"
    TENDER_DOCUMENT = "tender_document"
    ACADEMIC_PAPER = "academic_paper"
    LEGAL_DOCUMENT = "legal_document"
    FINANCIAL_REPORT = "financial_report"
    UNKNOWN = "unknown"

@dataclass
class DocumentAnalysis:
    document_type: DocumentType
    title: str
    author: str
    department: str
    classification: str
    summary: str
    key_sections: List[str]
    formatting_requirements: Dict[str, str]
    suggested_template: str
    confidence_score: float

class AIDocumentProcessor:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI Document Processor with OpenAI API"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Model selection for different tasks
        self.classification_model = "gpt-4o"  # Latest GPT-4o for classification
        self.conversion_model = "gpt-4"       # GPT-4 for complex conversions only
        
        # Indian Government Document Standards
        self.indian_standards = {
            "fonts": {
                "primary": "Devanagari",
                "secondary": "Times New Roman",
                "monospace": "Courier New"
            },
            "page_setup": {
                "size": "A4",
                "margins": {"top": "2.5cm", "bottom": "2.5cm", "left": "3cm", "right": "2.5cm"},
                "line_spacing": "1.5"
            },
            "colors": {
                "government": "#FF6600",  # Saffron
                "accent": "#000080",      # Navy Blue
                "text": "#000000"
            }
        }

    def analyze_document(self, text: str) -> DocumentAnalysis:
        """Analyze document using GPT-4 to determine type and formatting requirements"""
        
        analysis_prompt = f"""
        Analyze the following document text and provide a comprehensive analysis in JSON format.
        The document should be classified according to Indian government and institutional standards.

        Document Text:
        {text[:2000]}...

        Please provide analysis in this exact JSON format:
        {{
            "document_type": "one of: office_memorandum, circular, notification, research_paper, report, letter, policy_document, tender_document, academic_paper, legal_document, financial_report, unknown",
            "title": "extracted or inferred document title",
            "author": "extracted author/department name",
            "department": "government department or institution",
            "classification": "classification level (Public, Restricted, Confidential, Secret)",
            "summary": "brief summary of document content",
            "key_sections": ["list", "of", "main", "sections"],
            "formatting_requirements": {{
                "header_style": "formal/semi-formal/academic",
                "numbering_style": "indian_government/academic/legal",
                "reference_style": "government/academic/legal",
                "language_style": "formal_hindi_english/formal_english/technical"
            }},
            "suggested_template": "indian_government/academic_formal/legal_standard/corporate_report",
            "confidence_score": 0.95
        }}

        Consider Indian government document formatting standards and hierarchy.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.classification_model,  # Use GPT-4o for classification
                messages=[
                    {"role": "system", "content": "You are an expert in Indian government document formatting and classification. Analyze documents according to Government of India standards and best practices. Focus on accurate document type detection and metadata extraction."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse the JSON response
            analysis_text = response.choices[0].message.content
            
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                
                return DocumentAnalysis(
                    document_type=DocumentType(analysis_data.get('document_type', 'unknown')),
                    title=analysis_data.get('title', 'Document'),
                    author=analysis_data.get('author', 'Unknown'),
                    department=analysis_data.get('department', 'Unknown Department'),
                    classification=analysis_data.get('classification', 'Public'),
                    summary=analysis_data.get('summary', ''),
                    key_sections=analysis_data.get('key_sections', []),
                    formatting_requirements=analysis_data.get('formatting_requirements', {}),
                    suggested_template=analysis_data.get('suggested_template', 'indian_government'),
                    confidence_score=float(analysis_data.get('confidence_score', 0.0))
                )
            else:
                raise ValueError("Could not extract JSON from GPT response")
                
        except Exception as e:
            print(f"Error in document analysis: {e}")
            # Return default analysis
            return DocumentAnalysis(
                document_type=DocumentType.UNKNOWN,
                title="Document",
                author="Unknown",
                department="Unknown Department",
                classification="Public",
                summary="Document analysis failed",
                key_sections=[],
                formatting_requirements={},
                suggested_template="indian_government",
                confidence_score=0.0
            )

    def convert_with_hybrid_approach(self, text: str, analysis: DocumentAnalysis) -> str:
        """
        Hybrid conversion approach:
        1. Try code-based conversion first (fast, cost-effective)
        2. Fall back to GPT-4 for complex cases only
        """
        
        # Step 1: Try code-based conversion for common document types
        code_converted = self._code_based_conversion(text, analysis)
        
        # Step 2: Check if code-based conversion is sufficient
        if self._is_conversion_adequate(code_converted, analysis):
            print("✅ Using code-based conversion (fast & efficient)")
            return code_converted
        
        # Step 3: Fall back to GPT-4 for complex cases
        print("🤖 Using GPT-4 for complex document conversion")
        return self._gpt4_enhancement(code_converted, analysis)

    def _code_based_conversion(self, text: str, analysis: DocumentAnalysis) -> str:
        """Code-based rule-driven document conversion"""
        
        # Basic document structure improvements
        converted_text = text
        
        # Rule 1: Add proper document headers based on type
        if analysis.document_type == DocumentType.OFFICE_MEMORANDUM:
            converted_text = self._add_memo_structure(converted_text, analysis)
        elif analysis.document_type == DocumentType.CIRCULAR:
            converted_text = self._add_circular_structure(converted_text, analysis)
        elif analysis.document_type == DocumentType.NOTIFICATION:
            converted_text = self._add_notification_structure(converted_text, analysis)
        elif analysis.document_type == DocumentType.REPORT:
            converted_text = self._add_report_structure(converted_text, analysis)
        
        # Rule 2: Standardize section headings
        converted_text = self._standardize_headings(converted_text)
        
        # Rule 3: Add proper numbering and formatting
        converted_text = self._add_standard_numbering(converted_text)
        
        # Rule 4: Improve paragraph structure
        converted_text = self._improve_paragraphs(converted_text)
        
        return converted_text

    def _add_memo_structure(self, text: str, analysis: DocumentAnalysis) -> str:
        """Add Office Memorandum structure"""
        header = f"""
File No.: {analysis.formatting_requirements.get('file_number', 'No. 1/1/2025-Desk')}
Date: {analysis.formatting_requirements.get('date', 'Date: __________')}

OFFICE MEMORANDUM

Subject: {analysis.title}

        """
        
        footer = f"""


({analysis.author})
{analysis.department}
        """
        
        return header + text + footer

    def _add_circular_structure(self, text: str, analysis: DocumentAnalysis) -> str:
        """Add Circular structure"""
        header = f"""
File No.: {analysis.formatting_requirements.get('file_number', 'No. 1/1/2025-Desk')}
Date: {analysis.formatting_requirements.get('date', 'Date: __________')}

CIRCULAR

Subject: {analysis.title}

        """
        
        return header + text

    def _add_notification_structure(self, text: str, analysis: DocumentAnalysis) -> str:
        """Add Notification structure"""
        header = f"""
NOTIFICATION

File No.: {analysis.formatting_requirements.get('file_number', 'No. 1/1/2025-Desk')}
Date: {analysis.formatting_requirements.get('date', 'Date: __________')}

Subject: {analysis.title}

        """
        
        return header + text

    def _add_report_structure(self, text: str, analysis: DocumentAnalysis) -> str:
        """Add Report structure"""
        header = f"""
REPORT

Title: {analysis.title}
Prepared by: {analysis.author}
Department: {analysis.department}
Classification: {analysis.classification}

EXECUTIVE SUMMARY

        """
        
        return header + text

    def _standardize_headings(self, text: str) -> str:
        """Standardize section headings"""
        # Convert common heading patterns to proper format
        text = re.sub(r'^(\d+\.?\s*[A-Z][^.]*):?\s*$', r'\\section{\1}', text, flags=re.MULTILINE)
        text = re.sub(r'^([A-Z][A-Z\s]+):?\s*$', r'\\section{\1}', text, flags=re.MULTILINE)
        text = re.sub(r'^(\d+\.\d+\.?\s*[A-Z][^.]*):?\s*$', r'\\subsection{\1}', text, flags=re.MULTILINE)
        
        return text

    def _add_standard_numbering(self, text: str) -> str:
        """Add standard Indian government numbering"""
        lines = text.split('\n')
        numbered_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('\\') and len(line) > 50:
                # Add proper paragraph numbering for long content
                if not re.match(r'^\d+\.', line):
                    numbered_lines.append(line)
                else:
                    numbered_lines.append(line)
            else:
                numbered_lines.append(line)
        
        return '\n'.join(numbered_lines)

    def _improve_paragraphs(self, text: str) -> str:
        """Improve paragraph structure"""
        # Add proper spacing between paragraphs
        text = re.sub(r'\n\n+', r'\n\n', text)
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', text)
        
        return text

    def _is_conversion_adequate(self, converted_text: str, analysis: DocumentAnalysis) -> bool:
        """Check if code-based conversion is sufficient"""
        
        # Check for complexity indicators that might need GPT-4
        complexity_indicators = [
            len(converted_text) > 3000,  # Very long documents
            analysis.confidence_score < 0.7,  # Low confidence classification
            analysis.document_type == DocumentType.UNKNOWN,  # Unknown document type
            'complex table' in converted_text.lower(),  # Complex tables
            'mathematical formula' in converted_text.lower(),  # Math formulas
            analysis.document_type in [DocumentType.LEGAL_DOCUMENT, DocumentType.POLICY_DOCUMENT]  # Complex types
        ]
        
        # If any complexity indicator is true, use GPT-4
        return not any(complexity_indicators)

    def _gpt4_enhancement(self, text: str, analysis: DocumentAnalysis) -> str:
        """Use GPT-4 for complex document enhancement"""
        
        enhancement_prompt = f"""
        Enhance and restructure the following document according to Indian government standards and best practices.
        
        Document Type: {analysis.document_type.value}
        Current Title: {analysis.title}
        Department: {analysis.department}
        Classification: {analysis.classification}
        
        Original Text:
        {text}
        
        Please enhance this document by:
        1. Improving the structure and hierarchy
        2. Adding proper Indian government formatting
        3. Ensuring appropriate formal language
        4. Adding necessary sections if missing (like proper headers, file numbers, etc.)
        5. Maintaining the original content meaning while improving presentation
        6. Following Government of India manual of office procedures
        
        Return the enhanced text in a structured format suitable for LaTeX conversion.
        Include proper section headings, numbering, and formal language.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.conversion_model,  # Use GPT-4 for complex conversions
                messages=[
                    {"role": "system", "content": "You are an expert in Government of India document formatting, manual of office procedures, and official communication standards. Enhance documents to meet the highest government standards."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in GPT-4 enhancement: {e}")
            return text

    def enhance_content_structure(self, text: str, analysis: DocumentAnalysis) -> str:
        """
        Enhanced method using hybrid approach:
        1. GPT-4o for classification (already done in analyze_document)
        2. Code-based conversion with GPT-4 fallback
        """
        return self.convert_with_hybrid_approach(text, analysis)

    def generate_metadata(self, analysis: DocumentAnalysis) -> Dict[str, str]:
        """Generate comprehensive metadata based on analysis"""
        
        metadata = {
            "title": analysis.title,
            "author": analysis.author,
            "department": analysis.department,
            "classification": analysis.classification,
            "document_type": analysis.document_type.value,
            "template": analysis.suggested_template,
            "date": "\\today",
            "summary": analysis.summary,
            "keywords": ", ".join(analysis.key_sections),
            "language": analysis.formatting_requirements.get("language_style", "formal_english"),
            "confidence": str(analysis.confidence_score)
        }
        
        return metadata

    def suggest_improvements(self, text: str, analysis: DocumentAnalysis) -> List[str]:
        """Suggest improvements for the document"""
        
        suggestions_prompt = f"""
        Review this {analysis.document_type.value} document and suggest specific improvements 
        to meet Indian government standards and best practices:
        
        {text[:1000]}...
        
        Provide 5-7 specific, actionable suggestions for improving this document's:
        - Structure and organization
        - Language and tone
        - Compliance with government standards
        - Professional presentation
        - Technical accuracy
        
        Return as a numbered list.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.classification_model,  # Use GPT-4o for analysis and suggestions
                messages=[
                    {"role": "system", "content": "You are a senior government document reviewer with expertise in Indian administrative standards and modern document optimization techniques."},
                    {"role": "user", "content": suggestions_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            suggestions_text = response.choices[0].message.content
            # Extract numbered suggestions
            suggestions = re.findall(r'\d+\.\s*(.+)', suggestions_text)
            return suggestions
            
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return ["Document analysis completed. Manual review recommended."]