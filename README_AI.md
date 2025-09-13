# AI-Enhanced Doc2LaTeX Converter 🤖📄

> Transform your documents into beautiful LaTeX with the power of OpenAI GPT-4 and Indian Government standards

## 🌟 Features

### 🧠 AI-Powered Intelligence
- **GPT-4 Document Analysis**: Automatic document type detection and classification
- **Smart Content Enhancement**: AI-powered structure optimization and formatting
- **Intelligent Template Selection**: Automatic template matching based on document type
- **Content Suggestions**: AI-generated improvement recommendations

### 🇮🇳 Indian Government Standards
- **Manual of Office Procedures Compliance**: Follows GoI formatting guidelines
- **Professional Templates**: Government, Academic, Legal, and Corporate formats
- **Authentic Color Schemes**: Saffron and Navy blue government branding
- **Proper Typography**: Official letterhead and formatting standards

### 🎨 Beautiful Output
- **LaTeX Excellence**: Professional typesetting with beautiful fonts
- **PDF Generation**: Automatic compilation to high-quality PDFs
- **Multiple Formats**: Support for TXT, DOC, DOCX, and PDF inputs
- **Responsive Web Interface**: Modern Bootstrap 5 design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pdflatex (for PDF compilation)
- OpenAI API Key (for AI features)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Doc2LaTeX_Project
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up OpenAI API Key**
```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

4. **Run the application**
```bash
# AI-Enhanced Web Application
python app_ai.py

# Command Line Interface
python ai_convert.py --input document.txt --output ./output --build
```

## 🎯 Usage

### Web Interface
1. Open http://localhost:5001 in your browser
2. Upload your document (TXT, DOC, DOCX, or PDF)
3. Choose AI enhancement options:
   - Enable/disable AI analysis
   - Select custom title and author
   - Choose template (auto-select recommended)
4. Download your beautiful LaTeX and PDF files

### Command Line
```bash
# Basic conversion with AI
python ai_convert.py --input sample.txt --output ./result --api-key YOUR_KEY

# With custom metadata
python ai_convert.py --input document.docx --output ./result --title "Official Report" --author "Department Name" --build

# Using environment variable for API key
python ai_convert.py --input file.pdf --output ./result --build
```

## 🤖 AI Document Types

The AI system can automatically detect and format:

| Document Type | Template | Use Case |
|---------------|----------|----------|
| 📋 Office Memorandum | `government_memo` | Internal government communications |
| 📢 Circular | `government_circular` | Policy announcements |
| 📝 Notification | `government_notification` | Official notifications |
| 📊 Report | `government_report` | Detailed analysis reports |
| 🎓 Academic Paper | `academic_paper` | Research publications |
| ⚖️ Legal Document | `legal_document` | Legal proceedings |
| 🏢 Corporate Letter | `corporate_letter` | Business communications |

## 🎨 Template Features

### Government Templates
- **Authentic Letterhead**: Official government formatting
- **Color Compliance**: Saffron (#FF9933) and Navy (#138808) schemes
- **Typography**: Professional fonts and spacing
- **Structure**: Proper heading hierarchy and layout

### Academic Templates
- **Citation Ready**: Bibliography and reference support
- **Mathematical Typesetting**: Beautiful equation formatting
- **Figure Management**: Automatic figure and table handling

### Legal Templates
- **Section Numbering**: Proper legal document structure
- **Clause Formatting**: Standard legal document layout
- **Reference System**: Cross-reference capabilities

## 📁 Project Structure

```
Doc2LaTeX_Project/
├── 🤖 AI Enhanced Files
│   ├── ai_convert.py           # AI-powered CLI converter
│   ├── app_ai.py              # AI-enhanced web application
│   └── src/
│       ├── ai_processor.py     # OpenAI GPT-4 integration
│       └── template_engine.py  # Indian government templates
├── 🌐 Web Interface
│   └── templates/
│       ├── index_ai.html       # Enhanced upload interface
│       └── result_ai.html      # AI analysis results
├── ⚙️ Configuration
│   ├── config/
│   │   ├── brand.yaml         # Branding configuration
│   │   ├── docmeta.yaml       # Document metadata
│   │   └── mappings.yaml      # Text processing mappings
├── 📄 Legacy Files
│   ├── app.py                 # Original Flask app
│   ├── src/convert.py         # Basic converter
│   └── templates/
└── 📚 Documentation
    └── README.md              # This file
```

## 🔧 Configuration

### OpenAI API Setup
1. Get your API key from https://platform.openai.com/
2. Set the environment variable `OPENAI_API_KEY`
3. The system uses GPT-4 for optimal results

### Document Metadata (config/docmeta.yaml)
```yaml
meta:
  title: "Document Title"
  subtitle: "Document Subtitle"
  author: "Author Name"
  date: "2024-01-15"
  department: "Department Name"
```

### Branding (config/brand.yaml)
```yaml
brand:
  primary_color: "#138808"      # Indian Navy
  secondary_color: "#FF9933"    # Indian Saffron
  font_main: "Latin Modern Roman"
  logo_path: "assets/emblem.png"
```

## 🌟 AI Analysis Features

### Document Classification
- Automatic document type detection
- Confidence scoring (0-100%)
- Context-aware template selection

### Content Enhancement
- Structure optimization
- Language refinement
- Formatting improvements
- Consistency checks

### Metadata Extraction
- Title and author detection
- Department identification
- Classification assignment
- Summary generation

### Intelligent Suggestions
- Content improvement recommendations
- Formatting enhancement tips
- Compliance suggestions
- Best practice guidance

## 📊 API Reference

### AI Processor
```python
from src.ai_processor import AIDocumentProcessor

# Initialize
processor = AIDocumentProcessor(api_key="your_key")

# Analyze document
analysis = processor.analyze_document(text)

# Enhance content
enhanced = processor.enhance_content_structure(text, analysis)

# Get suggestions
suggestions = processor.suggest_improvements(text, analysis)
```

### Template Engine
```python
from src.template_engine import get_template_by_type

# Generate LaTeX
latex_doc = get_template_by_type(
    template_type="government_memo",
    metadata={"title": "Report", "author": "Officer"},
    content="Document content..."
)
```

## 🚀 Deployment

### Local Development
```bash
python app_ai.py
# Access at http://localhost:5001
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:5001 app_ai:app

# Using Docker
docker build -t doc2latex-ai .
docker run -p 5001:5001 -e OPENAI_API_KEY=your_key doc2latex-ai
```

## 🔍 Troubleshooting

### Common Issues

**ModuleNotFoundError: No module named 'openai'**
```bash
pip install openai
```

**API Key Issues**
- Ensure OPENAI_API_KEY is set
- Verify API key is valid
- Check OpenAI account credits

**PDF Compilation Errors**
- Install TexLive or MiKTeX
- Ensure pdflatex is in PATH
- Check LaTeX package dependencies

**Template Issues**
- Verify template type exists
- Check metadata format
- Ensure content encoding is UTF-8

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI GPT-4**: For intelligent document analysis
- **LaTeX Community**: For beautiful typesetting
- **Government of India**: For formatting standards
- **Bootstrap**: For responsive design
- **Flask**: For web framework

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**Made with ❤️ for beautiful documents and AI-powered intelligence**

> Transform your documents into professional, compliant, and beautiful LaTeX with the power of artificial intelligence and Indian government standards.