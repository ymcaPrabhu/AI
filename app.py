from flask import Flask, request, render_template, send_file, flash, redirect, url_for, jsonify
import os
import tempfile
import shutil
from pathlib import Path
import zipfile
from werkzeug.utils import secure_filename
import yaml
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import document processing functions directly
try:
    import docx
    from pdfminer.high_level import extract_text
    import pytesseract
    from PIL import Image
except ImportError as e:
    print(f"Warning: Optional dependency not available: {e}")

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

def text_to_latex(text: str, mappings: dict) -> str:
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

def generate_latex_document(content: str, meta: dict, brand: dict, template: str) -> str:
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

def create_overleaf_zip(source_dir: str, output_zip: str) -> bool:
    """Create a zip file from LaTeX project directory for Overleaf upload"""
    source_path = Path(source_dir)
    output_path = Path(output_zip)
    
    if not source_path.exists():
        print(f"Error: Source directory does not exist: {source_path}")
        return False
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Files to include in Overleaf zip
    include_extensions = {'.tex', '.bib', '.cls', '.sty', '.png', '.jpg', '.jpeg', '.pdf', '.eps'}
    exclude_files = {'main.aux', 'main.log', 'main.out', 'main.toc', 'main.fls', 'main.fdb_latexmk'}
    
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            
            for root, dirs, files in os.walk(source_path):
                # Skip certain directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check if file should be included
                    if (file_path.suffix.lower() in include_extensions or 
                        file_path.name == 'main.tex'):
                        
                        if file_path.name not in exclude_files:
                            # Calculate relative path for zip
                            rel_path = file_path.relative_to(source_path)
                            
                            # Add to zip
                            zipf.write(file_path, rel_path)
                            file_count += 1
            
            print(f"Successfully created Overleaf zip with {file_count} files: {output_path}")
            return True
            
    except Exception as e:
        print(f"Error creating zip file: {e}")
        return False

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure upload folders
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'web_output'
ALLOWED_EXTENSIONS = {'txt', 'docx', 'pdf', 'doc'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_config(config_path):
    """Load YAML configuration file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config {config_path}: {e}")
        return {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get form data
        template = request.form.get('template', 'pro_report')
        title = request.form.get('title', 'Document')
        author = request.form.get('author', 'Author')
        
        try:
            # Process the document
            result = process_document(filepath, template, title, author)
            
            if result['success']:
                return render_template('result.html', 
                                     success=True, 
                                     download_url=result['download_url'],
                                     pdf_url=result.get('pdf_url'),
                                     filename=result['filename'])
            else:
                flash(f'Conversion failed: {result["error"]}')
                return redirect(url_for('index'))
                
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload TXT, DOCX, or PDF files.')
        return redirect(url_for('index'))

def process_document(input_path, template, title, author):
    """Process uploaded document and create LaTeX/PDF output"""
    try:
        # Create temporary output directory
        output_id = os.path.splitext(os.path.basename(input_path))[0]
        output_dir = os.path.join(OUTPUT_FOLDER, output_id)
        
        # Clean up existing output
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
        # Load configurations
        meta_config = load_config('config/docmeta.yaml')
        brand_config = load_config('config/brand.yaml')
        mappings_config = load_config('config/mappings.yaml')
        
        # Override metadata with form data
        if 'meta' not in meta_config:
            meta_config['meta'] = {}
        meta_config['meta']['title'] = title
        meta_config['meta']['author'] = author
        meta_config['meta']['date'] = 'Generated Online'
        
        # Read input document
        document_text = read_input_file(input_path)
        if not document_text.strip():
            return {'success': False, 'error': 'No text could be extracted from the document'}
        
        # Convert to LaTeX
        latex_content = text_to_latex(document_text, mappings_config.get('mappings', {}))
        
        # Generate complete LaTeX document
        full_latex = generate_latex_document(latex_content, meta_config, brand_config, template)
        
        # Create output structure
        create_output_structure(output_dir)
        
        # Write main LaTeX file
        main_tex_path = Path(output_dir) / 'main.tex'
        with open(main_tex_path, 'w', encoding='utf-8') as f:
            f.write(full_latex)
        
        # Try to compile PDF
        pdf_path = None
        try:
            import subprocess
            result = subprocess.run([
                'pdflatex', '-interaction=nonstopmode', str(main_tex_path)
            ], capture_output=True, text=True, cwd=str(main_tex_path.parent))
            
            # Run twice for references
            subprocess.run([
                'pdflatex', '-interaction=nonstopmode', str(main_tex_path)
            ], capture_output=True, text=True, cwd=str(main_tex_path.parent))
            
            pdf_candidate = main_tex_path.with_suffix('.pdf')
            if pdf_candidate.exists():
                pdf_path = f'/download_pdf/{output_id}'
        except:
            pass  # PDF compilation failed, but we still have LaTeX
        
        # Create Overleaf zip
        zip_path = os.path.join(OUTPUT_FOLDER, f'{output_id}.zip')
        create_overleaf_zip(output_dir, zip_path)
        
        return {
            'success': True,
            'download_url': f'/download/{output_id}',
            'pdf_url': pdf_path,
            'filename': f'{output_id}.zip'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/download/<output_id>')
def download_file(output_id):
    """Download the generated Overleaf zip file"""
    zip_path = os.path.join(OUTPUT_FOLDER, f'{output_id}.zip')
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name=f'{output_id}_overleaf.zip')
    else:
        flash('File not found')
        return redirect(url_for('index'))

@app.route('/download_pdf/<output_id>')
def download_pdf(output_id):
    """Download the generated PDF file"""
    pdf_path = os.path.join(OUTPUT_FOLDER, output_id, 'main.pdf')
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name=f'{output_id}.pdf')
    else:
        flash('PDF not found')
        return redirect(url_for('index'))

@app.route('/preview/<output_id>')
def preview_latex(output_id):
    """Preview the generated LaTeX code"""
    tex_path = os.path.join(OUTPUT_FOLDER, output_id, 'main.tex')
    if os.path.exists(tex_path):
        with open(tex_path, 'r', encoding='utf-8') as f:
            latex_content = f.read()
        return render_template('preview.html', latex_content=latex_content, output_id=output_id)
    else:
        flash('LaTeX file not found')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint for deployment"""
    return jsonify({'status': 'healthy', 'service': 'Doc2LaTeX Web'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)