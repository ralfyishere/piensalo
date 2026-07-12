# Key — dev-04-bishop-domination

The bishop domination number of the 8x8 board is **8**.

`MIN_BISHOPS: 8`

Reasoning sketch (for judging the justification, not deterministically scored):
- Bishops on light and dark squares move on independent diagonal colorings, so
  the problem splits into dominating the light-square diagonals and the
  dark-square diagonals separately.
- A known construction places 8 bishops (e.g. along a central file/row pattern)
  so every square is occupied or attacked; 8 suffice.
- A counting/pigeonhole argument on the diagonals shows fewer than 8 cannot
  cover all squares of both colors. Hence the minimum is exactly 8.

This is hard combinatorial reasoning with a specific correct value that no
generic procedure can supply. Common wrong answers: 6 (confusing domination
with a weaker covering), 10, or 14 (the *independent* non-attacking bishops
maximum is 14 — a different problem). The grader's prose fallback treats 6, 10
and 14 as veto trap values and never infers the answer from mentions of the
board size ("8x8").
