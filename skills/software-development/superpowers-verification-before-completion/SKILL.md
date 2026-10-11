---
name: superpowers-verification-before-completion
description: Use when about to claim success, completion, or that tests pass. Run fresh verification first.
---

# Verification Before Completion

**Core principle:** Evidence before claims, always.

Используй этот навык как последний барьер перед любым утверждением о том, что работа завершена, баг исправлен, тесты проходят или сборка собирается. Он не заменяет `code-quality-gates`: конкретные команды тестов, линтеров и security-сканов бери из `code-quality-gates` Gate 1–4. Этот навык фиксирует дисциплину «сначала доказательство, потом слова».

## Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

Если ты не выполнил проверяющую команду в этом сообщении — ты не можешь утверждать, что всё работает.

## Gate Function

BEFORE claiming any status:

1. **IDENTIFY** — какая команда докажет это утверждение?
2. **RUN** — выполни полную команду заново, целиком.
3. **READ** — полный вывод, код возврата, количество падений.
4. **VERIFY** — вывод подтверждает утверждение?
   - Нет: сообщи фактический статус с доказательством.
   - Да: сообщи утверждение вместе с доказательством.
5. **ONLY THEN** — сделай утверждение.

Пропуск любого шага = не верификация, а самоуспокоенность.

## Common Failures

| Claim | Requires | Not sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags — STOP

- Слова "should", "probably", "seems to".
- Выражение удовлетворённости до проверки: "Great!", "Perfect!", "Done!".
- Собираешься коммитить / пушить / создавать PR без проверки.
- Доверяешь отчёту агента без независимой проверки.
- Полагаешься на частичную проверку.
- Думаешь "только в этот раз".
- Устал и хочешь закончить.
- Любая формулировка успеха без запущенной проверки.

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## When To Apply

**ALWAYS before:**
- Any variation of success/completion claims.
- Any expression of satisfaction.
- Any positive statement about work state.
- Committing, PR creation, task completion.
- Moving to next task.
- Delegating to agents.

**Rule applies to:** exact phrases, paraphrases, synonyms, implications of success, any communication suggesting completion/correctness.

## Mapping to Hermes gates

- Конкретные команды и security-сканы: `code-quality-gates` Gate 3 (Pre-Commit Verification).
- Тесты перед фиксом/фичей: `code-quality-gates` Gate 1 (TDD).
- Отладка неожиданных падений: `code-quality-gates` Gate 2 (Systematic Debugging).
- Runtime-отладка: `code-quality-gates` Gate 4 (Runtime Debugging).

## References

- `code-quality-gates` — Hermes-specific quality gates with concrete verification commands.
