# hermes-skills

Полная библиотека активных навыков (skills) для Hermes Agent, используемых в
проекте Master Ugwai.

Этот репозиторий — **машинно-читаемая копия** skill-директорий из
`~/.hermes/skills/`. Каждый навык следует формату Hermes SKILL.md и может быть
установлён или изучён другим агентом.

## 📚 Связанная база знаний

Документация, runbook'и и инструкции для агента живут в отдельном vault:

> **https://github.com/fester00/obsidian-memory**

Там находятся:

- `Operations/MOC — Skills.md` — индекс всех навыков и runbook'ов
- `Operations/Skills/*.md` — человеко-читаемые карточки ключевых навыков
- `Operations/Runbooks/Master Ugwai — Operating Instructions.md` — рабочие
  инструкции персоны Master Ugwai
- `AGENTS.md` — constitution агента для работы внутри vault

**Рекомендуемый порядок:** другой агент сначала читает Obsidian-базу, затем
приходит сюда за конкретными `SKILL.md` файлами.

## 🗂️ Структура

```
skills/
├── apple/
├── autonomous-ai-agents/
├── computer-use/
├── creative/
├── data-science/
├── devops/
├── dogfood/
├── education/
├── email/
├── gaming/
├── github/
├── knowledge-first-protocol/
├── marketing/
├── mcp/
├── media/
├── mlops/
├── note-taking/
├── productivity/
├── red-teaming/
├── research/
├── shopping/
├── smart-home/
├── social-media/
├── software-development/
└── yuanbao/
```

Каждый навык:

```text
skills/<category>/<skill-name>/
├── SKILL.md           # основной файл навыка
├── references/        # дополнительные материалы (опционально)
├── scripts/           # исполняемые скрипты (опционально)
├── templates/         # шаблоны (опционально)
└── examples/          # примеры (опционально)
```

## 📊 Статистика

| Метрика | Значение |
|---------|----------|
| Всего активных навыков | 135 |
| Категорий | 25 |
| В архиве | ~56 (не входят в этот репозиторий) |

## 🔥 Ключевые навыки

| Навык | Описание | Путь |
|---|---|---|
| `hermes-agent` | Полное руководство по Hermes Agent | `autonomous-ai-agents/hermes-agent/` |
| `superpowers-workflow` | Полный lifecycle разработки в Hermes | `software-development/superpowers-workflow/` |
| `knowledge-first-protocol` | Порядок поиска информации | `knowledge-first-protocol/` |
| `setup-zsh-oh-my-zsh` | Установка zsh + Oh My Zsh + Oh My Posh | `devops/setup-zsh-oh-my-zsh/` |
| `opencode` | Делегирование кодинга в OpenCode CLI | `autonomous-ai-agents/opencode/` |
| `hermes-skill-library` | Публикация и синхронизация библиотеки навыков | `software-development/hermes-skill-library/` |
| `obsidian` | Работа с Obsidian vault | `note-taking/obsidian/` |
| `pentajunior-v2-seo` | SEO-оптимизация pentajunior-v2 | `software-development/pentajunior-v2-seo/` |
| `yandex-seo-optimization` | SEO для Яндекса | `marketing/yandex-seo-optimization/` |
| `claude-design` | Дизайн-процесс + Prompt Enhancement Pipeline | `creative/claude-design/` |
| `ui-ux-pro-max` | Design intelligence + anti-generic checklist | `creative/ui-ux-pro-max/` |
| `popular-web-designs` | 74 реальных design system | `creative/popular-web-designs/` |
| `selective-vpn-routing` | Маршрутизация сервисов через VPN/прокси | `devops/selective-vpn-routing/` |

## 📥 Как использовать навык

### В Hermes

```bash
# Если skill поддерживает установку из репозитория
hermes skills install <skill-name>

# Или скопировать вручную
cp -r skills/<category>/<skill-name> ~/.hermes/skills/<category>/
```

### Для изучения другим агентом

Просто прочитай `SKILL.md` из нужной директории. Формат самодостаточен:
YAML frontmatter + markdown body с workflow, pitfalls и связями.

## 🔄 Синхронизация

Этот репозиторий — копия локальных навыков. Для обновления:

```bash
cd ~/hermes-skills
rsync -av --delete --exclude='.archive' --exclude='.curator_backups' --exclude='.hub' \
  ~/.hermes/skills/ skills/
git add -A
git commit -m "sync skills from ~/.hermes/skills"
git push origin main
```

## 📝 Лицензия

Навыки имеют разные лицензии в зависимости от источника. Смотри `license:` в
frontmatter каждого `SKILL.md`. Собственные навыки Master Ugwai — MIT.

## 🔗 Cross-links

- Obsidian knowledge base: https://github.com/fester00/obsidian-memory
- MOC — Skills: https://github.com/fester00/obsidian-memory/blob/main/Operations/MOC%20%E2%80%94%20Skills.md
- Hermes — Skills Registry: https://github.com/fester00/obsidian-memory/blob/main/Operations/Skills/Hermes%20%E2%80%94%20Skills%20Registry.md
- Master Ugwai Operating Instructions: https://github.com/fester00/obsidian-memory/blob/main/Operations/Runbooks/Master%20Ugwai%20%E2%80%94%20Operating%20Instructions.md
