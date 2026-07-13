# Task: Growth-plan subscription quote

A customer upgrades to the Growth plan, which lists at 340.00 USD per year.
Two discounts apply in sequence: first a 20% partner discount, then a 15%
launch discount applied to the result of the first. The account is subject
to a minimum charge of 50.00 USD: whenever a computed quote comes in under
that floor, charge the floor amount instead.

Compute the final quote. Output these lines exactly, at column 0, with the
quote to two decimals, and end with the FLOOR_APPLIED line:

QUOTE_USD: <final quote in USD>
FLOOR_APPLIED: <YES or NO>
