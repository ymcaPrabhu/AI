"""
Professional LaTeX Template Generator for Indian Government Standards
Creates beautiful, compliant documents following GoI formatting guidelines
"""

from typing import Dict, Any
from enum import Enum
import datetime
import re

def escape_latex(text: str) -> str:
    """Escape special LaTeX characters to prevent compilation errors"""
    if not isinstance(text, str):
        return str(text)
    
    # Dictionary of LaTeX special characters and their escaped versions
    latex_special_chars = {
        '#': '\\#',
        '$': '\\$',
        '%': '\\%',
        '&': '\\&',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '^': '\\textasciicircum{}',
        '~': '\\textasciitilde{}',
        '\\': '\\textbackslash{}',
    }
    
    # Escape special characters
    for char, escaped in latex_special_chars.items():
        text = text.replace(char, escaped)
    
    # Handle Unicode characters that might cause issues
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    return text

def clean_content_for_latex(content: str) -> str:
    """Clean and prepare content for LaTeX compilation"""
    # Check if content already contains LaTeX commands
    # If it does, selectively escape only problematic characters, not LaTeX commands
    has_latex_commands = bool(re.search(r'\\[a-zA-Z]+\{', content))
    
    if has_latex_commands:
        # Content already has LaTeX markup, selectively escape only text characters
        # that can cause compilation issues, but preserve LaTeX commands
        selective_chars = {
            '&': '\\&',
            '#': '\\#', 
            '$': '\\$',
            '%': '\\%',
            '_': '\\_',
            '^': '\\textasciicircum{}',
            '~': '\\textasciitilde{}'
        }
        
        for char, escaped in selective_chars.items():
            content = content.replace(char, escaped)
            
        # Normalize formatting
        content = re.sub(r'\n\s*\n', r'\n\n', content)  # Normalize paragraph breaks
        content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)  # Remove leading whitespace
    else:
        # Raw text content, needs full escaping
        content = escape_latex(content)
        # Fix common formatting issues
        content = re.sub(r'\n\s*\n', r'\n\n', content)  # Normalize paragraph breaks
        content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)  # Remove leading whitespace
    
    return content

class TemplateType(Enum):
    INDIAN_GOVERNMENT = "indian_government"
    ACADEMIC_FORMAL = "academic_formal"
    LEGAL_STANDARD = "legal_standard"
    CORPORATE_REPORT = "corporate_report"
    RESEARCH_PAPER = "research_paper"

