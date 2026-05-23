from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ZONE_NAME, DOMAIN
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
        name = str(self.record_data.get("name") or self.record_id or "DNS Reconciler")
        zone_name = str(self.coordinator.entry.data.get(CONF_ZONE_NAME) or "").strip(".")
        suffix = f".{zone_name}" if zone_name else ""
        if suffix and name.endswith(suffix):
            return name[: -len(suffix)]
        return name
