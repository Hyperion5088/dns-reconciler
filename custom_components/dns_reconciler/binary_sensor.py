from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DnsReconcilerCoordinator
from .entity import DnsReconcilerEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: DnsReconcilerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DnsRecordInSyncBinarySensor(coordinator, rid) for rid in coordinator.managed_record_ids])


class DnsRecordInSyncBinarySensor(DnsReconcilerEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: DnsReconcilerCoordinator, record_id: str) -> None:
        super().__init__(coordinator, record_id)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{record_id}_dns_in_sync"

    @property
    def name(self) -> str:
        return f"{self.record_name} DNS In Sync"

    @property
    def is_on(self) -> bool | None:
        if self.record_data.get("error"):
            return False
        return self.record_data.get("in_sync")

    @property
    def extra_state_attributes(self):
        return {
            "record_id": self.record_id,
            "record_name": self.record_data.get("name"),
            "desired_ip_entity": self.coordinator.external_ip_entity,
            "desired_ip": self.record_data.get("desired_ip"),
            "error": self.record_data.get("error"),
        }
