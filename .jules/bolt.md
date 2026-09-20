## 2026-08-25 - Fix Unindented File Processing in Directory Traversals
**Learning:** An unindented block after `for file in files:` inside an `os.walk` loop causes `UnboundLocalError` on empty directories and silently drops modifications for all files except the last file in each directory, leading to wasted computation and broken sanitization.
**Action:** Always verify that per-file processing and file-saving operations in `os.walk` loops are indented strictly inside the inner `for file in files:` block.
