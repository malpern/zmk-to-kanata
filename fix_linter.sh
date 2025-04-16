#!/bin/bash

# Fix trailing whitespace and ensure newline at end of file for all Python files
find converter -name "*.py" -type f -exec sed -i '' 's/ *$//' {} \;
find converter -name "*.py" -type f -exec bash -c 'if [ "$(tail -c 1 "$1")" != "" ]; then echo "" >> "$1"; fi' _ {} \;

echo "Fixed whitespace issues and missing newlines in all Python files"
