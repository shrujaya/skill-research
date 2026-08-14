---
name: open-issue-report-errors
description: Generate an issue report for repository X with open issue counts titles and recent updates.
---
# Generate an Open Issue Report

1. Run the following command to retrieve open issues from repository X, excluding pull requests, ordered by most recent update:

   ```sh
   gh issue list --repo X --state open --limit 1000 --search "sort:updated-desc" --json number,title,updatedAt > open_issues.json
   ```

2. Detect authentication failure by checking whether the command reports an authentication error or does not produce issue data. Stop and report that `gh` authentication failed.

3. Inspect the retrieved results for pull requests. Detect a mixed result set by finding entries identified as pull requests or entries that do not represent issues. Stop and report that the API response included pull requests.

4. Detect an empty or unexpectedly small issue list by comparing the number of retrieved issues with the expected repository activity. Stop and report that the issue list is empty or unexpectedly small.

5. Count the retrieved issues and create `issue_report.md`. State the count as the total number of open issues.

6. Add every issue as a list item containing its number and title.

7. Mark the first three issues in the update-ordered results with a star. Keep their issue numbers and titles in the list.

8. Save the completed report as `issue_report.md`.
