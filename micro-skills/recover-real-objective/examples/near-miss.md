# Near-miss example — skill must NOT fire

**Task:** "Increase the upload limit to 25 MB so that users can attach the PDF spec sheets our sales team sends — those run 15–20 MB."

**Why it must not fire:** This matches a counterindication: the request already states its objective ("so that users can attach the PDF spec sheets") and even the sizing rationale. There is nothing to recover.

**Why firing would hurt:** Restating "Interpreting this as: let users attach large PDFs" adds a redundant line that patronizes the user and spends the skill's token budget confirming what was already explicit — pure noise on a fully specified request.
