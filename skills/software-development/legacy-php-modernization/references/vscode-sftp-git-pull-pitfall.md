# VS Code SFTP + git pull pitfall

## Context

Legacy PHP cabinets (e.g. LigaLink ZF1 subscriber cabinet at `my.ligalink.ru/user/`) are edited locally in VS Code and deployed to production via an SFTP extension that auto-uploads files on save.

## The pitfall

VS Code SFTP extensions typically trigger upload only when a file is **saved inside the editor window**. They do **not** detect external changes made by `git pull` or by another process.

Result: after pulling teammate commits, some files are updated locally but not on the server. The symptom is a partially-deployed change — e.g. a view template references a new variable (`$this->passportAlert`), but the controller that sets it was never uploaded.

## Reproduction recipe

1. Teammate pushes a change touching both `IndexController.php` and `index.phtml`.
2. Locally: `git pull origin master`.
3. Open only `index.phtml` and save it → SFTP uploads the view.
4. `IndexController.php` is still the old version on the server.
5. Page renders without errors, but the new alert/variable never appears.

## Correct workflow

```bash
# Pull latest commits
cd /path/to/project
git pull origin master
```

Then in VS Code:

- **Ctrl+Shift+P → `SFTP: Sync Local to Remote`** (command name depends on extension)
- Or manually open every changed file and press **Ctrl+S**.

After sync, verify on the server:

```bash
ssh user@server
md5sum /path/to/project/application/modules/billing/controllers/IndexController.php
cd /path/to/local/project && md5sum application/modules/billing/controllers/IndexController.php
```

If hashes match, the file is deployed.

## OPcache note

If PHP OPcache is enabled, reload the PHP process after deploy:

```bash
sudo service php5-fpm reload
# or
sudo service php7-fpm reload
# or
sudo service apache2 reload
```

## Reference command palette names by extension

- `SFTP: Sync Local to Remote` (common for VS Code SFTP / liximomo)
- `Remote FS: Upload` (alternative extensions)

If the extension does not expose a bulk sync command, the only reliable method is to open and save each changed file.

## Related

- `legacy-php-modernization/SKILL.md` — Legacy ZF1 Cabinet Maintenance section
