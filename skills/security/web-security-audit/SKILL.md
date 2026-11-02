---
name: web-security-audit
description: Use when pentesting or auditing a live web site.
version: 1.0.0
author: Hermes Agent + Natan
license: MIT
metadata:
  hermes:
    tags: [security, pentest, audit, cve, wordpress, tls, recon, reporting]
    related_skills: [five-stages, verifying-live-service-changes, code-quality-gates]
---

# Web security audit (black-box)

The owner says «проведи пентест» / «проверь безопасность сайта» / drops a scanner list with CVE IDs. What he
wants back is not a wall of theory: it is verified findings with the command and the observed value behind each
one, the false positives named out loud, a report file, and a fix plan he can approve.

Run it inside `five-stages`: **a read-only audit is stages 1 and 5** — build, crawl, measure, report; no plan
gate, because nothing on disk changes. The moment he says «убери/исправь», that item goes back through stage 2
(plan file, explicit «go»). Say in the first line which stage you are in.

Depth lives in the references: CVE verification and applicability → `references/cve-verification.md`;
WordPress surface checklist and hardening snippets → `references/wordpress-blackbox.md`; the re-runnable probe
sweep → `scripts/wp-blackbox-recon.sh`.

## When to Use

- «Проведи пентест / проверь безопасность сайта» — any live HTTP service the owner points at.
- The owner pastes a scanner result or a CVE list and asks «что это / можешь что-то придумать».
- A site or service is about to be handed over, launched, or accepted from a contractor and needs a security
  baseline before it is signed off.
- An unfamiliar CVE ID lands in chat and needs a real verdict: vendor, affected ranges, fixed version, and
  whether it touches our stack at all — `references/cve-verification.md` is enough on its own for that.
- Not for source-code review of an application you have locally (`code-quality-gates`), and not for auditing a
  knowledge base or skill library (`knowledge-base-audit`).

## Hard rules before the first active probe

- **Audit only what the owner owns or has written permission for.** Evidence of ownership: the site's repo on
  this machine, a DB dump of it, admin/panel access. If ownership is unclear, do passive recon (DNS, headers,
  certificate, public files) while you ask — never the active part.
- **Non-destructive by default.** No exploitation payloads, no password brute force, no injection fuzzing, no
  file writes, no state-changing requests. Prove a capability with the smallest observable signal: a fault
  response, a 401, a status code, a version number.
- **Never aim a pingback/SSRF at a third-party host.** That points the owner's server at somebody else — a
  criminal act done with his IP. Point any SSRF probe at the target itself or do not run it.
- **Exploitation is a separate mandate.** «Проведи пентест» means measure and prove reachability; running an
  actual exploit that changes state needs its own approval and a backup window. Offer it as a next step.

## Procedure

### 1. Verify the claimed CVEs first — before any opinion about the site

For every ID the owner brings: `https://cveawg.mitre.org/api/cve/<CVE-ID>` (snippet in the reference).
Read vendor, product, affected version ranges, CVSS, fixed versions. Then answer three questions:

1. Is the vendor/product the same class of software the target actually runs?
2. Is the installed version inside an affected range?
3. If not — is the scanned host even running that product? Check its paths and subdomains before saying so.

A CVE whose vendor is a different product than the target's stack is a **scanner false positive**: name it, show
why, and do not map it onto the site. Report the record's real CVSS too — a scanner list carries the wrong number
often enough that it is worth quoting.

### 2. Establish what actually serves the domain

The live site is frequently **not** the repository sitting in the home directory: a redesign can be finished and
never deployed. Read the truth from the wire — `server`, `x-powered-by`, `<meta name="generator">`, certificate
issuer, `<link rel="https://api.w.org/">`, rest-api namespaces. If prod is a different codebase, say it in one
line at the top of the report, and audit what is actually serving.

### 3. Fingerprint and inventory with versions

A version without a number is not a finding. Get concrete versions for the core, theme and every extension, then
list them in a table «установлено → актуальная ветка». Cheap external sources per stack are in the references
(for WordPress: `readme.txt` `Stable tag`, rest namespaces, generator meta).

