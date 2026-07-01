# Archive Merge & Yandex Disk Download Workflow

Date: 2026-06-03
Session: VIDVIS v3 — user sent `vidvis-v3.rar` via Yandex.Disk share AND `src.zip` archive

## Scenario

User sends a new version of a project in two forms simultaneously:
1. **Full project RAR** on Yandex.Disk (147 MB, includes node_modules, .next, everything)
2. **Partial source ZIP** (src/ + public/images/ only, updated components)

## Workflow

### Step 1: Download from Yandex.Disk

Public share links (`https://disk.yandex.ru/d/...`) can be downloaded directly with curl:

```bash
curl -L -o vidvis-v3.rar "https://disk.yandex.ru/d/XXXXXXXX"
```

If the shared folder is accessed via OAuth-token REST API (`https://cloud-api.yandex.net/v1/disk/...`):

```python
import requests

token = "y0_..."  # OAuth access token (NOT client_id/secret!)
headers = {"Authorization": f"OAuth {token}", "Accept": "application/json"}

# List folder contents
def list_folder(path):
    url = f"https://cloud-api.yandex.net/v1/disk/resources?path={path}\u0026limit=100"
    r = requests.get(url, headers=headers, timeout=30)
    return r.json() if r.status_code == 200 else None

# Get download link for a file
def get_download_link(path):
    url = f"https://cloud-api.yandex.net/v1/disk/resources/download?path={path}"
    r = requests.get(url, headers=headers, timeout=30)
    return r.json().get("href") if r.status_code == 200 else None

# Download the actual file
r = requests.get(href, stream=True, timeout=120)
with open("file.rar", "wb") as f:
    for chunk in r.iter_content(65536):
        if chunk:
            f.write(chunk)
```

**Critical:** Client credentials (`client_id`/`client_secret`) alone are worthless for API access. You need an **OAuth access_token** (starts with `y0_`) obtained via browser flow or from the user's share link.

### Step 2: Extract RAR

```bash
# Pre-installed unrar (most distros)
unrar x -o+ archive.rar /dest/path

# If unrar is not available (custom build)
mkdir -p ~/bin
curl -sL "http://www.rarlab.com/rar/rarlinux-x64-612.tar.gz" -o rar.tar.gz
tar xzf rar.tar.gz -C ~/bin
~/bin/rar/unrar x -o+ archive.rar /dest/path
```

### Step 3: Merge with User Source Updates

User's `src.zip` often contains newer/updated components but NOT custom components built by the agent (e.g., PerspectiveScene, ParallaxDivider).

**ALWAYS ask before overwriting.** Prefer selective merge:

```bash
# Unzip user archive to temp
unzip -o src.zip -d /tmp/user_src

# Compare file sizes (newer code = usually different size)
for f in /tmp/user_src/src/components/*.tsx; do
    name=$(basename "$f")
    if [ -f "/current/project/src/components/$name" ]; then
        echo "$name: current=$(wc -c < "/current/project/src/components/$name") user=$(wc -c < "$f")"
    else
        echo "$name: NEW FILE"
    fi
done
```

**Components likely in user's archive (overwrite):**
- Hero.tsx, ArtGallery.tsx, HomeTextile.tsx, Products.tsx, Footer.tsx
- globals.css, layout.tsx, page.tsx
- useLenis.ts

**Components likely NOT in user's archive (preserve):**
- PerspectiveScene.tsx (agent-built 3D scene)
- ParallaxDivider.tsx (agent-built reusable divider)
- Preloader.tsx (agent-built)
- Navigation.tsx, MagneticCursor.tsx (standard but may be customized)

### Step 4: Fix External Image URLs

User's components often use external URLs (Unsplash, wallpaperscraft). ALWAYS check components after merge:

```bash
grep -rn "https://" src/components/*.tsx
```

Replace any external `<Image>` sources with local JPGs from `public/images/`:

```tsx
// Before (external — causes next/image error if not in remotePatterns)
<img src="https://images.unsplash.com/photo-xxx?w=800\u0026q=80" />

// After (local — zero config needed)
<Image src="/images/nature_1.jpg" fill className="object-cover" sizes="400px" />
```

Local images are **always preferred** for production builds:
- No external dependency
- Works offline
- Faster (no DNS resolution)
- No CORS / remotePatterns configuration needed

## Key Lessons

1. **Do NOT blind-overwrite custom components.** Ask the user what changed.
2. **ALWAYS check for external URLs after merging code from user archives.** Replace with local assets.
3. **Yandex.Disk RAR files can be large (147 MB).** Extracting with `unrar` may take 2-3 minutes.
4. **node_modules included in user RAR = skip npm install.** The node_modules from their machine may be outdated or wrong for the current environment.
5. **Delete node_modules and rebuild** (npm install clean) when merging large archives with dependencies.
