# FTP Connection Profile: TP-Link NAS

## Connection Details

### Public Server (remote access)
- **Host:** 130.255.9.9 (public IP of the user's home server)
- **Port:** 21
- **User:** Natanfes
- **Pass:** nat1789418
- **Server Software:** ProFTPD 1.3.4b (TP-Share)

### Local Server (LAN)
- **Host:** 192.168.0.1 (local network)
- **Port:** 21
- **User:** Natanfes
- **Pass:** nat1789418
- **Note:** Points to the same physical device. Preferred when available to avoid NAT/port-forwarding issues.

## Local Server Directory Structure

After login, root shows `/G/` as the primary storage mount:
```
/G/
├── Alarms/
├── Audiobooks/
├── DCIM/
├── Documents/
├── Download/
├── htdata/          # <- Active CakePHP project
│   ├── app/
│   │   ├── Config/
│   │   ├── Controller/
│   │   ├── Model/
│   │   └── View/
│   ├── index.php
│   ├── lib/Cake/
│   ├── plugins/
│   ├── vendors/
│   └── webroot/
├── nat/
├── Pictures/
└── Stas/
```

### Important: `G/htdata/` is already an unpacked project
If user mentions "htdata.rar" or sends an archive that's not received via chat, check `/G/htdata/` first — it may already be deployed as a live CakePHP project.

## Known Quirks

### Quirk 1: LIST shows directories, but CWD fails
Some directories appear in `LIST` output (root listing) but cannot be entered via `CWD` or `cd`. This is NOT a permissions issue — the FTP server itself denies the directory change with `550 No such file or directory` even though the directory is visible.

**Symptoms:**
- `ls G/ts-tutorial-site/` works (LIST shows files)
- `cd G/ts-tutorial-site` fails with `550 No such file or directory`
- `lftp mirror` fails with the same error

**Workaround — always use `%2f` prefix in curl paths:**
```bash
# WRONG — cd into G works, then cd into ts-tutorial-site fails
curl -u Natanfes:nat1789418 ftp://130.255.9.9/G/ts-tutorial-site/index.html

# CORRECT — use %2f (escaped /) to force absolute path from root
curl -u Natanfes:nat1789418 "ftp://130.255.9.9/%2fG/ts-tutorial-site/index.html"
```

**Why it works:** The `%2f` tells the FTP server to treat the path as absolute from the login root (`/`), bypassing the CWD issue.

**Upload with --ftp-create-dirs and %2f:**
```bash
cd /tmp/ts-site
for f in $(find . -type f); do
  curl --ftp-create-dirs -u Natanfes:nat1789418 \
    -T "$f" "ftp://130.255.9.9/%2fG/ts-tutorial-site/${f#./}"
done
```

### Quirk 2: Passive mode required
Active mode (`set ftp:passive-mode off`) causes timeouts. Always use passive mode (default in curl and lftp).

### Quirk 3: `put` and `STOR` work even when `cd` fails
Despite CWD failing, `STOR` (store file) works fine with absolute paths. This means you CAN upload files to a directory even if you can't cd into it.

### Quirk 4: No directory creation via simple `curl`
`curl` does NOT create remote directories automatically (unlike `lftp mirror`). Always use `--ftp-create-dirs` flag when uploading to subdirectories.

## Upload Recipes

### Single file
```bash
curl --ftp-create-dirs -u Natanfes:nat1789418 -T /local/file \
  "ftp://130.255.9.9/%2fG/destination/file"
```

### Entire directory (loop over find)
```bash
cd /source/dir
for f in $(find . -type f); do
  curl --ftp-create-dirs -u Natanfes:nat1789418 -T "$f" \
    "ftp://130.255.9.9/%2fG/destination/${f#./}" 2>/dev/null
done
```

## Probing
```bash
# Quick directory probe
curl -u Natanfes:nat1789418 ftp://130.255.9.9/%2fG/ 2>/dev/null

# Test write access
curl --ftp-create-dirs -u Natanfes:nat1789418 -T /dev/null \
  "ftp://130.255.9.9/%2fG/test-write/.probe" 2>/dev/null
```
