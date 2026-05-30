# AGENTS.md — construct-landing

These instructions apply to GitHub Copilot, Codex, OpenCode, and similar coding agents working in this repository.

## Shared Construct docs

- Use `~/Code/construct-docs` as the shared Construct documentation vault.
- Treat `~/Code/construct-docs/raw` as the source corpus. Do not rewrite, normalize, or reorganize files there unless the task explicitly targets raw-doc curation.
- Treat `~/Code/construct-docs/wiki` as the canonical curated knowledge base.
- Treat `~/Code/construct-docs/wiki/.drafts` as reserved for the `obsidian-llm-wiki-local` draft-review workflow. Do not write there manually unless the task explicitly involves `olw`.

## Where to save durable reasoning

- If a task produces durable implementation notes, rationale, architecture conclusions, or cross-repo findings, store them in the wiki vault instead of creating ad-hoc markdown notes in this repository unless repo-local docs are explicitly requested.
- Use `~/Code/construct-docs/wiki/sessions/YYYY-MM-DD-<topic>.md` for session notes.
- Use `~/Code/construct-docs/wiki/decisions/` for long-lived decisions that should survive beyond one task.
- Before creating a new session or decision note, look for an existing relevant note and extend it instead of duplicating content.

## Session note template

When you create or update a session note, prefer these sections:

1. `# Context`
2. `# What Changed`
3. `# Why`
4. `# Intended Outcome`
5. `# Decisions`
6. `# Open Questions`

## Operational logging

- Keep `~/Code/construct-docs/wiki/log.md` as a short operational log.
- Append a concise entry there when work materially updates the knowledge base or when a durable audit trail is useful.
