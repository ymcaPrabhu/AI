"""
AI-Enhanced Flask Web Application for Doc2LaTeX Converter
Provides intelligent web interface with OpenAI GPT-4 integration
"""

from flask import Flask, request, render_template, send_file, flash, redirect, url_for, jsonify
import os
import tempfile
import shutil
from pathlib import Path
import zipfile
from werkzeug.utils import secure_filename
import yaml
import sys
import subprocess
import datetime
import json

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables
load_env_file()

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import AI processing functions
try:
    from ai_processor import AIDocumentProcessor, DocumentAnalysis
    from template_engine import get_template_by_type, INDIAN_GOVERNMENT_TEMPLATES
    import docx
    from pdfminer.high_level import extract_text
    AI_AVAILABLE = True
    print("✅ AI features available")
    print("🚀 Optimization: GPT-4o for classification, Code-based conversion with GPT-4 fallback")
except ImportError as e:
    print(f"⚠️ AI features not available: {e}")
    AI_AVAILABLE = False

# Allow forcing AI off via environment variable
if os.getenv('DISABLE_AI', '0') == '1':
    AI_AVAILABLE = False
    print("⚠️ AI features disabled via DISABLE_AI=1")

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'txt', 'doc', 'docx', 'pdf'}

# Create directories
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def fallback_conversion(content: str, title: str = "Document", author: str = "Author") -> str:
    """Fallback LaTeX conversion when AI is not available"""
    from src.template_engine import escape_latex, clean_content_for_latex
    
    lines = content.split('\n')
    latex_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            latex_content.append('')
            continue
        
        # Simple heuristics
        if line.isupper() and len(line) > 10:
            latex_content.append(f'\\section{{{escape_latex(line.title())}}}')
        elif line.startswith('Subject:'):
            latex_content.append(f'\\subsection{{{escape_latex(line)}}}')
        elif line.startswith('No.') or line.startswith('Dated:'):
            latex_content.append(f'\\textbf{{{escape_latex(line)}}}')
            latex_content.append('')
        else:
            escaped_line = escape_latex(line)
            latex_content.append(escaped_line)
        latex_content.append('')
    
    return get_template_by_type('basic', {
        'title': escape_latex(title),
        'author': escape_latex(author),
        'date': datetime.datetime.now().strftime('%B %d, %Y')
    }, '\n'.join(latex_content))

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index_ai.html', 
                         ai_available=AI_AVAILABLE,
                         templates=INDIAN_GOVERNMENT_TEMPLATES if AI_AVAILABLE else {})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and conversion"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Get form data
            use_ai = request.form.get('use_ai', 'false') == 'true'
            custom_title = request.form.get('title', '').strip()
            custom_author = request.form.get('author', '').strip()
            template_choice = request.form.get('template', 'auto')
            # Always build PDF automatically
            build_pdf = True
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            upload_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(upload_path)
            
            # Read document content
            document_text = read_input_file(upload_path)
            if not document_text.strip():
                flash('Could not extract text from the document', 'error')
                return redirect(url_for('index'))
            
            # Create output directory
            output_dir = os.path.join(OUTPUT_FOLDER, f"project_{timestamp}")
            os.makedirs(output_dir, exist_ok=True)
            
            # Process with AI or fallback
            if use_ai and AI_AVAILABLE:
                result = process_with_ai(document_text, output_dir, custom_title, custom_author, template_choice)
            else:
                result = process_without_ai(document_text, output_dir, custom_title, custom_author)
            
            # Always attempt PDF compilation
            pdf_result = None
            if result['success']:
                print("🔨 Building PDF automatically...")
                pdf_result = build_pdf_document(result['latex_path'])
                if pdf_result['success']:
                    result['pdf_path'] = pdf_result['pdf_path']
                    result['pdf_size'] = pdf_result['pdf_size']
                    result['compilation_output'] = pdf_result['compilation_output']
                    result['pdf_available'] = True
                    flash('Document converted and PDF compiled successfully!', 'success')
                else:
                    # PDF failed but LaTeX succeeded
                    result['pdf_error'] = pdf_result['error']
                    result['compilation_output'] = pdf_result['compilation_output']
                    result['pdf_available'] = False
                    flash('Document converted to LaTeX successfully, but PDF compilation failed. LaTeX source is available for download.', 'warning')
            else:
                result['pdf_available'] = False
            
            # Store result in session or return immediately
            if result['success']:
                flash('Document converted successfully!', 'success')
                return render_template('result_ai.html', 
                                     result=result, 
                                     project_name=f"project_{timestamp}",
                                     ai_used=use_ai and AI_AVAILABLE)
            else:
                flash(f"Conversion failed: {result.get('error', 'Unknown error')}", 'error')
                return redirect(url_for('index'))
                
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload TXT, DOC, DOCX, or PDF files.', 'error')
        return redirect(url_for('index'))

