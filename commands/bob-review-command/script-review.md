---
owner: kai
---

# Script Review

After emitting the command review output, find `.py` files
associated with the anchor:

1. If the anchor is `foo.md`, look for a sibling folder named
   `foo/` and collect all `.py` files in it (non-recursive).
2. Also include any `.py` paths referenced inside the anchor
   text that exist on disk.

For each `.py` file found, spawn `/bob-review-script` as a
subagent. Pass the file's absolute path as `$ARGUMENTS` and
include this context in the subagent briefing:

- the script's role in the command workflow (from `## Collect`)
- the inputs, outputs, and validation checks the script must
  implement per the command's contract
- any downstream fields the script's output must satisfy

Bob should flag gaps between the script's actual behavior and
the command contract as additional findings, beyond standard
R1–R7 criteria.

Append findings under a `## Script Review` heading, one
subsection per file. If no `.py` files are found, note:

\`\`\`text
Script Review: no .py files found for this anchor.
\`\`\`
