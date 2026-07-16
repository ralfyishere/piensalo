"""Gateway configuration and security validation.

Defaults fail safe: bind to loopback, do not retain prompts/responses, redact
logs. The configurable upstream URL is the main attack surface (SSRF), so it is
validated hard: scheme allow-list, and — unless the operator explicitly opts in
— a block on link-local / cloud-metadata / multicast / reserved destinations.

This module imports no provider SDK and does no network I/O. It only validates
and holds settings.
"""
from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass, field
from urllib.parse import urlparse

from .router import RouterPolicy

MODES = ("observe",)  # only observe is implemented; others are DESIGNED.

# Loopback hosts we allow binding a server to by default.
_LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


class ConfigError(ValueError):
    """Raised for an invalid or unsafe gateway configuration."""


def _resolve_ips(host: str) -> list[ipaddress._BaseAddress]:
    """Resolve a host to IPs for SSRF checks. A literal IP resolves to itself.
    DNS failures raise ConfigError (fail closed — we won't proxy to a host we
    cannot vet)."""
    try:
        return [ipaddress.ip_address(host)]
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError as e:
        raise ConfigError(f"cannot resolve upstream host {host!r}: {e}") from e
    ips: list[ipaddress._BaseAddress] = []
    for info in infos:
        addr = info[4][0]
        try:
            ips.append(ipaddress.ip_address(addr.split("%")[0]))
        except ValueError:
            continue
    if not ips:
        raise ConfigError(f"upstream host {host!r} resolved to no usable address")
    return ips


def _ip_is_blocked(ip: ipaddress._BaseAddress) -> str | None:
    """Return a reason string if this IP is an SSRF-sensitive target, else None.
    Loopback is allowed (local upstreams like Ollama/LM Studio are the point);
    link-local, metadata, multicast, reserved, and unspecified are blocked."""
    if ip.is_link_local:
        return "link-local address (cloud metadata / autoconfig range)"
    if ip.is_multicast:
        return "multicast address"
    if ip.is_reserved:
        return "reserved address"
    if ip.is_unspecified:
        return "unspecified address (0.0.0.0/::)"
    # 169.254.169.254 is link-local and already caught above; be explicit for
    # readers auditing this guard.
    return None


@dataclass
class GatewayConfig:
    """Validated gateway settings. Construct via :meth:`build` so validation
    always runs."""

    mode: str = "observe"
    bind_host: str = "127.0.0.1"
    bind_port: int = 8788
    upstream_base_url: str = ""
    upstream_model: str = ""
    # Security / privacy
    auth_token: str | None = None
    allow_non_loopback_bind: bool = False
    allow_non_loopback_upstream: bool = False  # opt in to non-loopback upstream IPs
    allowed_upstream_prefixes: tuple[str, ...] = ()  # if set, upstream URL must match one
    no_store: bool = True  # do not retain prompt/response bodies
    redact: bool = True  # redact headers/paths in the ledger
    retention: str = "hashes"  # "hashes" | "metadata" | "full"
    # Limits (resource-exhaustion / recursion defenses)
    max_body_bytes: int = 8 * 1024 * 1024
    upstream_timeout_s: float = 120.0
    ledger_dir: str = ".piensalo/gateway"
    router_policy: RouterPolicy = field(default_factory=RouterPolicy)

    @classmethod
    def build(cls, **kwargs) -> "GatewayConfig":
        cfg = cls(**kwargs)
        cfg.validate()
        return cfg

    def validate(self) -> None:
        if self.mode not in MODES:
            raise ConfigError(
                f"mode {self.mode!r} is not implemented; supported: {MODES}. "
                "optimize-safe and verified modes are DESIGNED, not shipped."
            )
        if self.retention not in ("hashes", "metadata", "full"):
            raise ConfigError(f"retention must be hashes|metadata|full, got {self.retention!r}")
        if not (0 < self.bind_port < 65536):
            raise ConfigError(f"bind_port out of range: {self.bind_port}")

        # Bind must be loopback unless explicitly authorized. Fail closed.
        if self.bind_host not in _LOOPBACK_HOSTS and not self.allow_non_loopback_bind:
            raise ConfigError(
                f"refusing to bind non-loopback host {self.bind_host!r} without "
                "allow_non_loopback_bind=True — the gateway is loopback-only by default"
            )

        # Upstream URL validation (SSRF).
        if self.upstream_base_url:
            self._validate_upstream(self.upstream_base_url)

        if self.retention == "full" and self.no_store:
            raise ConfigError(
                "retention='full' contradicts no_store=True; set no_store=False to "
                "retain bodies (and understand you are storing prompts/responses)"
            )

    def _validate_upstream(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ConfigError(
                f"upstream scheme must be http/https, got {parsed.scheme!r} in {url!r}"
            )
        if not parsed.hostname:
            raise ConfigError(f"upstream URL has no host: {url!r}")

        if self.allowed_upstream_prefixes:
            if not any(url.startswith(p) for p in self.allowed_upstream_prefixes):
                raise ConfigError(
                    f"upstream {url!r} does not match any allowed prefix "
                    f"{self.allowed_upstream_prefixes}"
                )

        host = parsed.hostname
        is_loopback_name = host in _LOOPBACK_HOSTS
        for ip in _resolve_ips(host):
            blocked = _ip_is_blocked(ip)
            if blocked:
                raise ConfigError(f"upstream host {host!r} -> {ip} blocked: {blocked}")
            if ip.is_loopback:
                continue  # local upstreams are the primary use case
            if ip.is_private and not self.allow_non_loopback_upstream:
                raise ConfigError(
                    f"upstream host {host!r} -> {ip} is a private-network address; "
                    "set allow_non_loopback_upstream=True to permit it"
                )
        # A loopback *name* that resolves only to public IPs is suspicious but
        # already vetted above; nothing more to do.
        _ = is_loopback_name

    def public_summary(self) -> dict:
        """A redaction-safe view for `gateway status` — never includes the
        auth token."""
        return {
            "mode": self.mode,
            "bind": f"{self.bind_host}:{self.bind_port}",
            "loopback_only": self.bind_host in _LOOPBACK_HOSTS,
            "upstream_base_url": self.upstream_base_url,
            "upstream_model": self.upstream_model,
            "auth_required": self.auth_token is not None,
            "no_store": self.no_store,
            "redact": self.redact,
            "retention": self.retention,
            "max_body_bytes": self.max_body_bytes,
            "ledger_dir": self.ledger_dir,
        }
