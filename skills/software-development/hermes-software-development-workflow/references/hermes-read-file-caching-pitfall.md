# Hermes read_file Caching Pitfall

## Symptom

After writing a file with `write_file` or `patch`, subsequent `read_file(path)` calls return the **old content**. The file on disk is correct, but the tool's internal cache has not invalidated. This causes:

- Verification that reads back a file reports stale state
- Follow-up `patch` operations target old strings and fail or corrupt the file
- `execute_code` reading via `hermes_tools.read_file()` sees outdated content

## When It Happens

Most commonly observed after rapid successive edits to the same path, especially when:
- `write_file` or `patch` runs inside `execute_code`
- Multiple tool calls target the same file in one turn
- The file is large or has just been completely rewritten

## Detection

If `read_file` output contradicts `terminal` output or direct Python file reads, the cache is stale.

```bash
# Ground truth
cat path/to/file.tsx | grep "some string"
# or
python3 -c "print(open('path/to/file.tsx').read()[:500])"
```

## Workaround

Use direct filesystem reads for verification after heavy edits:

```python
import os
with open('/path/to/file.tsx', 'r', encoding='utf-8') as f:
    content = f.read()
assert 'expected string' in content
```

For quick checks, prefer `terminal` (`cat`, `grep`, `head`) over `read_file` after a burst of writes.

## Recovery

If a file was corrupted by a `patch` based on stale content:
1. Read the actual current content via `terminal` or Python.
2. Rewrite the whole file with `write_file` using the corrected content, rather than trying more patches.
3. Verify with `terminal`/`grep` or Python, not `read_file`.

## Prevention

- When verifying a file you just rewrote, use `terminal` or Python, not `read_file`.
- After `write_file` inside `execute_code`, print a checksum or key substring to confirm the write.
- If you need `read_file` pagination/line numbers, call it only before heavy edits, then switch to direct reads after.
