# DNS Reconciler for Home Assistant

HACS-compatible custom integration for keeping DNS records aligned with a Home Assistant external/WAN IP entity.

Current provider support: Cloudflare.

## Features

- Cloudflare token authentication via config flow.
- Zone and A/AAAA record discovery.
- Auto-discovery of candidate external IP source entities.
- Per-record sensor showing provider record content.
- Per-record binary sensor showing whether the record is in sync with the selected external IP entity.
- Per-record update button.
- Global "reconcile all" button.
- No IP cache required for correctness: desired state is the selected external IP entity, actual state is the provider DNS record value.

## Install via HACS custom repository

1. Add this repository as a custom integration repository in HACS.
2. Install **DNS Reconciler**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration → DNS Reconciler**.
5. Enter a narrow Cloudflare API token with DNS read/edit for the target zone.
6. Select the zone, external IP source entity, and DNS records to manage.

## Entity model

For each managed record:

- `sensor.<record>_dns_ip` — current provider record content.
- `binary_sensor.<record>_dns_in_sync` — on when provider record content matches the external IP entity.
- `button.<record>_update_dns` — manually reconcile this record.

Global:

- `button.dns_reconciler_reconcile_all` — manually reconcile all enabled managed records.

## Notes

For Cloudflare proxied records, this integration compares against the Cloudflare API record content, not public DNS resolution. This avoids false mismatches caused by Cloudflare edge IPs.
