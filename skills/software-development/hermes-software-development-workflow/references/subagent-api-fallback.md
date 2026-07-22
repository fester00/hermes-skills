# Subagent API Fallback: When `delegate_task` Hits Provider Limits

## Symptom

`delegate_task` returns immediately with a provider error such as:

```
HTTP 429 from ollama.com — weekly usage limit
```

No subagent work is performed. The plan is blocked.

## Root Cause

The configured LLM provider (e.g. ollama-cloud) has a hard weekly/ daily request
cap. Subagents count against the same pool as the main session, so a batch of
`delegate_task` calls can exhaust it.

## Fix / Workaround

Switch from parallel subagents to **manual execution waves in the main session**.

1. Read the plan and create a `todo` list in the main session.
2. Execute tasks one by one (or in small sequential groups) using direct tools.
3. Run the same verification gates after each task:
   - `npm run typecheck`
   - `npm run lint`
   - `npm run build`
   - `npm test`
4. Commit after every task.
5. Update the plan file to mark completed tasks.

## Communication Pattern

Tell the user:

> API субагентов недоступен (HTTP 429 weekly limit). Продолжаю задачи вручную в
> основной сессии с теми же гейтами проверки.

## Prevention

- Before dispatching a large batch, check recent provider usage if available.
- For heavy refactoring, prefer external coding agent CLIs (OpenCode, Claude Code)
  running in background processes, or do the work directly in the main session.
- Keep subagent tasks small and batched; if the first fails with 429, do not
  retry the rest — switch to manual mode immediately.

## See Also

- `hermes-software-development-workflow` Appendix C: Subagent-Driven Execution
- `references/coding-agents/` for external CLI agent options
