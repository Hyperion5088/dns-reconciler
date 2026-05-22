from __future__ import annotations

from datetime import timedelta
import ipaddress
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .cloudflare import CloudflareClient, CloudflareError, DnsRecord
from .const import CONF_EXTERNAL_IP_ENTITY, CONF_RECORD_IDS, CONF_TOKEN, CONF_ZONE_ID, UPDATE_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)


class DnsReconcilerCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="DNS Reconciler",
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )
        self.entry = entry
        self.client = CloudflareClient(async_get_clientsession(hass), entry.data[CONF_TOKEN])
        self.zone_id = entry.data[CONF_ZONE_ID]

    @property
    def external_ip_entity(self) -> str:
        return self.entry.options.get(CONF_EXTERNAL_IP_ENTITY, self.entry.data.get(CONF_EXTERNAL_IP_ENTITY, ""))

    @property
    def managed_record_ids(self) -> list[str]:
        return list(self.entry.options.get(CONF_RECORD_IDS, self.entry.data.get(CONF_RECORD_IDS, [])))

    def external_ip(self) -> str | None:
        state = self.hass.states.get(self.external_ip_entity)
        if state is None:
            return None
        value = str(state.state or "").strip()
        try:
            ip = ipaddress.ip_address(value)
        except ValueError:
            return None
        return str(ip) if ip.is_global else None

    async def _async_update_data(self) -> dict[str, dict]:
        desired_ip = self.external_ip()
        data: dict[str, dict] = {}
        for record_id in self.managed_record_ids:
            try:
                record = await self.client.dns_record(self.zone_id, record_id)
                data[record_id] = self._record_data(record, desired_ip)
            except CloudflareError as err:
                data[record_id] = {"record_id": record_id, "error": str(err), "desired_ip": desired_ip}
        return data

    def _record_data(self, record: DnsRecord, desired_ip: str | None, *, updated: bool = False) -> dict:
        return {
            "record_id": record.id,
            "name": record.name,
            "type": record.type,
            "content": record.content,
            "proxied": record.proxied,
            "ttl": record.ttl,
            "desired_ip": desired_ip,
            "in_sync": bool(desired_ip and record.content == desired_ip),
            "updated": updated,
            "error": None,
        }

    async def async_reconcile_record(self, record_id: str) -> None:
        desired_ip = self.external_ip()
        if not desired_ip:
            raise CloudflareError(f"External IP entity {self.external_ip_entity} is missing or not a global IP")
        record = await self.client.dns_record(self.zone_id, record_id)
        if record.content != desired_ip:
            record = await self.client.update_record_content(self.zone_id, record, desired_ip)
            _LOGGER.info("Updated DNS record %s (%s) to current external IP", record.name, record.type)
        await self.async_request_refresh()

    async def async_reconcile_all(self) -> None:
        for record_id in self.managed_record_ids:
            await self.async_reconcile_record(record_id)
