# Chaptarr for Home Assistant

A custom integration for [Chaptarr](https://chaptarr.com) (a Readarr fork for ebooks and audiobooks). It talks to Chaptarr's Readarr-style `/api/v1` API.

## Entities

| Entity | Description |
|---|---|
| `sensor.chaptarr_queue` | Number of items in the download queue. Each book appears as an attribute (`Author – Title: 42.0%`), and `import_blocked` counts the items stuck at import. |
| `sensor.chaptarr_wanted` | Total number of wanted/missing books |
| `binary_sensor.chaptarr_health` | On when Chaptarr reports health issues; each issue is an attribute |
| `calendar.chaptarr` | Book release dates (all-day events) |

The integration polls every 60 seconds. The queue sensor's attributes are not recorded, so large queues don't bloat the database.

## Installation

### HACS
1. HACS → ⋮ → **Custom repositories** → add `https://github.com/Luca-Bachini-Barr/ha-chaptarr` as an **Integration**.
2. Install **Chaptarr**, then restart Home Assistant.

### Manual
Copy `custom_components/chaptarr` into your Home Assistant `custom_components` folder and restart.

## Configuration
**Settings → Devices & services → Add integration → Chaptarr**, then enter:
- **URL**: e.g. `http://192.168.1.60:8789`
- **API key**: from Chaptarr → Settings → General → Security

## Example dashboard card
This card lists active downloads and hides imports that are blocked:

```yaml
type: markdown
content: >-
  {% set ns = namespace(rows=[]) %}
  {% for k, v in states.sensor.chaptarr_queue.attributes.items()
     if k not in ['unit_of_measurement','friendly_name','icon','state_class','import_blocked']
     and 'importBlocked' not in v %}
  {% set ns.rows = ns.rows + ['| ' ~ k ~ ' | ' ~ v ~ ' |'] %}{% endfor %}
  {% if ns.rows %}| Book | Progress |
  |:--|--:|
  {{ ns.rows | sort | join('\n') }}{% else %}Nothing downloading.{% endif %}
```
