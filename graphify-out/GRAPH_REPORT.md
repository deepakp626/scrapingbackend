# Graph Report - scrapingBackend  (2026-08-01)

## Corpus Check
- 7 files · ~816 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 37 nodes · 71 edges · 8 communities (6 shown, 2 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f9b6f978`
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

## God Nodes (most connected - your core abstractions)
1. `Blog` - 8 edges
2. `createBlog()` - 6 edges
3. `AsyncSession` - 6 edges
4. `AsyncSession` - 5 edges
5. `str` - 5 edges
6. `getBlogBySlug()` - 5 edges
7. `updateBlogService()` - 5 edges
8. `deleteBlogService()` - 5 edges
9. `get_paginated_blogs()` - 5 edges
10. `BlogCreate` - 4 edges

## Surprising Connections (you probably didn't know these)
- `bytes` --uses--> `Blog`  [INFERRED]
  services/blogServices.py → models/blog.py
- `int` --uses--> `Blog`  [INFERRED]
  services/blogServices.py → models/blog.py
- `AsyncSession` --uses--> `Blog`  [INFERRED]
  services/blogServices.py → models/blog.py
- `str` --uses--> `Blog`  [INFERRED]
  services/blogServices.py → models/blog.py
- `getLBog()` --calls--> `getBlogBySlug()`  [EXTRACTED]
  app/api/blogRoute.py → services/blogServices.py

## Import Cycles
- None detected.

## Communities (8 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.33
Nodes (8): BlogCreate, BlogResponse, BlogUpdate, Config, createBlog(), updateBlog(), BaseModel, UploadFile

### Community 1 - "Community 1"
Cohesion: 0.50
Nodes (4): deleteBlog(), getLBog(), AsyncSession, str

### Community 3 - "Community 3"
Cohesion: 0.67
Nodes (3): DeclarativeBase, Base, Blog

### Community 4 - "Community 4"
Cohesion: 0.60
Nodes (5): deleteBlogService(), getBlogBySlug(), AsyncSession, str, updateBlogService()

### Community 5 - "Community 5"
Cohesion: 0.50
Nodes (4): getPaginatedBLog(), int, get_paginated_blogs(), int

## Knowledge Gaps
- **3 isolated node(s):** `UploadFile`, `int`, `Config`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Blog` connect `Community 3` to `Community 4`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `createBlog()` connect `Community 7` to `Community 0`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `BlogCreate` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Blog` (e.g. with `bytes` and `AsyncSession`) actually correct?**
  _`Blog` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `UploadFile`, `int`, `Config` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._