def process_with_ai(document_text: str, output_dir: str, custom_title: str = None, 
                   custom_author: str = None, template_choice: str = 'auto') -> dict:
    """Process document using AI analysis"""
    try:
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {'success': False, 'error': 'OpenAI API key not configured'}
        
        # Initialize AI processor
        ai_processor = AIDocumentProcessor(api_key=api_key)
        
        # Analyze document
        analysis = ai_processor.analyze_document(document_text)
        
        # Enhance content
        enhanced_content = ai_processor.enhance_content_structure(document_text, analysis)
        
        # Generate metadata
        metadata = ai_processor.generate_metadata(analysis)
        
        # Override with user inputs
        if custom_title:
            metadata['title'] = custom_title
            analysis.title = custom_title
        if custom_author:
            metadata['author'] = custom_author
            analysis.author = custom_author
        
        # Select template
        if template_choice == 'auto':
            template_type = analysis.suggested_template
        else:
            template_type = template_choice
        
        # Generate LaTeX document
        latex_document = get_template_by_type(template_type, metadata, enhanced_content)
        
        # Save files
        latex_path = os.path.join(output_dir, 'main.tex')
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write(latex_document)
        
        # Save analysis
        analysis_path = os.path.join(output_dir, 'ai_analysis.json')
        analysis_data = {
            'document_type': analysis.document_type.value,
            'title': analysis.title,
            'author': analysis.author,
            'department': analysis.department,
            'classification': analysis.classification,
            'summary': analysis.summary,
            'confidence': analysis.confidence_score,
            'template_used': template_type,
            'suggestions': ai_processor.suggest_improvements(enhanced_content, analysis)
        }
        
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        # Save enhanced content
        content_path = os.path.join(output_dir, 'enhanced_content.txt')
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        return {
            'success': True,
            'latex_path': latex_path,
            'analysis_path': analysis_path,
            'content_path': content_path,
            'analysis': analysis_data,
            'template_used': template_type,
            'ai_enhanced': True
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_without_ai(document_text: str, output_dir: str, custom_title: str = None, 
                      custom_author: str = None) -> dict:
    """Process document using fallback method"""
    try:
        title = custom_title or "Document"
        author = custom_author or "Author"
        
        # Generate LaTeX using fallback
        latex_document = fallback_conversion(document_text, title, author)
        
        # Save files
        latex_path = os.path.join(output_dir, 'main.tex')
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write(latex_document)
        
        return {
            'success': True,
            'latex_path': latex_path,
            'analysis': None,
            'template_used': 'basic',
            'ai_enhanced': False
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def build_pdf_document(latex_path: str) -> dict:
    """Build PDF from LaTeX file with comprehensive error handling"""
    try:
        latex_path = Path(latex_path)
        output_dir = latex_path.parent
        
        # Change to output directory for compilation
        original_cwd = os.getcwd()
        os.chdir(str(output_dir))
        
        try:
            # Run pdflatex with just the filename (not full path)
            latex_filename = latex_path.name
            
            # First pass
            print(f"🔨 Running pdflatex first pass...")
            result1 = subprocess.run([
                'pdflatex', '-interaction=nonstopmode', '-halt-on-error', latex_filename
            ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
            
            # Second pass for references
            print(f"🔨 Running pdflatex second pass...")
            result2 = subprocess.run([
                'pdflatex', '-interaction=nonstopmode', '-halt-on-error', latex_filename
            ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
            
            # Check if PDF was created
            pdf_filename = latex_filename.replace('.tex', '.pdf')
            pdf_path = output_dir / pdf_filename
            
            if pdf_path.exists():
                # Get PDF file size
                pdf_size = pdf_path.stat().st_size
                print(f"✅ PDF created successfully: {pdf_size} bytes")
                return {
                    'success': True,
                    'pdf_path': str(pdf_path),
                    'pdf_size': pdf_size,
                    'compilation_output': f"Pass 1: {result1.returncode}, Pass 2: {result2.returncode}"
                }
            else:
                # Provide detailed error information
                error_info = f"Pass 1 exit code: {result1.returncode}\n"
                if result1.stderr:
                    error_info += f"Pass 1 stderr: {result1.stderr[:500]}...\n"
                if result1.stdout:
                    error_info += f"Pass 1 stdout: {result1.stdout[-1000:]}\n"
                
                return {
                    'success': False,
                    'error': 'PDF file was not created - likely LaTeX compilation errors',
                    'compilation_output': error_info
                }
                
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'PDF compilation timed out (60 seconds)',
            'compilation_output': 'Compilation process exceeded time limit'
        }
    except FileNotFoundError:
        return {
            'success': False,
            'error': 'pdflatex not found. Please install LaTeX (MiKTeX/TeX Live)',
            'compilation_output': 'LaTeX distribution not installed or not in PATH'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'compilation_output': f'Error during compilation: {str(e)}'
        }

@app.route('/download/<project_name>/<file_type>')
def download_file(project_name, file_type):
    """Download generated files with enhanced error handling"""
    try:
        project_dir = os.path.join(OUTPUT_FOLDER, project_name)
        
        if not os.path.exists(project_dir):
            flash('Project directory not found', 'error')
            return redirect(url_for('index'))
        
        if file_type == 'latex':
            latex_path = os.path.join(project_dir, 'main.tex')
            if os.path.exists(latex_path):
                return send_file(latex_path, as_attachment=True, 
                               download_name=f'{project_name}_source.tex',
                               mimetype='text/plain')
            else:
                flash('LaTeX file not found', 'error')
                return redirect(url_for('index'))
                
        elif file_type == 'pdf':
            pdf_path = os.path.join(project_dir, 'main.pdf')
            if os.path.exists(pdf_path):
                # Get file size for download info
                file_size = os.path.getsize(pdf_path)
                return send_file(pdf_path, as_attachment=True,
                               download_name=f'{project_name}_document.pdf',
                               mimetype='application/pdf')
            else:
                flash('PDF file not found. Try building the PDF first.', 'error')
                return redirect(url_for('index'))
                
        elif file_type == 'analysis':
            analysis_path = os.path.join(project_dir, 'ai_analysis.json')
            if os.path.exists(analysis_path):
                return send_file(analysis_path, as_attachment=True,
                               download_name=f'{project_name}_analysis.json',
                               mimetype='application/json')
            else:
                flash('Analysis file not found', 'error')
                return redirect(url_for('index'))
                
        elif file_type == 'zip':
            # Create comprehensive zip file with all outputs
            zip_path = os.path.join(project_dir, f'{project_name}_complete.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files in project directory
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        if not file.endswith('_complete.zip'):  # Don't include the zip itself
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, project_dir)
                            zipf.write(file_path, arcname)
                
                # Add a README file
                readme_content = f"""# {project_name} - AI-Enhanced LaTeX Conversion
                
Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Files included:
- main.tex: LaTeX source code
- main.pdf: Compiled PDF document (if available)
- ai_analysis.json: AI analysis results (if AI was used)
- enhanced_content.txt: AI-enhanced content (if AI was used)

To compile LaTeX manually:
1. Ensure you have LaTeX installed (TeXLive, MiKTeX, etc.)
2. Run: pdflatex main.tex
3. Run again for proper references: pdflatex main.tex

Generated by AI-Enhanced Doc2LaTeX Converter
"""
                zipf.writestr('README.txt', readme_content)
            
            return send_file(zip_path, as_attachment=True,
                           download_name=f'{project_name}_complete.zip',
                           mimetype='application/zip')
        
        elif file_type == 'compile':
            # On-demand PDF compilation
            latex_path = os.path.join(project_dir, 'main.tex')
            if not os.path.exists(latex_path):
                flash('LaTeX file not found', 'error')
                return redirect(url_for('index'))
            
            # Build PDF
            pdf_result = build_pdf_document(latex_path)
            
            if pdf_result['success']:
                flash('PDF compiled successfully!', 'success')
                return send_file(pdf_result['pdf_path'], as_attachment=True,
                               download_name=f'{project_name}_compiled.pdf',
                               mimetype='application/pdf')
            else:
                flash(f'PDF compilation failed: {pdf_result["error"]}', 'error')
                # Create error log file
                error_log_path = os.path.join(project_dir, 'compilation_error.log')
                with open(error_log_path, 'w', encoding='utf-8') as f:
                    f.write(f"PDF Compilation Error Log\n")
                    f.write(f"Generated: {datetime.datetime.now()}\n")
                    f.write(f"Error: {pdf_result['error']}\n\n")
                    f.write("Compilation Output:\n")
                    f.write(pdf_result.get('compilation_output', 'No output available'))
                
                return send_file(error_log_path, as_attachment=True,
                               download_name=f'{project_name}_error.log',
                               mimetype='text/plain')
        
        else:
            flash('Invalid file type requested', 'error')
            return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/compile_pdf/<project_name>')
def compile_pdf(project_name):
    """Compile LaTeX to PDF on demand"""
    try:
        project_dir = os.path.join(OUTPUT_FOLDER, project_name)
        latex_path = os.path.join(project_dir, 'main.tex')
        
        if not os.path.exists(latex_path):
            return jsonify({'success': False, 'error': 'LaTeX file not found'})
        
        # Build PDF
        pdf_result = build_pdf_document(latex_path)
        
        if pdf_result['success']:
            return jsonify({
                'success': True,
                'pdf_path': pdf_result['pdf_path'],
                'pdf_size': pdf_result['pdf_size'],
                'download_url': f'/download/{project_name}/pdf'
            })
        else:
            return jsonify({
                'success': False,
                'error': pdf_result['error'],
                'compilation_output': pdf_result.get('compilation_output', '')
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for document analysis"""
    if not AI_AVAILABLE:
        return jsonify({'error': 'AI features not available'}), 400
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        ai_processor = AIDocumentProcessor(api_key=api_key)
        analysis = ai_processor.analyze_document(text)
        
        return jsonify({
            'document_type': analysis.document_type.value,
            'title': analysis.title,
            'author': analysis.author,
            'department': analysis.department,
            'classification': analysis.classification,
            'summary': analysis.summary,
            'confidence': analysis.confidence_score,
            'suggested_template': analysis.suggested_template
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_available': AI_AVAILABLE,
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting AI-Enhanced Doc2LaTeX Web Application...")
    print(f"🤖 AI Features: {'Available' if AI_AVAILABLE else 'Not Available'}")
    if AI_AVAILABLE:
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"🔑 OpenAI API Key: {'Configured' if api_key else 'NOT CONFIGURED'}")
        print("⚡ AI Optimization: GPT-4o for classification, Code-first conversion with GPT-4 fallback")
        if not api_key:
            print("⚠️  Set OPENAI_API_KEY environment variable to enable AI features")

    # Stable defaults; configurable via env vars
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '5001'))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    use_reloader = os.getenv('FLASK_USE_RELOADER', '0') == '1'

    print(f"🛠️  Server config → host={host} port={port} debug={debug} reloader={use_reloader}")
    app.run(host=host, port=port, debug=debug, use_reloader=use_reloader)