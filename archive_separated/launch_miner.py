"""Archived mining launcher; intentionally disabled.

The former implementation contained hard-coded pool credentials and network
mining behavior. Keep credentials out of source control and do not execute
archived launchers.
"""

raise RuntimeError("Archived mining launcher disabled; use a reviewed implementation with environment-based secrets.")
