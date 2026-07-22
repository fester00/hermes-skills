# Case: upstash/context7

Repo: https://github.com/upstash/context7
Stars: 58k+. MIT license. Node.js/TypeScript monorepo.

## What it is

Context7 fetches up-to-date, version-specific documentation and code examples for
libraries and frameworks, then injects them into the LLM context via MCP or CLI.

## Strong sides

- Solves real pain: outdated/hallucinated library APIs.
- Large index of libraries, version-aware.
- Multiple integrations: MCP, CLI (`ctx7`), TypeScript SDK, Vercel AI SDK tools.
- Works without API key; higher rate limits with free key.

## Red flags

- Requires external service (context7.com) — not self-hostable.
- API backend, parser, and crawler are private; open-source part is just the
  client/MCP wrapper.
- Need to manage another API key/credential.

## Verdict for this user

**Recommended for adoption.** The user frequently works with specific library
versions (Next.js 15 / React 19, vkbottle, httpx, local TTS tools). Context7 fills
the gap between the user's project-specific skills and raw web search.

Recommended integration path for Hermes:

1. Add Context7 MCP server to `~/.hermes/config.yaml`:

   ```yaml
   mcp:
     servers:
       context7:
         command: npx
         args: ["-y", "@upstash/context7-mcp@latest"]
         env:
           CONTEXT7_API_KEY: "ctx7sk-..."
   ```

2. Or use HTTP transport:

   ```yaml
   mcp:
     servers:
       context7:
         transport: http
         url: https://mcp.context7.com/mcp
         headers:
           CONTEXT7_API_KEY: "ctx7sk-..."
   ```

3. Use the two-step workflow:
   - `resolve-library-id(libraryName, query)` → get `/org/project` ID
   - `query-docs(libraryId, query)` → fetch docs/code examples

4. Consider adding Context7 as a step in the knowledge-first protocol, between
   internal sources and web search, for any question involving external library
   APIs, setup, or configuration.
