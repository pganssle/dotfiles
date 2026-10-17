Configuration for coding agents: reusable skills shared across harnesses.

- `shared/` is tracked and published.
- `local/` is git-ignored, for private or unfinished skills.

`install.sh` uses two installation layouts:

- `~/.agents/skills/shared` and `~/.agents/skills/local` link to the respective
  skill collections. Codex scans through these links recursively, so adding a
  skill to either source directory needs no installer refresh. Start a new
  session if the client hasn't refreshed its skill list.
- `~/.claude/skills` contains individual skill links managed by Stow. Claude Code
  scans immediate skill directories, so new skills still require rerunning the
  installer or `stow -d agents -t ~/.claude shared local` from this repository.

To install only the Codex collection links, run `bash agents/install-skills.sh`.
The helper accepts an optional agent directory, migrates the old per-skill links,
leaves unrelated skills alone, and refuses conflicting collection names. A legacy
symlink for the entire `skills` directory must be removed first, preserving its
source directory. The helper creates an empty local collection if needed, so its
first skill will also be discovered automatically.
