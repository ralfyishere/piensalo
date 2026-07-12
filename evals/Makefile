# Fable Think eval lab — one-command reproduction.
#
#   make benchmark   = grader self-test battery + a 2-task harness smoke run
#                      (manual adapter, probe-sourced answers, no API needed)
#
# Neither target calls a model. A real run needs a config: see
# harness/config.example.json and harness/README.md.

.PHONY: benchmark selftest smoke

benchmark: selftest smoke

selftest:
	python3 harness/grader_selftest.py

smoke:
	python3 harness/runner.py --smoke
