# OpenCode sandbox external_directory auto-reject

## Symptom

When OpenCode CLI is asked to write to a directory outside its default working
cwd (e.g. `/mnt/data/natan-storage/...`), the request is auto-rejected even
after the user explicitly says "give permissions to opencode":

```
! permission requested: external_directory (/mnt/data/natan-storage/...); auto-rejecting
```

A second failure mode is an internal OpenCode tool error:

```
✗ Todos failed
Error: The todowrite tool was called with invalid arguments: SchemaError(...)
```

## Root cause

OpenCode's runtime applies a sandbox policy that auto-denies writes outside its
workspace. User authorization in the chat layer does not override this policy.

A separate issue affects headless execution via piped stdin: OpenCode's
built-in `todowrite` tool throws a SchemaError and aborts. This happens even
with `--auto --dir` and `--pure`. See `references/opencode-headless-limitations.md`
for details.

## Workarounds

1. **Preferred: use Hermes `delegate_task` subagents.**
   They share the host filesystem and can write to project directories directly.
   This also bypasses the `todowrite` bug.

2. **Alternative: scaffold inside OpenCode cwd and move.**
   - Let OpenCode create the project under `/tmp/...`.
   - Use Hermes terminal to move the result to the real target path.
   - Verify at the real path.
   - **Risk:** the `todowrite` bug may still abort headless execution.

3. **Do NOT keep retrying OpenCode with permission prompts.**
   The auto-reject is deterministic. Each retry wastes time and budget.

## Decision rule

```
Target path is outside OpenCode's default cwd?
  Yes → Prefer Hermes delegate_task subagents.
No, but using headless `opencode run < brief.md`?
  Yes → Prefer Hermes delegate_task subagents (todowrite bug).
Interactive TUI in project cwd?
  Yes → OpenCode may work; test with smoke task first.
```

## Session provenance

- 2026-08-01: silicone-lending-v3 at `/mnt/data/natan-storage/silicone-lending-v3`.
  OpenCode failed with `external_directory` auto-reject; Hermes `delegate_task`
  completed the same brief without issues.
- 2026-08-01: `opencode run --auto --dir /mnt/data/natan-storage/silicone-lending-v3 < brief.md`
  passed `--auto --dir` permissions but failed on internal `todowrite` SchemaError.
  The same command with a prompt starting `"Do not use todo or planning tools"`
  successfully wrote simple files, but large briefs still truncated.
