# Key — demo-03-release-note

Cognition passes iff all three facts appear accurately somewhere in the text:
- "offline" + "sync" both present;
- "40%" (or "40 percent") together with "search";
- "Android 8" together with "September 30".

Contract passes iff the raw text has the exact column-0 lines
`HEADLINE: ...` (<= 80 chars of text), `AUDIENCE: existing-users`,
`CTA: Update Lumen Notes in your app store`, and contains no Markdown bold
or code fences.

Typical failures: vague marketing copy that drops the numbers ("faster than
ever") fails cognition; a correct announcement wrapped in bold fails only
contract/delivery.
