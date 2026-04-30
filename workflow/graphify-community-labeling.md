---
title: Graphify Community Labeling (LLM-assisted)
tags: [workflow, graphify, tool]
created: 2026-04-24
updated: 2026-04-30
status: active
type: workflow
scope: tool
---

# Graphify Community Labeling (LLM-assisted)

How to give graphify communities semantic names (e.g. "Postprocessing & Figures Pipeline") instead of the generic `Community N` that `graphify cluster-only` produces, **and how those names survive re-clustering** without silently misaligning with content.

## Convention

After any re-clustering of a project's graph, Claude (the LLM) must assign 2–5 word plain-language names to each community and persist them to `graphify-out/.graphify_labels.json` in the membership-keyed schema below. Subsequent rebuilds carry names forward automatically; the LLM only has to (re)label communities the post-commit hook flags as `(drifted)` or `(new)`.

## Schema

`graphify-out/.graphify_labels.json` is keyed by `cid` but each entry stores both the name and the member set captured at write-time:

```json
{
  "0": {
    "name": "Postprocess Draws & Figures",
    "members": ["postprocess.R", "03_postprocess_results.R", "..."]
  },
  "1": { "name": "...", "members": ["..."] }
}
```

The `members` list is what makes the name survive a re-cluster — `cid` is volatile (the cluster algorithm is free to shuffle ids run-to-run), but member overlap identifies the same community.

## Rationale

- `graphify cluster-only <path>` only emits `labels = {cid: f"Community {cid}"}` — no LLM call (see `graphify/__main__.py` L1329 in the pipx venv).
- Labels are **not** persisted inside `graph.json`; they live in `graphify-out/.graphify_labels.json` and are applied at export time via the `community_labels=` parameter of `to_obsidian`, `to_canvas`, and `to_html`.
- Without labels, the vault's community overview notes become `_COMMUNITY_Community 0.md` etc., which defeats the purpose of the graph-as-navigation-index (see [[claude-md-vs-vault-notes]]).
- Without **member-keyed** labels, every re-cluster silently shuffled the cid→name mapping (incident on 2026-04-29: nearly all 29 community names had drifted from their content over a few days of post-commit-hook rebuilds). Member-keyed labels + Jaccard carry-forward in the hook prevent this.

## How re-clustering is handled (automatic)

### Trigger condition

The hook fires only when a commit touches **pipeline files**: `analysis/` (excluding `analysis/scratchpads/`) and `tests/`, with extensions `.R`, `.sh`, `.stan`, `.Rmd`, or `.qmd`. Commits that only change notebooks (`notebooks/`) or scratchpads (`analysis/scratchpads/`) do **not** trigger a rebuild. Both directories remain in the graph scope for manual rebuilds.

This avoids spurious re-clusterings — and the accompanying community-drift warnings — from exploratory scratchpad commits that don't affect the pipeline graph structure.

### What happens on a triggered rebuild

The project post-commit hook (installed from `scripts/post-commit-graphify` into `<your-project>/.git/hooks/post-commit`) does the following on every rebuild:

1. Re-clusters the graph.
2. For each new community `C_new`, computes Jaccard similarity against every old community's `members` list.
3. Greedy one-to-one assignment by descending Jaccard, with cutoff `JACCARD_THRESHOLD = 0.5`. Old name carries forward to whatever new `cid` the algorithm picked.
4. Communities with no qualifying old match are named `Community <cid> (new)`.
5. Communities matched at `J < 1.0` keep their old name **and** are reported on stderr as `WARN: N communities drifted; relabel pass needed`.
6. Refreshed `{name, members}` written back to `.graphify_labels.json` so next run starts from current membership.
7. Vault mirror at `~/vault/graphify/<project>/` (overridable via `GRAPHIFY_VAULT_MIRROR`) wiped and regenerated via `to_obsidian` + `to_canvas` with the carried-forward labels.

What survives automatically: **pure cid shuffles** (J=1.0, silent), **small membership churn** (J ≥ 0.5, name carries with warning), **community splits** (the half with ≥0.5 overlap inherits the parent name; the other half is flagged `(new)`), **disappearances** (orphan labels auto-pruned).

What the LLM still has to do: assign names to communities flagged `(new)` or to ones flagged `(drifted)` whose Jaccard is so low that the carried name is misleading.

## Procedure — full relabel (rare, only on first setup or after major restructure)

### 1. Dump community membership

After clustering, list each community with its member node labels so Claude has enough context to name them:

