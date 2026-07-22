---

# Codebase Memory Audit Template

Use this template when creating `codebase-memory-audit.md` notes in project folders.

## Project

- **Project name:** {{PROJECT_NAME}}
- **Project path:** {{PROJECT_PATH}}
- **Generated:** {{TIMESTAMP}}
- **CBM version:** {{CBM_VERSION}}

## Graph overview

| Metric | Value |
|---|---|
| Nodes | {{NODE_COUNT}} |
| Edges | {{EDGE_COUNT}} |
| Languages | {{LANGUAGES}} |
| Source files | {{FILE_COUNT}} |
| Project slug | `{{PROJECT_SLUG}}` |

## Hotspots

Most referenced symbols — changing these has wide impact:

| Symbol | Fan-in | File |
|---|---|---|
| {{HOTSPOT_1}} | {{FAN_IN_1}} | {{FILE_1}} |
| {{HOTSPOT_2}} | {{FAN_IN_2}} | {{FILE_2}} |
| {{HOTSPOT_3}} | {{FAN_IN_3}} | {{FILE_3}} |

## Layers

| Layer | Packages | Role |
|---|---|---|
| entry | {{ENTRY_PACKAGES}} | Top-level pages/routes/scripts |
| internal | {{INTERNAL_PACKAGES}} | Business logic handlers |
| core | {{CORE_PACKAGES}} | Shared utilities and DB access |
| leaf | {{LEAF_PACKAGES}} | No outbound dependencies |

## Boundaries

Key cross-module call links:

| From | To | Call count |
|---|---|---|
| {{FROM_1}} | {{TO_1}} | {{COUNT_1}} |
| {{FROM_2}} | {{TO_2}} | {{COUNT_2}} |
| {{FROM_3}} | {{TO_3}} | {{COUNT_3}} |

## Clusters

Functional communities detected by CBM:

| Cluster | Label | Members | Cohesion | Top nodes |
|---|---|---|---|---|
| {{CLUSTER_ID_1}} | {{LABEL_1}} | {{MEMBERS_1}} | {{COHESION_1}} | {{TOP_NODES_1}} |
| {{CLUSTER_ID_2}} | {{LABEL_2}} | {{MEMBERS_2}} | {{COHESION_2}} | {{TOP_NODES_2}} |
| {{CLUSTER_ID_3}} | {{LABEL_3}} | {{MEMBERS_3}} | {{COHESION_3}} | {{TOP_NODES_3}} |

## Entry points

- {{ENTRY_POINT_1}}
- {{ENTRY_POINT_2}}
- {{ENTRY_POINT_3}}

## Key queries

Useful CBM queries for this project:

```bash
codebase-memory-mcp cli trace_path --project {{PROJECT_SLUG}} --function-name {{HOTSPOT_1}} --direction inbound
codebase-memory-mcp cli search_code --project {{PROJECT_SLUG}} --pattern "TODO|FIXME"
codebase-memory-mcp cli query_graph --project {{PROJECT_SLUG}} --query "MATCH (f:Function) WHERE f.in_degree = 0 AND NOT f.is_test RETURN f.name LIMIT 20"
```

## Usage in design/planning

When working on this project, consult this audit before:
- Refactoring hotspots (high fan-in)
- Crossing boundaries between layers
- Adding new entry points
- Removing "leaf" packages

## Rebuild command

```bash
codebase-memory-mcp cli index_repository --repo-path {{PROJECT_PATH}}
```
