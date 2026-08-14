---
name: open-issue-report-examples
description: Generate an issue report for repository X with open issue counts titles and recent updates.
---
# Generate an Open Issue Report

1. Run the following command to retrieve open issues from repository X, excluding pull requests, ordered by most recent update:

   ```sh
   gh issue list --repo X --state open --limit 1000 --search "sort:updated-desc" --json number,title,updatedAt
   ```

2. Create `issue_report.md`. State the total number of returned issues, then list every issue by number and title.

3. Mark the first three update-ordered issues with a star and save the report.

## Worked Example

Run:

```sh
gh issue list --repo X --state open --limit 1000 --search "sort:updated-desc" --json number,title,updatedAt
```

Receive:

```json
[{"number":42,"title":"Fix login redirect","updatedAt":"2026-08-13T15:00:00Z"},{"number":17,"title":"Add export option","updatedAt":"2026-08-12T09:00:00Z"},{"number":8,"title":"Update documentation","updatedAt":"2026-08-11T18:00:00Z"},{"number":3,"title":"Refine labels","updatedAt":"2026-08-10T12:00:00Z"}]
```

Write `issue_report.md` as:

```markdown
# Open Issues

Total open issues: 4

- ⭐ #42 Fix login redirect
- ⭐ #17 Add export option
- ⭐ #8 Update documentation
- #3 Refine labels
```
