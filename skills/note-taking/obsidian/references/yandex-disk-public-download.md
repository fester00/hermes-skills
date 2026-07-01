# Downloading public Yandex.Disk links via API

Direct HTTP GET to `https://disk.yandex.ru/d/<key>` returns a captcha page from server-side.
Use the Yandex.Disk public resources API instead.

## Fetch file metadata

```bash
PUBLIC_URL="https://disk.yandex.ru/d/bU4CEPAf5kjFcA"
curl -s "https://cloud-api.yandex.net/v1/disk/public/resources?public_key=${PUBLIC_URL}"
```

Response is JSON. For directories, `_embedded.items` lists files.
For a single file, `file` field contains the direct download URL.

## Extract direct download URL

```bash
# For a single file
curl -s "https://cloud-api.yandex.net/v1/disk/public/resources?public_key=${PUBLIC_URL}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file',''))"

# For a directory: list files, pick first
curl -s "https://cloud-api.yandex.net/v1/disk/public/resources?public_key=${PUBLIC_URL}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); items=d.get('_embedded',{}).get('items',[]); [print(i['file']) for i in items if 'file' in i]"
```

## Download

```bash
curl -sL -o archive.zip "<direct_url_from_above>"
```

## Notes
- No API token required for public links.
- Direct URLs are signed and time-limited; fetch metadata just before downloading.
- For large directories, add `&limit=100` or paginate with `offset=`.
