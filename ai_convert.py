"""
AI-Enhanced Document Converter with OpenAI GPT-4 Integration
Intelligent document processing for beautiful Indian government standards
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ai_processor import AIDocumentProcessor, DocumentAnalysis
    from template_engine import get_template_by_type
    import docx
    from pdfminer.high_level import extract_text
except ImportError as e:
    print(f"Warning: Optional dependency not available: {e}")

def load_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config {config_path}: {e}")
        return {}

def read_input_file(input_path: str) -> str:
    """Read and extract text from various input formats"""
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Handle different file types
    if input_path.suffix.lower() == '.txt':
        with open(input_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    elif input_path.suffix.lower() == '.docx':
        try:
            doc = docx.Document(input_path)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return ""
    
    elif input_path.suffix.lower() == '.pdf':
        try:
            return extract_text(str(input_path))
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
    
    else:
        # Try reading as text file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""

def ai_enhanced_conversion(input_path: str, output_dir: str, openai_api_key: str, 
                          user_title: str = None, user_author: str = None) -> Dict[str, Any]:
    """
    AI-Enhanced document conversion with intelligent analysis
    """
    
    print("🤖 Starting AI-Enhanced Document Conversion...")
    
    # Step 1: Read input document
    print("📖 Reading input document...")
    document_text = read_input_file(input_path)
    if not document_text.strip():
        raise ValueError("No text could be extracted from the document")
    
    # Step 2: Initialize AI processor
    print("🧠 Initializing AI Document Processor...")
    ai_processor = AIDocumentProcessor(api_key=openai_api_key)
    
    # Step 3: Analyze document with GPT-4
    print("🔍 Analyzing document with GPT-4...")
    analysis = ai_processor.analyze_document(document_text)
    
    print(f"📋 Document Analysis Results:")
    print(f"   Type: {analysis.document_type.value}")
    print(f"   Title: {analysis.title}")
    print(f"   Department: {analysis.department}")
    print(f"   Classification: {analysis.classification}")
    print(f"   Template: {analysis.suggested_template}")
    print(f"   Confidence: {analysis.confidence_score:.2f}")
    
    # Step 4: Enhance content structure
    print("✨ Enhancing content structure with AI...")
    enhanced_content = ai_processor.enhance_content_structure(document_text, analysis)
    
    # Step 5: Generate metadata
    print("📝 Generating document metadata...")
    metadata = ai_processor.generate_metadata(analysis)
    
    # Override with user inputs if provided
    if user_title:
        metadata['title'] = user_title
        analysis.title = user_title
    if user_author:
        metadata['author'] = user_author
        analysis.author = user_author
    
    # Step 6: Generate suggestions
    print("💡 Generating improvement suggestions...")
    suggestions = ai_processor.suggest_improvements(enhanced_content, analysis)
    
    # Step 7: Create beautiful LaTeX document
    print("🎨 Creating beautiful LaTeX document...")
    latex_document = get_template_by_type(
        analysis.suggested_template, 
        metadata, 
        enhanced_content
    )
    
    # Step 8: Create output structure
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / 'figures').mkdir(exist_ok=True)
    (output_path / 'bib').mkdir(exist_ok=True)
    (output_path / 'assets').mkdir(exist_ok=True)
    
    # Step 9: Write files
    print("💾 Writing output files...")
    
    # Main LaTeX file
    main_tex_path = output_path / 'main.tex'
    with open(main_tex_path, 'w', encoding='utf-8') as f:
        f.write(latex_document)
    
    # Analysis report
    analysis_path = output_path / 'ai_analysis.yaml'
    analysis_data = {
        'document_analysis': {
            'type': analysis.document_type.value,
            'title': analysis.title,
            'author': analysis.author,
            'department': analysis.department,
            'classification': analysis.classification,
            'summary': analysis.summary,
            'confidence': analysis.confidence_score,
            'template_used': analysis.suggested_template
        },
        'metadata': metadata,
        'suggestions': suggestions,
        'processing_info': {
            'ai_enhanced': True,
            'original_file': str(input_path),
            'generated_date': str(datetime.datetime.now())
        }
    }
    
    with open(analysis_path, 'w', encoding='utf-8') as f:
        yaml.dump(analysis_data, f, default_flow_style=False, allow_unicode=True)
    
    # Enhanced content file
    content_path = output_path / 'enhanced_content.txt'
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f"✅ AI-Enhanced conversion completed!")
    print(f"📁 Output directory: {output_path}")
    print(f"📄 Main LaTeX file: {main_tex_path}")
    
    return {
        'success': True,
        'output_dir': str(output_path),
        'main_tex': str(main_tex_path),
        'analysis': analysis,
        'metadata': metadata,
        'suggestions': suggestions,
        'enhanced_content': enhanced_content
    }

def main():
    """Main entry point for AI-enhanced conversion"""
    parser = argparse.ArgumentParser(description='AI-Enhanced Doc2LaTeX Converter with GPT-4')
    parser.add_argument('--input', '-i', required=True, help='Input document file')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--title', help='Override document title')
    parser.add_argument('--author', help='Override document author')
    parser.add_argument('--build', action='store_true', help='Build PDF using pdflatex')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OpenAI API key is required!")
        print("   Set OPENAI_API_KEY environment variable or use --api-key argument")
        return 1
    
    try:
        # Run AI-enhanced conversion
        result = ai_enhanced_conversion(
            input_path=args.input,
            output_dir=args.output,
            openai_api_key=api_key,
            user_title=args.title,
            user_author=args.author
        )
        
        print("\n📊 AI Analysis Summary:")
        print(f"Document Type: {result['analysis'].document_type.value}")
        print(f"Confidence Score: {result['analysis'].confidence_score:.2f}")
        print(f"Template Used: {result['analysis'].suggested_template}")
        
        print("\n💡 AI Suggestions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"   {i}. {suggestion}")
        
        # Build PDF if requested
        if args.build:
            print("\n🔨 Building PDF...")
            try:
                import subprocess
                main_tex_path = Path(result['main_tex'])
                
                # Run pdflatex twice for references
                for i in range(2):
                    result_build = subprocess.run([
                        'pdflatex', '-interaction=nonstopmode', str(main_tex_path)
                    ], capture_output=True, text=True, cwd=str(main_tex_path.parent))
                
                pdf_path = main_tex_path.with_suffix('.pdf')
                if pdf_path.exists():
                    print(f"✅ PDF built successfully: {pdf_path}")
                else:
                    print("❌ PDF build failed")
                    
            except Exception as e:
                print(f"❌ PDF build error: {e}")
        
        print(f"\n🎉 Conversion completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    import datetime
    exit(main())