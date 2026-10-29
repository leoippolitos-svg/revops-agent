---
name: html-report
description: Builds a one-page HTML report or presentation using the Fernway design system. Use when someone asks for a report, a pipeline review, a slide for a meeting, a visual summary or "something I can share".
---

# HTML report

## Steps

1. Agree on the question the report answers, in one sentence. A report without a question is a data dump.
2. Get the numbers through the normal answer protocol (definitions first, gold only).
3. Load the design tokens from `design-system/tokens.json` (colors, fonts, spacing). Never invent colors.
4. Build a single self-contained HTML file: title, the answer in one line, at most four charts or tables, definitions used, data date.
5. Run the checklist below before delivering.

## Checklist

- [ ] Every number has its definition and source table in a footnote
- [ ] Data date shown at the top
- [ ] Charts have titles that state the takeaway, not just the metric name
- [ ] Readable on a phone
- [ ] No data beyond what the question needs

## Troubleshooting

- **Too many charts**: keep the ones that support the one-line answer; move the rest to an appendix link.
