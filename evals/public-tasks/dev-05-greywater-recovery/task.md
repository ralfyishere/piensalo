<!-- Fable Think eval task | label: DEVELOPMENT | id: dev-05-greywater-recovery -->

# Task: Greywater recovery report

A greenhouse treats greywater through a four-stage recovery train. **2,000
litres per day** enter stage 1. Each stage passes a fraction of the water
that *enters it* on to the next stage; the rest is lost as sludge or
evaporation:

- Stage 1 passes 90% of what enters it.
- Stage 2 passes 85% of what enters it.
- Stage 3 passes 80% of what enters it.
- Stage 4 passes 75% of what enters it.

The water leaving stage 4 is the usable recovered water. Fresh mains water
costs **EUR 3.20 per cubic metre** (1 cubic metre = 1,000 litres). Assume a
30-day month.

Deliver, in your answer file:

1. A `WORKING:` section showing the litres/day leaving each of the four
   stages.
2. A line exactly of the form
   `RECOVERED_LPD: <usable recovered water, litres per day, integer>`
3. A line exactly of the form
   `RECOVERED_M3_MONTH: <usable recovered water over the 30-day month, in
   cubic metres, two decimals>`
4. A line exactly of the form
   `SAVINGS_EUR_MONTH: <mains water cost avoided over the month, EUR, two
   decimals>`

The three summary lines are parsed by a script; get the formats exact.
