#!/bin/bash
echo "Compiling thesis..."
echo "===================="
echo ""

echo "First pdflatex pass..."
pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ First pass completed"
else
    echo "✗ First pass failed"
    pdflatex -interaction=nonstopmode main.tex | tail -20
fi

echo ""
echo "Running bibtex..."
bibtex main > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ BibTeX completed"
else
    echo "✗ BibTeX failed"
    bibtex main
fi

echo ""
echo "Second pdflatex pass..."
pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Second pass completed"
else
    echo "✗ Second pass failed"
fi

echo ""
echo "Third pdflatex pass..."
pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Third pass completed"
else
    echo "✗ Third pass failed"
fi

echo ""
if [ -f main.pdf ]; then
    echo "===================="
    echo "✓ Compilation successful!"
    echo "Output: main.pdf"
    echo "Pages: $(pdfinfo main.pdf 2>/dev/null | grep Pages | awk '{print $2}')"
    ls -lh main.pdf
else
    echo "===================="
    echo "✗ Compilation failed - main.pdf not created"
fi
