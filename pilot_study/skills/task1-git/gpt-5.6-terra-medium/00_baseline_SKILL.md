---
name: open-issue-report
description: Generate an issue report for repository X with open issue counts titles and recent updates.
---
# Generate an Open Issue Report

1. Run the following command to retrieve open issues from repository X, excluding pull requests, ordered by most recent update:

   ```sh
   gh issue list --repo X --state open --limit 1000 --search "sort:updated-desc" --json number,title,updatedAt > open_issues.json
   ```

2. Count the issues in `open_issues.json` and create `issue_report.md`. State the count as the total number of open issues.

3. Add a list of every issue using its number and title.

4. Mark the first three issues from the update-ordered results with a star. Include their issue numbers and titles in the list.

5. Save the completed report as `issue_report.md`.
