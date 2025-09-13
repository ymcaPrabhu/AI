#!/usr/bin/env python3
"""
Doc2LaTeX Conversion Pipeline
Converts documents (DOCX, PDF, TXT) to LaTeX projects ready for Overleaf
"""

import argparse
import os
import sys
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

# Import document parsers
try:
    import docx
    from pdfminer.high_level import extract_text
    import pytesseract
    from PIL import Image
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

def text_to_latex(text: str, mappings: Dict[str, Any]) -> str:
    """Convert plain text to LaTeX format using mappings"""
    lines = text.split('\n')
    latex_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            latex_content.append('')
            continue
        
        # Simple heuristics for document structure
        if line.isupper() and len(line) > 10:
            # Likely a title or heading
            latex_content.append(f'\\section{{{line.title()}}}')
        elif line.startswith('Subject:'):
            latex_content.append(f'\\subsection{{{line}}}')
        elif line.startswith('No.') or line.startswith('Dated:'):
            latex_content.append(f'\\textbf{{{line}}}')
            latex_content.append('')  # Add space after bold text
        elif '(' in line and line.endswith(')') and len(line) < 50:
            # Likely a signature or designation
            latex_content.append('\\vspace{1em}')
            latex_content.append(f'\\textit{{{line}}}')
        else:
            # Regular paragraph - escape special characters
            escaped_line = line.replace('&', '\\&').replace('%', '\\%').replace('$', '\\$')
            latex_content.append(escaped_line)
        
        latex_content.append('')
    
    return '\n'.join(latex_content)

def generate_latex_document(content: str, meta: Dict[str, Any], brand: Dict[str, Any], template: str) -> str:
    """Generate complete LaTeX document with styling"""
    
    # Extract metadata
    title = meta.get('meta', {}).get('title', 'Document')
    subtitle = meta.get('meta', {}).get('subtitle', '')
    author = meta.get('meta', {}).get('author', '')
    date = meta.get('meta', {}).get('date', '')
    
    # Extract branding
    brand_info = brand.get('brand', {})
    primary_color = brand_info.get('primary_color', '#000000')
    font_main = brand_info.get('font_main', 'Latin Modern Roman')
    
    # Fix color definition
    color_hex = primary_color.replace('#', '')
    
    # Create subtitle section
    subtitle_section = ""
    if subtitle:
        subtitle_section = f"\\begin{{center}}\\large\\textit{{{subtitle}}}\\end{{center}}\\vspace{{1em}}"

    latex_doc = f"""\\documentclass[11pt,a4paper]{{article}}

% Packages
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{fancyhdr}}
\\usepackage{{titlesec}}
\\usepackage{{graphicx}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{hyperref}}

% Page setup
\\geometry{{
    top=22mm,
    bottom=22mm,
    left=22mm,
    right=22mm
}}

% Colors
\\definecolor{{primarycolor}}{{HTML}}{{{color_hex}}}

% Title setup
\\title{{{title}}}
\\author{{{author}}}
\\date{{{date}}}

% Header/Footer
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[C]{{\\textbf{{{title}}}}}
\\fancyfoot[C]{{\\thepage}}

\\begin{{document}}

\\maketitle

{subtitle_section}

{content}

\\end{{document}}
"""
    
    return latex_doc

def create_output_structure(output_dir: str):
    """Create Overleaf project directory structure"""
    output_path = Path(output_dir)
    
    # Create main directories
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / 'figures').mkdir(exist_ok=True)
    (output_path / 'bib').mkdir(exist_ok=True)
    (output_path / 'assets').mkdir(exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description='Convert documents to LaTeX for Overleaf')
    parser.add_argument('--in', dest='input_file', required=True, help='Input document file')
    parser.add_argument('--template', default='pro_report', help='LaTeX template to use')
    parser.add_argument('--meta', required=True, help='Document metadata YAML file')
    parser.add_argument('--brand', required=True, help='Brand/styling YAML file')
    parser.add_argument('--out', required=True, help='Output directory for Overleaf project')
    parser.add_argument('--build', action='store_true', help='Build PDF using latexmk')
    
    args = parser.parse_args()
    
    print(f"Converting {args.input_file} to LaTeX project...")
    
    # Load configurations
    meta_config = load_config(args.meta)
    brand_config = load_config(args.brand)
    mappings_config = load_config('config/mappings.yaml')
    
    # Read input document
    try:
        document_text = read_input_file(args.input_file)
        if not document_text.strip():
            print("Warning: No text extracted from input document")
            return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    # Convert to LaTeX
    latex_content = text_to_latex(document_text, mappings_config.get('mappings', {}))
    
    # Generate complete LaTeX document
    full_latex = generate_latex_document(latex_content, meta_config, brand_config, args.template)
    
    # Create output structure
    create_output_structure(args.out)
    
    # Write main LaTeX file
    main_tex_path = Path(args.out) / 'main.tex'
    with open(main_tex_path, 'w', encoding='utf-8') as f:
        f.write(full_latex)
    
    print(f"LaTeX project created at: {args.out}")
    print(f"Main file: {main_tex_path}")
    
    # Build PDF if requested
    if args.build:
        print("Building PDF...")
        pdf_built = False
        
        # Try multiple PDF compilation methods
        compile_methods = [
            {
                'name': 'pdflatex (direct)',
                'commands': [
                    ['pdflatex', '-interaction=nonstopmode', str(main_tex_path)],
                    ['pdflatex', '-interaction=nonstopmode', str(main_tex_path)]  # Run twice for references
                ]
            },
            {
                'name': 'latexmk with pdflatex',
                'commands': [
                    ['latexmk', '-pdf', '-pdflatex=pdflatex', '-cd', str(main_tex_path)]
                ]
            },
            {
                'name': 'latexmk (default)',
                'commands': [
                    ['latexmk', '-pdf', '-cd', str(main_tex_path)]
                ]
            }
        ]
        
        for method in compile_methods:
            if pdf_built:
                break
                
            print(f"Trying {method['name']}...")
            try:
                import subprocess
                success = True
                
                for cmd in method['commands']:
                    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(main_tex_path.parent))
                    
                    if result.returncode != 0:
                        success = False
                        break
                
                if success:
                    pdf_path = main_tex_path.with_suffix('.pdf')
                    if pdf_path.exists():
                        print(f"✓ PDF built successfully with {method['name']}!")
                        print(f"PDF location: {pdf_path}")
                        pdf_built = True
                        break
                    else:
                        print(f"✗ {method['name']} completed but no PDF found")
                else:
                    print(f"✗ {method['name']} failed")
                    if 'latexmk' in method['name'] and 'perl' in result.stderr.lower():
                        print("  → Perl is required for latexmk. Trying direct pdflatex...")
                    
            except FileNotFoundError as e:
                print(f"✗ {method['name']}: Command not found ({e.filename})")
            except Exception as e:
                print(f"✗ {method['name']}: {e}")
        
        if not pdf_built:
            print("\n⚠️  PDF compilation failed with all methods.")
            print("Possible solutions:")
            print("1. Install Perl: https://www.activestate.com/products/perl/")
            print("2. Use MiKTeX Console to install missing packages")
            print("3. Upload the generated LaTeX to Overleaf for online compilation")
            print(f"4. Manual compilation: pdflatex {main_tex_path}")
            print("\nThe LaTeX file is ready and should compile in any LaTeX environment.")

if __name__ == '__main__':
    main()
