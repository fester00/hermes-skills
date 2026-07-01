---
name: apple-ecosystem
description: |
  Manage Apple ecosystem apps from the terminal: Notes (memo), Reminders (remindctl),
  Messages (imsg), and Find My (AppleScript + UI automation). All commands require
  macOS with appropriate permissions and iCloud sign-in.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [apple, macos, notes, reminders, imessage, findmy, icloud]
    related_skills: [obsidian, google-workspace]
---

# Apple Ecosystem

Use macOS CLI tools to manage Apple apps that sync across devices via iCloud.

---

## Quick Permission Checklist

All Apple automation requires explicit macOS permissions:

| App | Permission Path |
|-----|----------------|
| Notes | System Settings → Privacy → Automation → Notes |
| Reminders | System Settings → Privacy → Reminders |
| Messages | System Settings → Privacy → Full Disk Access (terminal) + Automation → Messages |
| Find My | System Settings → Privacy → Screen Recording (terminal) |

---

## 1. Apple Notes (`memo`)

Create, search, edit, and export Apple Notes directly from the terminal.

**Install:** `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`

**Commands:**
```bash
memo list                           # All notes
memo search "query"                 # Full-text search
memo show "Note Title"            # Display note content
memo new "Title" "Body text"        # Create a note
memo edit "Title" "Updated body"    # Update a note
memo export "Title" > note.md      # Export to markdown
```

**See `references/apple-notes.md` for folder management, batch export, and HTML output.**

---

## 2. Apple Reminders (`remindctl`)

Add, list, complete, and manage lists in Apple Reminders.

**Install:** `brew install steipete/tap/remindctl`

**Commands:**
```bash
remindctl status                    # Check authorization
remindctl authorize                 # Grant permissions
remindctl lists                     # Show all lists
remindctl add "Buy milk" --list Shopping --due "tomorrow 9am"
remindctl list Shopping             # Show items in a list
remindctl complete "Buy milk" --list Shopping
remindctl delete "Buy milk" --list Shopping
```

**See `references/apple-reminders.md` for due-date syntax, recurring reminders, and priority tags.**

---

## 3. iMessage (`imsg`)

Send and read iMessages/SMS via the macOS Messages app.

**Install:** `brew install steipete/tap/imsg`

**Commands:**
```bash
imsg send +1234567890 "Hello"       # Send SMS/iMessage
imsg recent                         # Recent conversations
imsg search "query"                   # Search message history
imsg read +1234567890              # Read last messages with contact
imsg send "user@icloud.com" "Text"  # Send via Apple ID
```

**See `references/imessage.md` for group chat caveats, attachment handling, and read receipts.**

---

## 4. Find My (`osascript` + `peekaboo`)

Track Apple devices and AirTags via FindMy.app automation.

**Prerequisites:** macOS with Find My app, iCloud signed in, devices already registered.

**Open and capture:**
```bash
osascript -e 'tell application "FindMy" to activate'
# Then use vision_analyze on a screenshot to read device locations
```

**With `peekaboo` (optional, better UI automation):**
```bash
brew install steipete/tap/peekaboo
peekaboo list-devices               # List registered devices
peekaboo locate "iPhone"           # Get location text
```

**See `references/findmy.md` for AirTag patrol routes, device battery checks, and AppleScript snippets.**

---

## Decision Tree

| User says... | Use section |
|--------------|-------------|
| "create a note" / "save to Notes" | **1. Apple Notes** |
| "remind me to..." / "set a reminder" | **2. Apple Reminders** |
| "send a text" / "iMessage" / "SMS" | **3. iMessage** |
| "where is my..." / "track my..." | **4. Find My** |
| "apple" (ambiguous) | Ask which app, or offer the four options |