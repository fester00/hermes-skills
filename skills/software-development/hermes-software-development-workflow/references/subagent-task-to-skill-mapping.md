---
title: "Task-to-Skill Routing Map"
description: "Validated mapping of user's 5 typical tasks to skills + agent routing. No personality roles — direct routing only."
updated: 2026-05-17
verified: 2026-05-17
---

# Task-to-Skill Routing Map

Reference for matching incoming user requests to the right skills and routing decision.

## Typical Task Categories

| # | Типовая задача | Primary skills | Делать сам? | Делегировать когда? |
|---|---------------|----------------|------------|---------------------|
| 1 | **Создать сайт/проект** | `hermes-software-development-workflow` + `claude-design` + `sketch` + `popular-web-designs` + `code-quality-gates` + `expo-tanstack-backend` | ✅ Да | OpenCode background только при масштабном параллельном кодинге |
| 2 | **Найти в интернете товар** | `browser-automation` + `web` toolset | ✅ **ВСЕГДА САМ** | ❌ НИКОГДА — persona-правило |
| 3 | **Рефакторинг** | `code-quality-gates` + `subagent-driven-development` | ✅ Да | OpenCode если >25 файлов; 2 OC если 3+ подсистем |
| 4 | **Создать/переработать стиль** | `claude-design` + `popular-web-designs` + `sketch` | ✅ Да | delegate_task 1 шт. — только параллельные варианты |
| 5a | **Поиск через интернет** | `browser-automation` + `web` toolset | ✅ **ВСЕГДА САМ** | ❌ НИКОГДА |
| 5b | **Web scraping** | `browser-automation` | ✅ **ВСЕГДА САМ** | ❌ НИКОГДА |