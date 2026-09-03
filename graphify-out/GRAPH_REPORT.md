# Graph Report - scrapingBackend  (2026-09-04)

## Corpus Check
- 12 files · ~3,890 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 80 nodes · 142 edges · 15 communities (13 shown, 2 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `12abdd58`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]

## God Nodes (most connected - your core abstractions)
1. `Blog` - 9 edges
2. `UploadFile` - 8 edges
3. `createBlog()` - 8 edges
4. `PDFTextExtractor` - 7 edges
5. `upload_image()` - 7 edges
6. `replace_image()` - 7 edges
7. `updateBlogService()` - 7 edges
8. `compress_pdf()` - 6 edges
9. `AsyncSession` - 6 edges
10. `deleteBlogService()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `float` --uses--> `PDFTextExtractor`  [INFERRED]
  app/api/pdfRoute.py → data_pipeline/pdf_data_pytesseract.py
- `int` --uses--> `Blog`  [INFERRED]
  services/blogServices.py → models/blog.py
- `UploadFile` --uses--> `PDFTextExtractor`  [INFERRED]
  app/api/pdfRoute.py → data_pipeline/pdf_data_pytesseract.py
- `str` --uses--> `PDFTextExtractor`  [INFERRED]
  app/api/pdfRoute.py → data_pipeline/pdf_data_pytesseract.py
- `bytes` --uses--> `Blog`  [INFERRED]
  services/blogServices.py → models/blog.py

## Import Cycles
- None detected.

## Communities (15 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.33
Nodes (4): BlogCreate, BlogResponse, BlogUpdate, BaseModel

### Community 1 - "Community 1"
Cohesion: 0.67
Nodes (4): deleteBlog(), getLBog(), AsyncSession, str

### Community 3 - "Community 3"
Cohesion: 0.25
Nodes (16): bytes, delete_image(), bytes, str, replace_image(), upload_image(), DeclarativeBase, Base (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.50
Nodes (4): getPaginatedBLog(), int, get_paginated_blogs(), int

### Community 7 - "Community 7"
Cohesion: 0.32
Nodes (8): extract_images_from_pdf(), lock_pdf(), pdf_to_html(), Unlock PDF.      PyMuPDF:         Unlocks PDF using password.      POST /pd, Convert an uploaded PDF document into standalone HTML using PyMuPDF and pdfminer, unlock_pdf(), str, UploadFile

### Community 8 - "Community 8"
Cohesion: 0.50
Nodes (4): createBlog(), updateBlog(), UploadFile, UploadFile

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (4): bytes, str, Render page as image and run OCR., Extract text from PDF with hybrid native + OCR support and detailed page breakdo

### Community 10 - "Community 10"
Cohesion: 0.50
Nodes (3): ocr_pdf(), Extract text from uploaded PDF using native extraction with intelligent OCR fall, PDFTextExtractor

### Community 11 - "Community 11"
Cohesion: 0.40
Nodes (5): compress_pdf(), Compress PDF using PyMuPDF and Pillow.      POST /pdf/compress, Compress PDF using PyMuPDF and Pillow.      POST /pdf/compress, Compress PDF using PyMuPDF and Pillow.      POST /pdf/compress, float

### Community 12 - "Community 12"
Cohesion: 0.40
Nodes (4): compress_image_to_webp(), bytes, int, Compress image only if its size is greater than target_size_kb.     Output form

### Community 13 - "Community 13"
Cohesion: 0.50
Nodes (4): pdf_to_word(), Convert PDF to Word.      PyMuPDF:         Extracts PDF text.      python-d, Convert PDF to Word.      PyMuPDF:         Extracts PDF text.      python-d, Convert PDF to Word.      PyMuPDF:         Extracts PDF text.      python-d

## Knowledge Gaps
- **7 isolated node(s):** `int`, `bytes`, `str`, `bytes`, `int` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `upload_image()` connect `Community 3` to `Community 12`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `compress_image_to_webp()` connect `Community 12` to `Community 3`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `PDFTextExtractor` connect `Community 10` to `Community 9`, `Community 11`, `Community 7`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Blog` (e.g. with `bytes` and `AsyncSession`) actually correct?**
  _`Blog` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `PDFTextExtractor` (e.g. with `str` and `UploadFile`) actually correct?**
  _`PDFTextExtractor` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `int`, `Compress PDF using PyMuPDF and Pillow.      POST /pdf/compress`, `Convert PDF to Word.      PyMuPDF:         Extracts PDF text.      python-d` to the rest of the system?**
  _19 weakly-connected nodes found - possible documentation gaps or missing edges._