### 4. Map versions to CVEs, then decide applicability honestly

NVD `virtualMatchString` on a CPE gives every CVE whose range covers the installed version; `keywordSearch` finds
plugin records NVD indexes only by vendor name. Decide applicability **by the version range in the CVE record**,
not by the CPE hit alone. Two caveats that must appear in the report:

- Old branches of a widely deployed product receive security **backports**, so a CPE match overstates. Downgrade
  such a claim to «применимость требует проверки на сервере» and name the server-side check.
- Findings that need an authenticated session are **confirmed by version, not by exploitation**. Write exactly
  that; do not imply you executed them.

### 5. Test transport and response configuration

Minimum TLS version, cipher, HSTS and the other security headers, cookie flags, HTTP→HTTPS redirect, server
banner. Force old TLS explicitly — see the pitfall below, the naive command lies.

### 6. Probe the unauthenticated surface with status codes only

Exposed entry points, backup directories, listing, install/upgrade scripts, debug logs, `.env`/`.git`, rest
namespaces, legacy RPC endpoints, cookie flags, robots.txt announcements. Record `code + size` per path in a
table; a 403 on a directory means «exists but no listing», not «absent» — say which one it is.

### 7. Report, then the plan

- **Report** (Russian, evidence-first) → vault `Operations/` named `Аудит — безопасность <host> (<date>).md`.
  Structure: what was checked and when → the claimed-CVE verdict → component inventory table → findings by
  severity, each with the observed value/command → «что проверено и в порядке» (so nobody re-fixes working
  things) → priorities → limitations of the audit.
- **Plan** (fixes) → `~/.hermes/plans/<ts>-fix-<slug>-security.md` per `five-stages`, each step carrying its
  verification command and expected output, plus the rollback line.
- **Deliver both as files** in chat (`MEDIA:/abs/path`), with a short passport in the message: what was verified,
  what was not, what you need from him (admin/SFTP/panel access), and the question «даю go?».

## Pitfalls

- **`openssl s_client -tls1` failing proves nothing about the server.** OpenSSL 3 refuses legacy protocols at
  its default security level, and `no protocols available` is the *client's* refusal — it reads exactly like a
  server with TLS 1.0 disabled. Force it: `echo | openssl s_client -tls1 -cipher 'DEFAULT@SECLEVEL=0' -connect
  host:443 -servername host` and read `Protocol :`. This is the «a negative finding is only as good as the method»
  rule from `five-stages` in its most expensive form: a config finding reversed in front of the owner.
- **A data file under uploads is not automatically a leak.** Files that map plugin names to DB tables are static
  reference data shipped by the plugin (thousands of entries) — they carry no site-specific information. Open the
  file and check whether the content is about *this* site before writing «информационная утечка».
- **CPE match on an EOL branch produces an alarming matrix that may be wrong.** Backports again: state the caveat
  and the server-side verification (`wp core verify-checksums`) instead of asserting twelve exploitable CVEs.
- **Rate limiting cannot be disproved with three requests.** «Признаков блокировки нет на трёх попытках;
  полноценная проверка не проводилась, чтобы не ловить блокировку IP» is the honest sentence — never «лимита нет».
- **The RPC endpoint is the usual winner, and its probe is one request.** `system.listMethods`, then a single
  `system.multicall` batch with a throwaway credential pair: a `faultCode 403 / неверное имя` reply proves
  credentials are *evaluated* through the batch API, which is brute-force amplification — without ever running
  a real brute force.
- **Severity follows the reachable chain, not the number.** Author-level arbitrary file deletion → delete
  `wp-config.php` → reinstall → RCE outranks a higher-scored CVE that needs a role the site never grants. Order
  priorities by «что может сделать атакующий, который дошёл до этой точки».
- **NVD without an API key throttles.** Sleep several seconds between calls and cap `resultsPerPage`; cve.org
  has no such limit and is the faster path for reading one record.
- **Inventory claims must come from a source that names this site's own install.** A slug found in a generic
  plugin list is not installed software; grep the readme endpoints, not a directory index you assumed.
