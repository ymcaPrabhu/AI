@echo off
REM Simple PDF compilation script for Windows (no Perl required)
REM Usage: compile_pdf.bat path\to\main.tex

if "%1"=="" (
    echo Usage: compile_pdf.bat path\to\main.tex
    exit /b 1
)

set TEX_FILE=%1
set TEX_DIR=%~dp1
set TEX_NAME=%~n1

echo Compiling PDF using pdflatex...
echo Working directory: %TEX_DIR%
echo File: %TEX_NAME%.tex

cd /d "%TEX_DIR%"

echo.
echo === First pass ===
pdflatex -interaction=nonstopmode "%TEX_NAME%.tex"
if errorlevel 1 (
    echo Error in first pass
    goto :error
)

echo.
echo === Second pass (for references) ===
pdflatex -interaction=nonstopmode "%TEX_NAME%.tex"
if errorlevel 1 (
    echo Error in second pass
    goto :error
)

if exist "%TEX_NAME%.pdf" (
    echo.
    echo ✓ PDF compilation successful!
    echo Output: %TEX_DIR%%TEX_NAME%.pdf
    
    REM Clean up auxiliary files
    if exist "%TEX_NAME%.aux" del "%TEX_NAME%.aux"
    if exist "%TEX_NAME%.log" del "%TEX_NAME%.log"
    if exist "%TEX_NAME%.out" del "%TEX_NAME%.out"
    if exist "%TEX_NAME%.toc" del "%TEX_NAME%.toc"
    
    exit /b 0
) else (
    echo ✗ PDF file was not created
    goto :error
)

:error
echo.
echo ✗ PDF compilation failed
echo Check the log files for details
exit /b 1