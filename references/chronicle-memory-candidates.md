# Chronicle Memory Candidate Gotchas

## Candidate is not memory

A skill may discover information that could be durable, but it does not become memory merely because it appears in a journal.

Emit a principal-scoped candidate and let the sanctioned Chronicle ingestion path decide durable representation.

## Required ownership fields

Every memory-affecting candidate identifies:

- target principal;
- source actor/speaker;
- claim state;
- provenance/source references;
- derivation type;
- confidence when inferred;
- temporal validity when known.

Never infer that "memory" means the user principal.

## User evidence

Assistant, tool, and system text are not user-stated evidence.

When a skill infers something about the user, mark it inferred and preserve the source lineage. Repeated summaries of one source do not create independent corroboration.

## Structured values

Do not flatten emails, URLs, paths, addresses, or other structured values to satisfy an obsolete graph-string constraint. Preserve structured values and provenance through Chronicle's sanctioned interfaces.

## Direct database access

Never open Chronicle's SQLite database from a skill.

Use a Chronicle API/tool contract or emit a candidate through a documented journal/interface path.

## Journals

Journals remain immutable evidence. They are not deleted after ingestion and they are not automatically promoted into durable memory.
