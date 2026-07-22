>
# CI GitHub Actions Workflow with OAuth `workflow` Scope Pitfall

## Context

Adding `.github/workflows/ci.yml` to a repository whose remote URL uses an
OAuth App token (e.g. `gh auth login` with a GitHub OAuth token) can fail on
push with:

```
! [remote rejected] master -> master
(refusing to allow an OAuth App to create or update workflow
`.github/workflows/ci.yml` without `workflow` scope)
```

## Why it happens

GitHub requires the `workflow` OAuth scope to create or modify workflow files.
The default `gh auth login` token has `repo`, `read:org`, `gist`, but not
`workflow`. A `gh auth refresh --scopes workflow` may still not add the scope
if the token was originally issued without it.

## Workaround without regenerating the token

1. Remove the workflow file from the current commit:
   ```bash
   git rm .github/workflows/ci.yml
   git commit --amend --no-edit
   ```

2. Push the rest of the changes:
   ```bash
   git push origin master
   ```

3. Add the workflow file later through the GitHub web UI:
   - Repository → Actions → New workflow → set up a workflow yourself.
   - Paste the YAML content and commit directly to `master`.
   The web UI uses a different authorization path and does not require the
   OAuth `workflow` scope.

## Sample workflow content

```yaml
name: CI

on:
  push:
    branches: [master, main]
  pull_request:
    branches: [master, main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 24
      - run: npm ci
      - run: npm run typecheck
      - run: npm run lint
      - run: npm run test
      - run: npm run build
```

## Alternative fix (requires token regeneration)

Generate a **classic** GitHub Personal Access Token with at least:
- `repo`
- `workflow`
- `read:org` (optional)

Then re-authenticate `gh`:

```bash
gh auth logout
gh auth login --hostname github.com --git-protocol https --scopes repo,workflow,read:org,gist
```

Paste the new classic token when prompted.

## Communication pattern

Tell the user:

> Пуш с workflow-файлом не прошёл: GitHub требует scope `workflow` для OAuth-токена.
> Я удалил файл из коммита, запушил остальное, а workflow ты можешь добавить
> вручную через GitHub UI.

## See also

- `hermes-software-development-workflow` Phase 6: Finishing (push options)
- `github-workflows` skill for general GitHub Actions authoring
- GitHub docs: Scopes for OAuth Apps
