---
name: open-issue-report-verified
description: Generate and verify an issue report for repository X with open issue counts titles and recent updates.
---
# Generate an Open Issue Report

1. Run the following command to retrieve open issues from repository X, excluding pull requests, ordered by most recent update:

   ```sh
   gh issue list --repo X --state open --limit 1000 --search "sort:updated-desc" --json number,title,updatedAt > open_issues.json
   ```

   Verify that `open_issues.json` contains issue objects with `number`, `title`, and `updatedAt` fields before proceeding.

2. Count the issues in `open_issues.json` and create `issue_report.md` with that number as the total open issue count.

   Verify that the stated count equals the number of retrieved issue objects before proceeding.

3. Add every retrieved issue to the report using its number and title.

   Verify that every retrieved issue appears once in the list before proceeding.

4. Mark the first three issues from the update-ordered results with a star.

   Verify that exactly the three most recently updated issues are starred before proceeding.

5. Save the completed report as `issue_report.md`.

   Verify that `issue_report.md` contains the total count, each issue number and title, and stars on the three most recently updated issues.
