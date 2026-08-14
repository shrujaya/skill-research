---
name: open-issue-report-hyper-detailed
description: Generate an exact markdown report for repository X open issues using the gh CLI.
---
# Generate an Open Issue Report

Run these commands from the directory where `issue_report.md` belongs.

1. Retrieve up to 1,000 open issues from repository X. Request exactly the `number`, `title`, and `updatedAt` fields. Use `--state open` and the search qualifier `sort:updated-desc`; `gh issue list` returns issues rather than pull requests.

   ```sh
   gh issue list --repo X --state open --limit 1000 --search "sort:updated-desc" --json number,title,updatedAt > open_issues.json
   ```

2. Create `issue_report.md` with this exact heading and count line. Derive `COUNT` from the number of objects in `open_issues.json`.

   ```markdown
   # Open Issues

   Total open issues: COUNT

   ## Issues
   ```

3. Add one list item for every object in `open_issues.json`, in its existing order. Use exactly this format, substituting the issue number and title:

   ```markdown
   - #NUMBER TITLE
   ```

4. Add `⭐ ` immediately before `#NUMBER` for items at zero-based positions `0`, `1`, and `2`. Keep every other item unstarred. The first three objects are the three most recently updated because the retrieval command uses `sort:updated-desc`.

5. Save only the finished markdown report at the exact path `issue_report.md`.
