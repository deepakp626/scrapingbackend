# Graph Report - scrapingbackend  (2026-10-04)

## Corpus Check
- 18 files · ~5,420 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .lock 1)

## Summary
- 128 nodes · 220 edges · 11 communities (7 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `aa2b5dd5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BaseModel
- updateBlog
- vercel.json
- blogServices.py
- blogRoute.py
- storage.py
- pdfRoute.py
- pdf_data_pytesseract.py
- scrapingbackend

## God Nodes (most connected - your core abstractions)
1. `Blog` - 8 edges
2. `upload_image()` - 7 edges
3. `createBlog()` - 7 edges
4. `deleteBlogService()` - 7 edges
5. `updateBlog()` - 6 edges
6. `delete_image()` - 6 edges
7. `getBlogBySlug()` - 6 edges
8. `updateBlogService()` - 6 edges
9. `compress_image_to_webp()` - 6 edges
10. `createBlog()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `getLBog()` --calls--> `getBlogBySlug()`  [EXTRACTED]
  app/api/blogRoute.py → services/blogServices.py
- `updateBlog()` --calls--> `updateBlogService()`  [EXTRACTED]
  app/api/blogRoute.py → services/blogServices.py
- `deleteBlog()` --calls--> `deleteBlogService()`  [EXTRACTED]
  app/api/blogRoute.py → services/blogServices.py
- `getPaginatedBLog()` --calls--> `get_paginated_blogs()`  [EXTRACTED]
  app/api/blogRoute.py → services/blogServices.py
- `createBlog()` --calls--> `upload_image()`  [EXTRACTED]
  services/blogServices.py → database/storage.py

## Import Cycles
- None detected.

## Communities (11 total, 4 thin omitted)

### Community 1 - "updateBlog"
Cohesion: 0.14
Nodes (15): BlogCreate, BlogResponse, BlogUpdate, createBlog(), deleteBlog(), getLBog(), getPaginatedBLog(), AsyncSession (+7 more)

### Community 2 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

### Community 3 - "blogServices.py"
Cohesion: 0.14
Nodes (22): delete_image(), Delete a blog thumbnail from Supabase., Replace an existing image. No delete is required because upload_image() already…, replace_image(), datetime, DeclarativeBase, math, Base (+14 more)

### Community 4 - "blogRoute.py"
Cohesion: 0.12
Nodes (18): app_api, CodeExecutionRequest, CodeExecutionResponse, _decode(), execute_code(), BaseModel, post, connectDB() (+10 more)

### Community 5 - "storage.py"
Cohesion: 0.19
Nodes (14): delete_image(), replace_image(), upload_image(), Convert blog slug into a safe and consistent storage filename. Example: "my-…, Upload or replace a blog thumbnail. Uses upsert=True so uploading an existing…, _safe_filename(), upload_image(), dotenv (+6 more)

### Community 7 - "pdfRoute.py"
Cohesion: 0.13
Nodes (23): compress_pdf(), extract_images_from_pdf(), lock_pdf(), ocr_pdf(), pdf_to_html(), pdf_to_word(), post, UploadFile (+15 more)

### Community 9 - "pdf_data_pytesseract.py"
Cohesion: 0.18
Nodes (9): PDFTextExtractor, Render page as image and run OCR., Extract text from PDF with hybrid native + OCR support and detailed page…, io, pil, pymupdf, pytesseract, shutil (+1 more)

## Knowledge Gaps
- **4 isolated node(s):** `scrapingbackend`, `version`, `builds`, `routes`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 47 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PDFTextExtractor` connect `pdf_data_pytesseract.py` to `pdfRoute.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `upload_image()` connect `storage.py` to `blogServices.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Blog` (e.g. with `deleteBlogService()` and `get_paginated_blogs()`) actually correct?**
  _`Blog` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `scrapingbackend`, `version`, `builds` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updateBlog` be split into smaller, more focused modules?**
  _Cohesion score 0.13970588235294118 - nodes in this community are weakly interconnected._
- **Should `blogServices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14130434782608695 - nodes in this community are weakly interconnected._
- **Should `blogRoute.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._