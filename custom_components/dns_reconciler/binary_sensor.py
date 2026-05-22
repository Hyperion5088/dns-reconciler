from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DnsReconcilerCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: DnsReconcilerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(DnsRecordInSyncBinarySensor(coordinator, rid) for rid in coordinator.managed_record_ids)


class DnsRecordInSyncBinarySensor(CoordinatorEntity[DnsReconcilerCoordinator], BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: DnsReconcilerCoordinator, record_id: str) -> None:
        super().__init__(coordinator)
        self.record_id = record_id
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{record_id}_dns_in_sync"

    @property
    def name(self) -> str:
        data = self.coordinator.data.get(self.record_id, {}) if self.coordinator.data else {}
        return f"{data.get('name', self.record_id)} DNS In Sync"

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data.get(self.record_id, {}) if self.coordinator.data else {}
        if data.get("error"):
            return False
        return data.get("in_sync")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self.record_id, {}) if self.coordinator.data else {}
        return {"desired_ip_entity": self.coordinator.external_ip_entity, "error": data.get("error")}
