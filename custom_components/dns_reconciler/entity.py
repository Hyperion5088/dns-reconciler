from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DnsReconcilerCoordinator


class DnsReconcilerEntity(CoordinatorEntity[DnsReconcilerCoordinator]):
    """Base entity for DNS Reconciler entities."""

    def __init__(self, coordinator: DnsReconcilerCoordinator, record_id: str | None = None) -> None:
        super().__init__(coordinator)
        self.record_id = record_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry.entry_id)},
            name=self.coordinator.entry.title,
            manufacturer="Hermes",
            model="DNS Reconciler",
            configuration_url="https://github.com/Hyperion5088/dns-reconciler",
        )

    @property
    def record_data(self) -> dict[str, Any]:
        if self.record_id is None or not self.coordinator.data:
            return {}
        return self.coordinator.data.get(self.record_id, {})

    @property
    def record_name(self) -> str:
        return str(self.record_data.get("name") or self.record_id or "DNS Reconciler")
