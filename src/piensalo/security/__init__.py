"""piensalo.security — hygiene scanning for skill directories.

Third-party skill text is untrusted input: it is read into a model's
context and can carry instructions the operator never wrote. ``skill_scan``
performs a static sweep of a skill directory for the known hazard classes
before a skill is installed or exported.
"""
from piensalo.security.skill_scan import scan_skill_dir

__all__ = ["scan_skill_dir"]
