from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .cloudflare import CloudflareClient, CloudflareError, DnsRecord
from .const import (
    CONF_EXTERNAL_IP_ENTITY,
    CONF_PUBLIC_IP_URL,
    CONF_USE_PUBLIC_IP_FALLBACK,
    CONF_AUTO_SYNC,
    CONF_PROVIDER,
    CONF_RECORD_IDS,
    CONF_TOKEN,
    CONF_ZONE_ID,
    CONF_ZONE_NAME,
    DOMAIN,
    DEFAULT_PUBLIC_IP_URL,
    PROVIDER_CLOUDFLARE,
)
from .discovery import discover_external_ip_entities


class DnsReconcilerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._token: str | None = None
        self._zones: list[dict[str, Any]] = []
        self._zone_id: str | None = None
        self._zone_name: str | None = None
        self._records: list[DnsRecord] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            self._token = user_input[CONF_TOKEN]
            client = CloudflareClient(async_get_clientsession(self.hass), self._token)
            try:
                await client.verify_token()
                self._zones = await client.zones()
                return await self.async_step_zone()
            except CloudflareError:
                errors["base"] = "auth_failed"

        schema = vol.Schema({vol.Required(CONF_TOKEN): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_zone(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            self._zone_id = user_input[CONF_ZONE_ID]
            zone = next((z for z in self._zones if z["id"] == self._zone_id), None)
            self._zone_name = zone.get("name") if zone else self._zone_id
            client = CloudflareClient(async_get_clientsession(self.hass), self._token or "")
            try:
                self._records = await client.dns_records(self._zone_id)
                return await self.async_step_records()
            except CloudflareError:
                errors["base"] = "records_failed"

        options = {z["id"]: z.get("name", z["id"]) for z in self._zones}
        schema = vol.Schema({vol.Required(CONF_ZONE_ID): vol.In(options)})
        return self.async_show_form(step_id="zone", data_schema=schema, errors=errors)

    async def async_step_records(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        candidates = discover_external_ip_entities(self.hass)
        default_external = candidates[0][0] if candidates else ""

        if user_input is not None:
            record_ids = user_input.get(CONF_RECORD_IDS, [])
            if not record_ids:
                errors[CONF_RECORD_IDS] = "no_records"
            else:
                title = f"DNS Reconciler ({self._zone_name})"
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_PROVIDER: PROVIDER_CLOUDFLARE,
                        CONF_TOKEN: self._token,
                        CONF_ZONE_ID: self._zone_id,
                        CONF_ZONE_NAME: self._zone_name,
                        CONF_EXTERNAL_IP_ENTITY: user_input.get(CONF_EXTERNAL_IP_ENTITY, ""),
                        CONF_USE_PUBLIC_IP_FALLBACK: user_input.get(CONF_USE_PUBLIC_IP_FALLBACK, True),
                        CONF_PUBLIC_IP_URL: user_input.get(CONF_PUBLIC_IP_URL, DEFAULT_PUBLIC_IP_URL),
                        CONF_AUTO_SYNC: user_input.get(CONF_AUTO_SYNC, False),
                        CONF_RECORD_IDS: record_ids,
                    },
                )

        record_options = {r.id: f"{r.name} ({r.type}) -> {r.content}" for r in self._records}
        schema = vol.Schema({
            vol.Optional(CONF_EXTERNAL_IP_ENTITY, default=default_external): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Optional(CONF_USE_PUBLIC_IP_FALLBACK, default=True): selector.BooleanSelector(),
            vol.Optional(CONF_PUBLIC_IP_URL, default=DEFAULT_PUBLIC_IP_URL): str,
            vol.Optional(CONF_AUTO_SYNC, default=False): selector.BooleanSelector(),
            vol.Required(CONF_RECORD_IDS): selector.SelectSelector(selector.SelectSelectorConfig(
                options=[{"value": key, "label": label} for key, label in record_options.items()],
                multiple=True,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )),
        })
        return self.async_show_form(step_id="records", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return DnsReconcilerOptionsFlow(config_entry)


class DnsReconcilerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry
        self._records: list[DnsRecord] = []

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        client = CloudflareClient(async_get_clientsession(self.hass), self.entry.data[CONF_TOKEN])
        if not self._records:
            try:
                self._records = await client.dns_records(self.entry.data[CONF_ZONE_ID])
            except CloudflareError:
                errors["base"] = "records_failed"
        candidates = discover_external_ip_entities(self.hass)
        current_external = self.entry.options.get(CONF_EXTERNAL_IP_ENTITY, self.entry.data.get(CONF_EXTERNAL_IP_ENTITY, ""))
        current_public_url = self.entry.options.get(CONF_PUBLIC_IP_URL, self.entry.data.get(CONF_PUBLIC_IP_URL, DEFAULT_PUBLIC_IP_URL))
        current_use_fallback = self.entry.options.get(
            CONF_USE_PUBLIC_IP_FALLBACK,
            self.entry.data.get(CONF_USE_PUBLIC_IP_FALLBACK, True),
        )
        current_auto_sync = self.entry.options.get(CONF_AUTO_SYNC, self.entry.data.get(CONF_AUTO_SYNC, False))
        if not current_external and candidates:
            current_external = candidates[0][0]

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        record_options = {r.id: f"{r.name} ({r.type}) -> {r.content}" for r in self._records}
        current_records = self.entry.options.get(CONF_RECORD_IDS, self.entry.data.get(CONF_RECORD_IDS, []))
        schema = vol.Schema({
            vol.Optional(CONF_EXTERNAL_IP_ENTITY, default=current_external): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Optional(CONF_USE_PUBLIC_IP_FALLBACK, default=current_use_fallback): selector.BooleanSelector(),
            vol.Optional(CONF_PUBLIC_IP_URL, default=current_public_url): str,
            vol.Optional(CONF_AUTO_SYNC, default=current_auto_sync): selector.BooleanSelector(),
            vol.Required(CONF_RECORD_IDS, default=current_records): selector.SelectSelector(selector.SelectSelectorConfig(
                options=[{"value": key, "label": label} for key, label in record_options.items()],
                multiple=True,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )),
        })
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
