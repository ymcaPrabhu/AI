#!/usr/bin/env python3
"""
Overleaf Project Packager
Creates zip files from LaTeX projects for easy upload to Overleaf
"""

import argparse
import zipfile
import os
from pathlib import Path
import shutil

def create_overleaf_zip(source_dir: str, output_zip: str) -> bool:
    """
    Create a zip file from LaTeX project directory for Overleaf upload
    
    Args:
        source_dir: Path to the LaTeX project directory
        output_zip: Path for the output zip file
    
    Returns:
        bool: True if successful, False otherwise
    """
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
                            print(f"Added: {rel_path}")
            
            print(f"\nSuccessfully created Overleaf zip with {file_count} files: {output_path}")
            return True
            
    except Exception as e:
        print(f"Error creating zip file: {e}")
        return False

def validate_latex_project(project_dir: str) -> bool:
    """
    Validate that the directory contains a valid LaTeX project
    
    Args:
        project_dir: Path to check
        
    Returns:
        bool: True if valid LaTeX project, False otherwise
    """
    project_path = Path(project_dir)
    
    if not project_path.exists():
        print(f"Project directory does not exist: {project_path}")
        return False
    
    # Check for main.tex file
    main_tex = project_path / 'main.tex'
    if not main_tex.exists():
        print(f"No main.tex file found in {project_path}")
        return False
    
    print(f"Valid LaTeX project found at: {project_path}")
    return True

def main():
    """Main entry point for the Overleaf packager"""
    parser = argparse.ArgumentParser(description='Package LaTeX projects for Overleaf upload')
    parser.add_argument('--src', required=True, help='Source LaTeX project directory')
    parser.add_argument('--zip', required=True, help='Output zip file path')
    parser.add_argument('--validate', action='store_true', help='Validate project before zipping')
    
    args = parser.parse_args()
    
    print(f"Packaging LaTeX project: {args.src}")
    
    # Validate project if requested
    if args.validate:
        if not validate_latex_project(args.src):
            print("Project validation failed. Aborting.")
            return 1
    
    # Create the zip file
    success = create_overleaf_zip(args.src, args.zip)
    
    if success:
        zip_size = Path(args.zip).stat().st_size / 1024  # KB
        print(f"\n✓ Overleaf package ready: {args.zip} ({zip_size:.1f} KB)")
        print("You can now upload this zip file directly to Overleaf.")
        return 0
    else:
        print("\n✗ Failed to create Overleaf package")
        return 1

if __name__ == '__main__':
    exit(main())