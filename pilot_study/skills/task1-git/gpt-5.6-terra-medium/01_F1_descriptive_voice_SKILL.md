---
name: open-issue-report-descriptive
description: Generate an issue report for repository X with open issue counts titles and recent updates.
---
# Generate an Open Issue Report

1. You should run the following command to retrieve open issues from repository X. The command excludes pull requests and orders the results by most recent update:

   ```sh
   gh issue list --repo X --state open --limit 1000 --search "sort:updated-desc" --json number,title,updatedAt > open_issues.json
   ```

2. You should count the issues in `open_issues.json` and create `issue_report.md`. The report should state that number as the total count of open issues.

3. You should add every issue as a list item containing its number and title.

4. You should mark the first three issues in the update-ordered results with a star. Those entries should retain their issue numbers and titles.

5. You should save the completed report as `issue_report.md`.
