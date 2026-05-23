from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DnsReconcilerCoordinator
from .entity import DnsReconcilerEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: DnsReconcilerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DnsRecordIpSensor(coordinator, rid) for rid in coordinator.managed_record_ids])


class DnsRecordIpSensor(DnsReconcilerEntity, SensorEntity):
    _attr_icon = "mdi:dns"

    def __init__(self, coordinator: DnsReconcilerCoordinator, record_id: str) -> None:
        super().__init__(coordinator, record_id)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{record_id}_dns_ip"

    @property
    def name(self) -> str:
        return f"{self.record_name} DNS IP"

    @property
    def native_value(self):
        return self.record_data.get("content")

    @property
    def extra_state_attributes(self):
        return {
            "record_id": self.record_id,
            "record_name": self.record_data.get("name"),
            "record_type": self.record_data.get("type"),
            "proxied": self.record_data.get("proxied"),
            "ttl": self.record_data.get("ttl"),
            "desired_ip_entity": self.coordinator.external_ip_entity,
            "desired_ip": self.record_data.get("desired_ip"),
            "in_sync": self.record_data.get("in_sync"),
            "error": self.record_data.get("error"),
        }
