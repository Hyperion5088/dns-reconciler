from types import SimpleNamespace

from custom_components.dns_reconciler.discovery import discover_external_ip_entities


class States:
    def __init__(self, states):
        self._states = states

    def async_all(self, domain):
        return self._states if domain == "sensor" else []


def state(entity_id, value, name):
    return SimpleNamespace(entity_id=entity_id, state=value, attributes={"friendly_name": name})


def test_unifi_wan_ip_is_best_external_ip_candidate():
    hass = SimpleNamespace(states=States([
        state("sensor.random_public_ip", "8.8.8.8", "Random Public IP"),
        state("sensor.udm_pro_wan_ip", "217.43.36.165", "UniFi WAN IP"),
    ]))

    candidates = discover_external_ip_entities(hass)

    assert candidates[0][0] == "sensor.udm_pro_wan_ip"
