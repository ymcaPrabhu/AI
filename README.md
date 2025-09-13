# AI-Enhanced Doc2LaTeX Converter

A sophisticated document conversion system that transforms various document formats into professional LaTeX documents using AI-powered analysis and hybrid processing approaches.

## 🚀 Features

- **AI-Powered Classification**: Uses GPT-4o for intelligent document type detection
- **Hybrid Processing**: Code-first conversion with GPT-4 fallback for complex documents
- **Indian Government Standards**: Compliant with Government of India manual of office procedures
- **Web Interface**: User-friendly Flask web application
- **Multiple Input Formats**: Supports TXT, DOC, DOCX, and PDF files
- **PDF Compilation**: Integrated pdfLaTeX compilation with error handling
- **Template Library**: Pre-built templates for various document types

## 🏛️ Supported Document Types

- Office Memorandums
- Government Circulars
- Notifications
- Reports
- Policy Documents
- Academic Papers
- Legal Documents

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- LaTeX distribution (TeX Live/MiKTeX)
- OpenAI API key (optional, for AI features)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ymcaPrabhu/AI.git
   cd AI
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

### Web Application Usage
1. Start the web server:
   ```bash
   python app_ai.py
   ```

2. Open your browser to `http://localhost:5001`

3. Upload a document and select conversion options

4. Download the generated LaTeX source or compiled PDF

### Command Line Usage
```bash
python src/convert.py --in input/sample.docx --template pro_report --meta config/docmeta.yaml --brand config/brand.yaml --out output/overleaf_project --build
```

### Overleaf Export
```bash
python src/export/pack_overleaf.py --src output/overleaf_project --zip output/overleaf_project.zip
```

## 🤖 AI Optimization

The system uses an intelligent hybrid approach:

1. **Classification**: GPT-4o analyzes document structure and type
2. **Conversion**: Code-based rules handle standard documents efficiently
3. **Enhancement**: GPT-4 processes complex cases requiring advanced understanding
4. **Cost Optimization**: Minimal AI usage while maintaining high quality

## 🏗️ Project Structure

```
├── src/
│   ├── ai_processor.py      # AI document analysis and processing
│   ├── template_engine.py   # LaTeX template generation
│   ├── convert.py          # Command-line conversion tool
│   └── export/
│       └── pack_overleaf.py # Overleaf package creator
├── templates/              # HTML templates for web interface
├── config/                # Configuration files
├── input/                 # Sample input documents
├── app_ai.py             # Main web application
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for AI features
- `DISABLE_AI`: Set to '1' to disable AI features
- `FLASK_DEBUG`: Set to '1' for debug mode
- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 5001)

### Templates
- Modify `config/docmeta.yaml` for document metadata
- Customize `config/brand.yaml` for branding elements
- Edit templates in `src/template_engine.py` for custom formatting

## 🎯 Use Cases

- **Government Offices**: Convert documents to standard government formats
- **Academic Institutions**: Transform research papers and reports
- **Legal Firms**: Format legal documents with proper structure
- **Corporate**: Create professional reports and documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o and GPT-4 API
- Government of India Manual of Office Procedures
- LaTeX community for excellent documentation tools

---

**Note**: This system is optimized for cost-effective AI usage while maintaining high-quality document conversion standards.
