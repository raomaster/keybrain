# Use Case 3: Capture a PDF or Word Document

**Goal:** Add a PDF, Word, Excel, or PowerPoint file to your knowledge base.

## Steps

1. Place the file somewhere accessible
2. In your terminal:
   ```bash
   kb add ~/Downloads/important-paper.pdf
   ```
3. The file is copied to `inbox/`
4. When processed, the agent:
   - Converts the file to Markdown using `markitdown`
   - Classifies the content (article, research, course, etc.)
   - Creates a properly formatted file in the right folder
   - Extracts key information into the frontmatter

## Supported formats

| Format | Extension | Conversion |
|--------|-----------|------------|
| PDF | `.pdf` | Text extraction |
| Word | `.docx` | Full conversion |
| Excel | `.xlsx`, `.xls` | Table conversion |
| PowerPoint | `.pptx` | Slide conversion |
| Images | `.jpg`, `.png` | OCR (requires OpenAI API key) |
| Audio | `.mp3`, `.wav` | Transcription (requires OpenAI API key) |

## Tips
- Office file conversion works 100% locally
- OCR and audio transcription require an OpenAI API key for advanced features
- You can drag and drop files into `inbox/` directly