```python
# run in the graphify pipx venv
import json
from graphify.build import build_from_json

raw = json.loads(open('graphify-out/graph.json').read())
G = build_from_json(raw)
communities = {}
for nid, a in G.nodes(data=True):
    c = a.get('community')
    if c is None: continue
    communities.setdefault(int(c), []).append(nid)

for cid, members in sorted(communities.items(), key=lambda x: -len(x[1])):
    labels = [G.nodes[n].get('label', n) for n in members]
    print(f'## Community {cid} ({len(members)} nodes)')
    for lbl in labels[:25]:
        print(f'  - {lbl}')
```

### 2. Name each community (2–5 words)

Claude reads the member lists and assigns short plain-language names. Good examples:
- ✅ `Postprocessing & Figures Pipeline`
- ✅ `Parameter Priors & Bounds`
- ✅ `ODE Models (Stan)`

Avoid jargon or names that duplicate a single function label.

### 3. Persist and regenerate

Write `.graphify_labels.json` in the **`{name, members}` schema** (not the legacy flat `{cid: name}`):

```python
from graphify.cluster import score_all
from graphify.export import to_obsidian, to_canvas, to_html

names = {0: "...", 1: "...", ...}                 # dict keyed by int community id
cohesion = score_all(G, communities)

rich = {str(cid): {'name': names[cid], 'members': sorted(communities[cid])}
        for cid in communities}
open('graphify-out/.graphify_labels.json','w').write(json.dumps(rich, indent=2))

# Pass a flat {cid: name} dict to the export functions
flat = {int(k): v['name'] for k, v in rich.items()}
to_html(G, communities, 'graphify-out/graph.html', community_labels=flat)
n = to_obsidian(G, communities, OBSIDIAN_DIR,
                community_labels=flat, cohesion=cohesion)
to_canvas(G, communities, f'{OBSIDIAN_DIR}/graph.canvas',
          community_labels=flat)
```

Set `OBSIDIAN_DIR` to `~/vault/graphify/<your-project>` (or whatever path you pass to `--obsidian-dir`). Wipe its contents before regeneration to avoid stale notes from earlier runs.

### 3a. Do NOT mirror `GRAPH_REPORT.md` or `graph.json`

These two files are emitted to `graphify-out/` (the source of truth) and must **not** be copied or left in `OBSIDIAN_DIR`. Reasons:

- `to_obsidian` regenerates the per-node and `_COMMUNITY_*` notes on every run, but historically did **not** rewrite `GRAPH_REPORT.md` / `graph.json` if they were already present in the mirror — so any copy there silently goes stale across rebuilds (incident on 2026-04-28: mirrored `GRAPH_REPORT.md` was 4 days behind the source after a rebuild that didn't re-run `to_obsidian`).
- The authoritative versions live at `<project>/graphify-out/GRAPH_REPORT.md` and `<project>/graphify-out/graph.json`. Read them there.
- If a wipe-then-regenerate cycle ever produces them in `OBSIDIAN_DIR`, delete them immediately after step 3. The post-commit hook handles this automatically.

## Procedure — partial relabel (the common case)

When the hook reports `WARN: N communities drifted; relabel pass needed`:

1. Read the warning lines (`C<cid> <- old C<old_cid> "<name>" (J=…)` for drifted; `C<cid> unmatched: Community N (new)` for new).
2. Dump membership for *only* the flagged cids (modify the loop in step 1 above to filter `cid in flagged`).
3. Decide for each flagged community whether the carried name is still right (low Jaccard but still semantically the same community), or whether it needs a fresh 2–5 word name.
4. Edit `.graphify_labels.json` directly: change the `name` field for the flagged cids; leave their `members` list as-is (the hook will overwrite it on the next rebuild).
5. Regenerate the vault mirror and HTML by running step 3 above, **or** simply trigger the hook by making any commit.

No need to re-derive member lists by hand — the hook keeps them in sync.

## Verify

- `ls graphify/<project>/ | grep '^_COMMUNITY_' | wc -l` should equal the community count
- No `_COMMUNITY_Community N.md` files should remain — all should have semantic names
- `ls graphify/<project>/ | grep -E '^(GRAPH_REPORT\.md|graph\.json)$'` must return nothing (per step 3a)

## Scope

Applies to every graphify-maintained project subfolder under `graphify/` in this vault.

- **Initial `/graphify` setup** → full relabel procedure.
- **Every pipeline commit** → post-commit hook runs the automatic carry-forward; LLM only intervenes if stderr reports `WARN: ... drifted; relabel pass needed`. Scratchpad and notebook commits do not trigger the hook.
- **Major restructure** (e.g. large file rename, scope change) → if Jaccard carry-forward flags too many communities, fall back to full relabel.

## Related

- [[claude-md-vs-vault-notes]] — why the vault mirror matters as a navigation layer
