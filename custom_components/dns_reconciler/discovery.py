from __future__ import annotations

import ipaddress

from homeassistant.core import HomeAssistant

BAD_ENTITY_HINTS = (
    "certificate",
    "response_time",
    "uptime",
    "monitor_type",
    "monitored_hostname",
    "monitored_url",
    "status",
    "dns_response",
    "ping",
)
GOOD_HINTS = ("wan", "wan_ip", "ip_wan", "public_ip", "external_ip", "internet_ip", "external", "public")
BEST_PLATFORM_HINTS = ("unifi_network_infrastructure", "unifi", "udm", "router", "gateway")


def is_global_ip(value: str) -> bool:
    try:
        return ipaddress.ip_address(value).is_global
    except ValueError:
        return False


def discover_external_ip_entities(hass: HomeAssistant) -> list[tuple[str, str]]:
    """Return candidate entity ids and labels, best first."""
    candidates: list[tuple[int, str, str]] = []
    for state in hass.states.async_all("sensor"):
        entity_id = state.entity_id
        attrs = state.attributes
        name = str(attrs.get("friendly_name") or entity_id)
        haystack = f"{entity_id} {name}".lower()
        value = str(state.state or "").strip()

        if not is_global_ip(value):
            continue
        if any(hint in haystack for hint in BAD_ENTITY_HINTS):
            continue
        if not any(hint in haystack for hint in GOOD_HINTS):
            continue

        score = 0
        if "wan" in haystack:
            score += 50
        if "ip_wan" in haystack or "wan_ip" in haystack:
            score += 30
        if "unifi" in haystack or "udm" in haystack:
            score += 30
        if any(hint in haystack for hint in BEST_PLATFORM_HINTS):
            score += 20
        if "net_router" in haystack or "router" in haystack:
            score += 15
        if "public_ip" in haystack or "external_ip" in haystack:
            score += 10
        candidates.append((-score, entity_id, name))

    candidates.sort()
    return [(entity_id, f"{name} ({entity_id})") for _, entity_id, name in candidates]
