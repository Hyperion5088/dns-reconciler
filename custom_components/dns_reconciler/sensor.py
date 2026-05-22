from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DnsReconcilerCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: DnsReconcilerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(DnsRecordIpSensor(coordinator, rid) for rid in coordinator.managed_record_ids)


class DnsRecordIpSensor(CoordinatorEntity[DnsReconcilerCoordinator], SensorEntity):
    _attr_icon = "mdi:dns"

    def __init__(self, coordinator: DnsReconcilerCoordinator, record_id: str) -> None:
        super().__init__(coordinator)
        self.record_id = record_id
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{record_id}_dns_ip"

    @property
    def name(self) -> str:
        data = self.coordinator.data.get(self.record_id, {}) if self.coordinator.data else {}
        return f"{data.get('name', self.record_id)} DNS IP"

    @property
    def native_value(self):
        data = self.coordinator.data.get(self.record_id, {}) if self.coordinator.data else {}
        return data.get("content")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self.record_id, {}) if self.coordinator.data else {}
        return {
            "record_id": self.record_id,
            "record_name": data.get("name"),
            "record_type": data.get("type"),
            "proxied": data.get("proxied"),
            "ttl": data.get("ttl"),
            "desired_ip_entity": self.coordinator.external_ip_entity,
            "in_sync": data.get("in_sync"),
            "error": data.get("error"),
        }
