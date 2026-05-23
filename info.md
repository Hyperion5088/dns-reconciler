# DNS Reconciler

![DNS Reconciler logo](logo.png)

Home Assistant custom integration for reconciling selected Cloudflare DNS records against your current external/WAN IP.

## Highlights

- HACS-compatible custom integration.
- Cloudflare zone and A/AAAA record discovery.
- UniFi/UDM WAN IP sensor auto-discovery.
- Optional public IP web-service fallback.
- Optional auto-sync when Cloudflare is out of sync.
- Per-record DNS IP, in-sync, and update-button entities.
- Global **Reconcile All** button.

## Setup

After installing through HACS and restarting Home Assistant:

1. Add **DNS Reconciler** from **Settings → Devices & services**.
2. Enter a Cloudflare API token with DNS read/edit for the zone.
3. Select the zone and records to manage.
4. Select an external IP entity, or enable public IP fallback.
5. Enable auto-sync if Cloudflare should be updated automatically.
