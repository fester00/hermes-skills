# Smart Device Signatures on a Consumer LAN

Depth notes for steps 5–7 of the skill: identifying an unknown host. Values below were observed
on a real home network behind a GL.iNet GL-MT6000 gateway (192.168.0.0/24).

## mDNS service → device class

| Service | Device class | Notes |
|---|---|---|
| `_yandexio._tcp` | Yandex Station / Alice speakers | TCP 1961. Answers only multicast mDNS; typically ICMP-silent. |
| `_googlecast._tcp` | Chromecast, Google/Nest, Android TV | TXT carries `fn` (friendly name), `md`, `id`. |
| `_airplay._tcp` | Apple TV, AirPlay TVs | TXT carries `manufacturer`, `model`, `deviceid` — richest self-description of any service. |
| `_androidtvremote2._tcp` | Android TV remote pairing | |
| `_matter._tcp` / `_matterc._udp` | Matter accessories | |
| `_hap._tcp` | HomeKit accessories | |
| `_http._tcp` | Embedded web UI | Generic; not conclusive on its own. |
| `_raop._tcp` | AirPlay audio (often the same box as `_airplay`) | |

`_services._dns-sd._udp.local` enumerates all of the above in one query — always run it first.

## Yandex Station (Alice) — worked example

Observed record set:

- Instance / PTR name: `YandexIOReceiver-<deviceId>`
- TXT: `deviceId=R10GB7000WNY6N`, `platform=cucumber`, `cluster=yes`
- rDNS: `Yandex-Station-Midi-<suffix>.lan` ← **the model name lives here**, not in mDNS
- OUI `3C:0B:4F`, registered to *Yandex Services AG* (Lucerne), later renamed *Intertech Services AG*
  — so an OUI lookup returns "Intertech", not "Yandex". Cross-check the registration history.
- Port 1961 (Yandex IO) accepts TCP but **ignores plaintext JSON** (`softwareVersion`, `externalLED`
  return an empty reply) — the channel is encrypted.
- `cluster=yes` means the speaker belongs to a multiroom group.

Local control options, in increasing order of effort: Home Assistant custom integration
(`yandex_station`, installed via HACS — does local control after a cloud login), community Python
libraries, or the cloud dialog API. Do not advertise local control from an open port alone.

### Can it be reflashed, or pointed at a different AI model?

This is the follow-up question that always comes after identifying a speaker. Answer it from the
mechanism, not from optimism.

**Local control is additive, not a replacement.** Yandex-brand speakers support local and cloud
control *simultaneously*; local mode enables automatically and nothing needs to be switched off.
Native Alice keeps working. What local mode adds: TTS in Alice's voice with effects (whisper,
megaphone, sound library, other SpeechKit voices) and no length cap, the speaker keeps listening
after TTS, per-message volume, playback/volume readback, media by URL, and multiroom streaming.
Cloud-only remains: ~100-character TTS cap, no state readback.

**Hard limits to state up front when the user asks for "other brains":**

- To have your own model answer through the speaker you need a scripted trigger — a vendor
  smart-home scenario keyed on a phrase (works on every model), or a local-intent trick that
  intercepts only a small fixed set of phrases. Multi-turn dialog is possible by registering a
  vendor "Dialogs" skill on your own webhook, which requires a public HTTPS endpoint.
- Reading the speaker's **own** answers only works for a fixed phrase set (weather, time, smart
  home). Arbitrary Q&A text is not returned, so Alice's answer cannot be rewritten — only your own
  text can be injected and spoken in her voice.
- **The microphone stream is not exposed.** It cannot be fed to your own ASR or wake word, so wake
  word and speech recognition always stay with the vendor. Never promise a full assistant swap;
  describe it as adding a scripted side channel.
- The integration creates a service scenario (named like `ХА UUID`) in the vendor app — deleting it
  breaks the integration until the host is restarted.
- Community integrations track a moving target: vendor firmware updates periodically break
  features, so budget for occasional updates.

**Reflashing: closed.** The U-Boot debug console is guarded by a vendor-specific challenge
("Rabbit Hole"): an RSA-2048 signature over a per-boot random challenge, verified in the
bootloader. There is one login attempt — a wrong answer reboots the device with a fresh challenge,
so brute force is useless, and the published firmware reverse-engineering work found no bypass.
That research covers the Amlogic-based models (S905X2 / A113X: Mini 2, Lite, Max); the
Midi / Station 2 / 3 generation's SoC is not publicly documented and is not covered. Dumping the
bootloader is only possible while it is not password-protected, and the vendor sets that password
remotely on newer units. No public custom firmware exists for the family — community "hacks" are
hardware mods (e.g. an ESP8266 plus optocoupler to switch audio output), not software.

Verdict to give the user: keep the vendor brain and add your own as a side channel; root/flash
attempts risk a bricked device with no replacement firmware.

## Other vendors seen in the wild

| OUI / pattern | Vendor | Notes |
|---|---|---|
| `94:83:c4` | GL Technologies (GL.iNet routers) | Gateway also answers on 8080/8443 for its web UI. |
| `50:ff:20` | Keenetic Limited | A second router behind the main one ⇒ expect a double-NAT leg. |
| `d8:d6:68` | Tuya Smart | Smart plugs/sensors; cloud-driven, little local surface. |
| `a4:6b:b6` | Intel Corporate | PC/laptop NIC. |
| Same MAC on many IPs | Range extender / repeater | e.g. `36:ce:4b:33:6e:67` answering for three IPs behind a TP-Link RE220. Proxy ARP, not spoofing. |
| 2nd hex digit in `2/6/a/e` | Randomised / private MAC | `36:ce:4b`, `62:08:8a`, `3a:c2:b9` — OUI lookup returns `Not Found`. Expected. |

## Reading the results

The reliable identification order is: **rDNS hostname → mDNS TXT → OUI registration history →
open port accepting a connection**. Two or more agreeing signals before naming a device.

## OUI lookup and its rate limit

```bash
curl -s --max-time 15 https://api.macvendors.com/3C:0B:4F
```

Batches trip `Please slow down your requests or upgrade your plan`; a sleep of 0.5 s between
requests is not enough for 5+ lookups. On that response, stop and switch to a web search for
`"<OUI>" OUI vendor` — the IEEE-derived lookup sites answer the same question without a key.