class IndianLaTeXTemplates:
    """Professional LaTeX templates following Indian government standards"""
    
    @staticmethod
    def get_government_template(metadata: Dict[str, Any], content: str) -> str:
        """Generate beautiful Indian Government document template"""
        
        title = escape_latex(metadata.get('title', 'Government Document'))
        author = escape_latex(metadata.get('author', 'Government of India'))
        department = escape_latex(metadata.get('department', 'Department Name'))
        classification = escape_latex(metadata.get('classification', 'Public'))
        file_number = escape_latex(metadata.get('file_number', 'No. 1/1/2025-Desk'))
        
        # Clean content for LaTeX
        cleaned_content = clean_content_for_latex(content)
        
        template = f"""\\documentclass[11pt,a4paper]{{article}}

% Indian Government Document Template
% Compliant with Manual of Office Procedures, Government of India

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
\\usepackage{{enumitem}}
\\usepackage{{array}}
\\usepackage{{longtable}}
\\usepackage{{booktabs}}
\\usepackage{{multirow}}
\\usepackage{{tikz}}

% Page setup according to GoI standards
\\geometry{{
    top=2.5cm,
    bottom=2.5cm,
    left=3cm,
    right=2.5cm,
    headheight=1.5cm,
    headsep=1cm,
    footskip=1cm
}}

% Indian Government Colors
\\definecolor{{saffron}}{{RGB}}{{255, 153, 51}}
\\definecolor{{navyblue}}{{RGB}}{{0, 0, 128}}
\\definecolor{{darkgreen}}{{RGB}}{{19, 136, 8}}
\\definecolor{{ashokachakrablue}}{{RGB}}{{6, 49, 137}}

% Font settings (Government standard - pdflatex compatible)
% Using standard LaTeX fonts that work with pdflatex

% Header and Footer setup
\\pagestyle{{fancy}}
\\fancyhf{{}}

% Government header
\\fancyhead[C]{{%
    \\begin{{minipage}}{{\\textwidth}}
        \\centering
        \\textbf{{\\large Government of India}} \\\\[0.2cm]
        \\textbf{{\\normalsize {department}}} \\\\[0.1cm]
        \\rule{{\\textwidth}}{{0.5pt}}
    \\end{{minipage}}
}}

\\fancyfoot[C]{{\\thepage}}
\\fancyfoot[L]{{\\small Classification: {classification}}}
\\fancyfoot[R]{{\\small Generated: \\today}}

% Section formatting
\\titleformat{{\\section}}
    {{\\normalfont\\Large\\bfseries\\color{{navyblue}}}}
    {{\\thesection}}{{1em}}{{}}

\\titleformat{{\\subsection}}
    {{\\normalfont\\large\\bfseries\\color{{darkgreen}}}}
    {{\\thesubsection}}{{1em}}{{}}

% Custom commands for Indian government formatting
\\newcommand{{\\filenum}}[1]{{\\textbf{{File No.: }}#1}}
\\newcommand{{\\subject}}[1]{{\\textbf{{Subject: }}#1}}
\\newcommand{{\\reference}}[1]{{\\textbf{{Reference: }}#1}}
\\newcommand{{\\classification}}[1]{{\\textbf{{Classification: }}#1}}

% Document properties
\\title{{{title}}}
\\author{{{author}}}
\\date{{\\today}}

\\begin{{document}}

% Government letterhead (text-based, no external graphics)
\\begin{{center}}
    {{\\Large \\textbf{{\\color{{saffron}}Government of India}}}} \\\\[0.2cm]
    {{\\large \\textbf{{{department}}}}} \\\\[0.3cm]
    \\rule{{0.8\\textwidth}}{{1pt}}
\\end{{center}}

\\vspace{{0.5cm}}

% Document header information
\\begin{{flushleft}}
    \\filenum{{{file_number}}} \\\\[0.3cm]
    \\textbf{{Dated: }}\\today \\\\[0.5cm]
\\end{{flushleft}}

% Document title
\\begin{{center}}
    {{\\Large \\textbf{{\\color{{navyblue}}{title}}}}} \\\\[0.5cm]
\\end{{center}}

% Main content
{cleaned_content}

\\vspace{{2cm}}

% Signature block
\\begin{{flushright}}
    \\begin{{minipage}}{{6cm}}
        \\centering
        \\rule{{5cm}}{{0.5pt}} \\\\[0.2cm]
        ({author}) \\\\
        {department} \\\\
        Government of India
    \\end{{minipage}}
\\end{{flushright}}

% Document footer
\\vfill
\\begin{{center}}
    \\rule{{\\textwidth}}{{0.5pt}} \\\\[0.2cm]
    \\small This document is generated electronically and is valid without signature \\\\
    \\textit{{Satyameva Jayate}} \\quad \\textit{{Truth Alone Triumphs}}
\\end{{center}}

\\end{{document}}"""
        
        return template

    @staticmethod
    def get_academic_template(metadata: Dict[str, Any], content: str) -> str:
        """Generate academic paper template with Indian institutional standards"""
        
        title = metadata.get('title', 'Research Paper')
        author = metadata.get('author', 'Author Name')
        institution = metadata.get('department', 'Institution Name')
        
        template = f"""\\documentclass[12pt,a4paper]{{article}}

% Academic Template for Indian Institutions
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
\\usepackage{{natbib}}
\\usepackage{{abstract}}
\\usepackage{{authblk}}

% Page setup
\\geometry{{
    top=2.5cm,
    bottom=2.5cm,
    left=2.5cm,
    right=2.5cm
}}

% Colors for academic formatting
\\definecolor{{academicblue}}{{RGB}}{{0, 51, 102}}
\\definecolor{{titlecolor}}{{RGB}}{{139, 0, 0}}

% Title formatting
\\title{{\\Large \\textbf{{\\color{{titlecolor}}{title}}}}}
\\author{{{author}}}
\\affil{{{institution}}}
\\date{{\\today}}

% Section formatting
\\titleformat{{\\section}}
    {{\\normalfont\\large\\bfseries\\color{{academicblue}}}}
    {{\\thesection}}{{1em}}{{}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
{metadata.get('summary', 'Abstract content here.')}
\\end{{abstract}}

\\textbf{{Keywords:}} {metadata.get('keywords', 'keyword1, keyword2, keyword3')}

\\tableofcontents
\\newpage

{content}

\\bibliographystyle{{plain}}
\\bibliography{{references}}

\\end{{document}}"""
        
        return template

    @staticmethod
    def get_minimal_template(metadata: Dict[str, Any], content: str) -> str:
        """Generate minimal LaTeX template that always compiles"""
        
        title = escape_latex(metadata.get('title', 'Document'))
        author = escape_latex(metadata.get('author', 'Author'))
        
        # Clean content for LaTeX
        cleaned_content = clean_content_for_latex(content)
        
        template = f"""\\documentclass[11pt,a4paper]{{article}}

% Minimal template using only basic LaTeX packages
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}

% Basic document setup
\\title{{{title}}}
\\author{{{author}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

% Main content
{cleaned_content}

\\end{{document}}"""
        
        return template
        """Generate legal document template following Indian legal standards"""
        
        template = f"""\\documentclass[12pt,a4paper]{{article}}

% Legal Document Template - Indian Standards
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{fancyhdr}}
\\usepackage{{titlesec}}
\\usepackage{{enumerate}}
\\usepackage{{legal}}

% Page setup for legal documents
\\geometry{{
    top=2.5cm,
    bottom=2.5cm,
    left=3.5cm,
    right=2.5cm,
    headheight=1cm
}}

% Legal formatting colors
\\definecolor{{legalblue}}{{RGB}}{{0, 0, 139}}

% Header setup
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[C]{{\\textbf{{Legal Document}}}}
\\fancyfoot[C]{{\\thepage}}

% Legal section numbering
\\renewcommand{{\\thesection}}{{\\Roman{{section}}}}
\\renewcommand{{\\thesubsection}}{{\\arabic{{subsection}}}}

\\title{{\\textbf{{\\color{{legalblue}}{metadata.get('title', 'Legal Document')}}}}}
\\author{{{metadata.get('author', 'Legal Authority')}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

{content}

\\end{{document}}"""
        
        return template

    @staticmethod
    def get_report_template(metadata: Dict[str, Any], content: str) -> str:
        """Generate corporate/government report template"""
        
        template = f"""\\documentclass[11pt,a4paper]{{report}}

% Professional Report Template
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{fancyhdr}}
\\usepackage{{titlesec}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}
\\usepackage{{tocloft}}

% Page setup
\\geometry{{
    top=2.5cm,
    bottom=2.5cm,
    left=3cm,
    right=2.5cm
}}

% Professional colors
\\definecolor{{reportblue}}{{RGB}}{{0, 82, 155}}
\\definecolor{{reportgray}}{{RGB}}{{64, 64, 64}}

% Chapter and section formatting
\\titleformat{{\\chapter}}
    {{\\normalfont\\huge\\bfseries\\color{{reportblue}}}}
    {{\\thechapter}}{{1em}}{{}}

\\titleformat{{\\section}}
    {{\\normalfont\\Large\\bfseries\\color{{reportgray}}}}
    {{\\thesection}}{{1em}}{{}}

\\title{{\\Huge \\textbf{{\\color{{reportblue}}{metadata.get('title', 'Professional Report')}}}}}
\\author{{{metadata.get('author', 'Report Author')}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\tableofcontents
\\listoffigures
\\listoftables

\\chapter{{Executive Summary}}
{metadata.get('summary', 'Executive summary content.')}

{content}

\\end{{document}}"""
        
        return template

