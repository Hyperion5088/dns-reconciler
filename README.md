# DNS Reconciler for Home Assistant

![DNS Reconciler logo](logo.png)

HACS-compatible Home Assistant custom integration for keeping selected Cloudflare DNS records aligned with your current external/WAN IP.

Current provider support: **Cloudflare**.

## Features

- Visual config flow; no YAML required.
- Cloudflare token authentication.
- Zone and A/AAAA record discovery.
- Auto-discovery of likely external IP sensors, including UniFi/UDM WAN IP entities.
- Optional public IP web-service fallback when no selected entity is valid.
- Optional auto-sync: update Cloudflare only when a managed record is out of sync.
- Per-record entities:
  - current DNS IP sensor
  - DNS in-sync binary sensor
  - manual update button
- Global **Reconcile All** button.
- HACS branding assets included with `icon.png` in the repository root.

## Install via HACS custom repository

1. In HACS, add this repository as a custom repository.
2. Category: **Integration**.
3. Install **DNS Reconciler**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration → DNS Reconciler**.
6. Enter a narrow Cloudflare API token with DNS read/edit for the target zone.
7. Select the zone and DNS records to manage.
8. Choose an external/WAN IP entity, or enable the public IP fallback.
9. Enable auto-sync if you want Cloudflare updated automatically when out of sync.

Repository URL:

`https://github.com/Hyperion5088/dns-reconciler`

## Options

After setup, open the integration options to change:

- External IP entity
- Public IP fallback enabled/disabled
- Public IP fallback URL
- Auto-sync enabled/disabled
- Managed DNS records

## Entity model

For each managed record:

- `sensor.<record>_dns_ip` — current Cloudflare record content.
- `binary_sensor.<record>_dns_in_sync` — on when Cloudflare matches the desired external IP.
- `button.<record>_update_dns` — manually reconcile this record.

Global:

- `button.<integration>_reconcile_all` — manually reconcile all managed records.

## Auto-sync behavior

When auto-sync is enabled, the integration checks every 15 minutes.

It updates Cloudflare only when:

- a valid desired external IP is available, and
- the Cloudflare record content differs from that IP.

If the record is already correct, no Cloudflare update is sent.

## Notes

For Cloudflare proxied records, this integration compares against the Cloudflare API record content, not public DNS resolution. This avoids false mismatches caused by Cloudflare edge IPs.
