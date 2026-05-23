from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DnsReconcilerCoordinator
from .entity import DnsReconcilerEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: DnsReconcilerCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[ButtonEntity] = [DnsReconcileAllButton(coordinator)]
    entities.extend(DnsRecordUpdateButton(coordinator, rid) for rid in coordinator.managed_record_ids)
    async_add_entities(entities)


class DnsRecordUpdateButton(DnsReconcilerEntity, ButtonEntity):
    _attr_icon = "mdi:cloud-sync"

    def __init__(self, coordinator: DnsReconcilerCoordinator, record_id: str) -> None:
        super().__init__(coordinator, record_id)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{record_id}_update_dns"

    @property
    def name(self) -> str:
        return f"Update {self.record_name} DNS"

    async def async_press(self) -> None:
        await self.coordinator.async_reconcile_record(self.record_id or "")


class DnsReconcileAllButton(DnsReconcilerEntity, ButtonEntity):
    _attr_icon = "mdi:cloud-sync-outline"

    def __init__(self, coordinator: DnsReconcilerCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_reconcile_all"
        self._attr_name = "Reconcile All"

    async def async_press(self) -> None:
        await self.coordinator.async_reconcile_all()
