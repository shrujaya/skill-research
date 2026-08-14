---
name: open-issue-report-emphasis
description: Generate an issue report for repository X with open issue counts titles and recent updates.
---
# Generate an Open Issue Report

1. Run the following command to retrieve open issues from repository X, excluding pull requests, ordered by most recent update:

   ```sh
   gh issue list --repo X --state open --limit 1000 --search "sort:updated-desc" --json number,title,updatedAt > open_issues.json
   ```

2. Count the issues in `open_issues.json` and create `issue_report.md`. The report MUST state the count as the total number of open issues.

3. List every issue using its number and title. NEVER include pull requests in this list.

4. Mark the first three issues from the update-ordered results with a star. IMPORTANT: mark exactly the three most recently updated issues.

5. Save the completed report as `issue_report.md`.
