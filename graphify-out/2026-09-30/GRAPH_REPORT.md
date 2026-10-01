# Graph Report - scrapingbackend  (2026-09-27)

## Corpus Check
- 14 files · ~4,293 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .lock 1)

## Summary
- 109 nodes · 191 edges · 12 communities (9 shown, 3 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7ab180b1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BaseModel
- AsyncSession
- db.py
- blogServices.py
- code_Engine_Route.py
- blogRoute.py
- pdfRoute.py
- createBlog
- pdf_data_pytesseract.py
- updateBlog
- scrapingbackend

## God Nodes (most connected - your core abstractions)
1. `Blog` - 8 edges
2. `updateBlog()` - 6 edges
3. `updateBlogService()` - 6 edges
4. `deleteBlogService()` - 6 edges
5. `createBlog()` - 5 edges
6. `execute_code()` - 5 edges
7. `upload_image()` - 5 edges
8. `replace_image()` - 5 edges
9. `createBlog()` - 5 edges
10. `getBlogBySlug()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `getLBog()` --calls--> `getBlogBySlug()`  [EXTRACTED]
  app/api/blogRoute.py → services/blogServices.py
- `updateBlog()` --calls--> `updateBlogService()`  [EXTRACTED]
  app/api/blogRoute.py → services/blogServices.py
- `deleteBlog()` --calls--> `deleteBlogService()`  [EXTRACTED]
  app/api/blogRoute.py → services/blogServices.py
- `getPaginatedBLog()` --calls--> `get_paginated_blogs()`  [EXTRACTED]
  app/api/blogRoute.py → services/blogServices.py
- `deleteBlogService()` --uses--> `Blog`  [INFERRED]
  services/blogServices.py → models/blog.py

## Import Cycles
- None detected.

## Communities (12 total, 3 thin omitted)

### Community 1 - "AsyncSession"
Cohesion: 0.40
Nodes (6): deleteBlog(), getLBog(), getPaginatedBLog(), AsyncSession, get, delete

### Community 2 - "db.py"
Cohesion: 0.29
Nodes (6): connectDB(), dotenv, fastapi_middleware_cors, get, read_root(), sqlalchemy_ext_asyncio

### Community 3 - "blogServices.py"
Cohesion: 0.16
Nodes (22): delete_image(), replace_image(), upload_image(), datetime, DeclarativeBase, math, Base, Blog (+14 more)

### Community 4 - "code_Engine_Route.py"
Cohesion: 0.21
Nodes (10): CodeExecutionRequest, CodeExecutionResponse, _decode(), execute_code(), BaseModel, post, field_validator, judge0api (+2 more)

### Community 5 - "blogRoute.py"
Cohesion: 0.40
Nodes (4): app_api, get_db(), fastapi, typing

### Community 7 - "pdfRoute.py"
Cohesion: 0.13
Nodes (23): compress_pdf(), extract_images_from_pdf(), lock_pdf(), ocr_pdf(), pdf_to_html(), pdf_to_word(), post, UploadFile (+15 more)

### Community 8 - "createBlog"
Cohesion: 0.40
Nodes (4): BlogCreate, createBlog(), post, UploadFile

### Community 9 - "pdf_data_pytesseract.py"
Cohesion: 0.18
Nodes (9): PDFTextExtractor, Render page as image and run OCR., Extract text from PDF with hybrid native + OCR support and detailed page…, io, pil, pymupdf, pytesseract, shutil (+1 more)

### Community 10 - "updateBlog"
Cohesion: 0.33
Nodes (5): BlogResponse, BlogUpdate, BaseModel, updateBlog(), put

## Knowledge Gaps
- **1 isolated node(s):** `scrapingbackend`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 38 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PDFTextExtractor` connect `pdf_data_pytesseract.py` to `pdfRoute.py`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `updateBlog()` connect `updateBlog` to `createBlog`, `AsyncSession`, `blogServices.py`, `blogRoute.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Blog` (e.g. with `deleteBlogService()` and `get_paginated_blogs()`) actually correct?**
  _`Blog` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `scrapingbackend` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pdfRoute.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12681159420289856 - nodes in this community are weakly interconnected._