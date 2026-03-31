#!/bin/bash
# add_document.sh — Add a new document to ABE's knowledge base.
#
# The gno daemon auto-detects new files, but this script also
# handles PDF-to-text conversion if you add a PDF manually.
#
# Usage:
#   bash scripts/add_document.sh /path/to/document.pdf
#   bash scripts/add_document.sh /path/to/document.txt

set -e

KNOWLEDGE_DIR="/Users/lucas/Documents/Pi515/ABE/knowledge"
FILE="$1"

if [ -z "$FILE" ]; then
  echo "Usage: bash scripts/add_document.sh /path/to/file"
  exit 1
fi

if [ ! -f "$FILE" ]; then
  echo "File not found: $FILE"
  exit 1
fi

FILENAME=$(basename "$FILE")
DEST="$KNOWLEDGE_DIR/$FILENAME"

# Copy the file
cp "$FILE" "$DEST"
echo "Copied: $FILENAME → knowledge/"
echo ""
echo "Document added to knowledge/"
echo "The gno daemon will index it automatically."
echo "Or run manually: gno index"
