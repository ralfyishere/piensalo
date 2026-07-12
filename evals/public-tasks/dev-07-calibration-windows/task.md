<!-- Fable Think eval task | label: DEVELOPMENT | id: dev-07-calibration-windows -->

# Task: Calibration count for a conveyor run

A conveyor is calibrated on a fixed schedule during a continuous run:

- The run is divided into consecutive **45-minute** windows starting from
  time zero.
- Each **complete** 45-minute window triggers exactly one calibration.
- After the last complete window there may be a leftover partial window at
  the end of the run. That final partial window triggers one **additional**
  calibration **if and only if it lasts at least 30 minutes** (a partial
  window of exactly 30 minutes counts; anything shorter does not).

Compute the total number of calibrations for a run that lasts **exactly 300
minutes**.

Deliver, in your answer file:

1. A short `WORKING:` section: how many complete 45-minute windows there are,
   the length of the leftover partial window, and whether it triggers an
   extra calibration.
2. A line exactly of the form
   `CALIBRATIONS: <total number of calibrations, integer>`

The summary line is parsed by a script; get the format exact.
