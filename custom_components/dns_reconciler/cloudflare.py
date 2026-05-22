from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp

API_BASE = "https://api.cloudflare.com/client/v4"


class CloudflareError(Exception):
    """Cloudflare API error."""


@dataclass(slots=True)
class DnsRecord:
    id: str
    name: str
    type: str
    content: str
    proxied: bool | None = None
    ttl: int | None = None

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> "DnsRecord":
        return cls(
            id=raw["id"],
            name=raw["name"],
            type=raw["type"],
            content=raw.get("content", ""),
            proxied=raw.get("proxied"),
            ttl=raw.get("ttl"),
        )


class CloudflareClient:
    def __init__(self, session: aiohttp.ClientSession, token: str) -> None:
        self._session = session
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        async with self._session.request(method, f"{API_BASE}{path}", headers=self._headers, **kwargs) as resp:
            payload = await resp.json(content_type=None)
            if resp.status >= 400 or not payload.get("success", False):
                errors = payload.get("errors") or []
                message = "; ".join(str(e.get("message", e)) for e in errors) or f"HTTP {resp.status}"
                raise CloudflareError(message)
            return payload.get("result")

    async def verify_token(self) -> None:
        await self._request("GET", "/user/tokens/verify")

    async def zones(self) -> list[dict[str, Any]]:
        return await self._request("GET", "/zones?per_page=50")

    async def dns_records(self, zone_id: str) -> list[DnsRecord]:
        records: list[DnsRecord] = []
        for record_type in ("A", "AAAA"):
            result = await self._request("GET", f"/zones/{zone_id}/dns_records?type={record_type}&per_page=100")
            records.extend(DnsRecord.from_api(item) for item in result)
        records.sort(key=lambda r: (r.name, r.type))
        return records

    async def dns_record(self, zone_id: str, record_id: str) -> DnsRecord:
        result = await self._request("GET", f"/zones/{zone_id}/dns_records/{record_id}")
        return DnsRecord.from_api(result)

    async def update_record_content(self, zone_id: str, record: DnsRecord, content: str) -> DnsRecord:
        payload: dict[str, Any] = {
            "type": record.type,
            "name": record.name,
            "content": content,
        }
        if record.ttl is not None:
            payload["ttl"] = record.ttl
        if record.proxied is not None:
            payload["proxied"] = record.proxied
        result = await self._request("PATCH", f"/zones/{zone_id}/dns_records/{record.id}", json=payload)
        return DnsRecord.from_api(result)