def get_template_by_type(template_type: str, metadata: Dict[str, Any], content: str) -> str:
    """Get appropriate template based on document type"""
    
    templates = IndianLaTeXTemplates()
    
    if template_type == "indian_government":
        return templates.get_government_template(metadata, content)
    elif template_type == "academic_formal":
        return templates.get_academic_template(metadata, content)
    elif template_type == "legal_standard":
        return templates.get_legal_template(metadata, content)
    elif template_type == "corporate_report":
        return templates.get_report_template(metadata, content)
    else:
        # Default to government template
        return templates.get_government_template(metadata, content)

# Export templates dictionary for external use
INDIAN_GOVERNMENT_TEMPLATES = {
    'government_memo': {
        'name': 'Government Memorandum',
        'description': 'Official inter-departmental communication',
        'emoji': '📋'
    },
    'government_circular': {
        'name': 'Government Circular', 
        'description': 'Policy announcements and instructions',
        'emoji': '📢'
    },
    'government_notification': {
        'name': 'Government Notification',
        'description': 'Official public notifications',
        'emoji': '📝'
    },
    'government_report': {
        'name': 'Government Report',
        'description': 'Detailed analysis and findings',
        'emoji': '📊'
    },
    'academic_paper': {
        'name': 'Academic Paper',
        'description': 'Research publications and papers',
        'emoji': '🎓'
    },
    'legal_document': {
        'name': 'Legal Document',
        'description': 'Legal proceedings and documents',
        'emoji': '⚖️'
    },
    'corporate_letter': {
        'name': 'Corporate Letter',
        'description': 'Business communications',
        'emoji': '🏢'
    },
    'basic': {
        'name': 'Basic Document',
        'description': 'Simple document format',
        'emoji': '📄'
    }
}