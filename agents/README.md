Configuration for coding agents — skills, and eventually whatever else turns
out to be worth sharing between harnesses. Nothing in here is specific to a
particular agent, so `install.sh` stows the same tree into each harness's
configuration directory (currently just `~/.claude`).

There are two stow packages:

- `shared/` is tracked in this repository and published.
- `local/` is git-ignored, for things that shouldn't be public: work-specific
  skills, anything with personal details in it, half-finished experiments.

Both stow into the same directories, so `~/.claude/skills` ends up as a real
directory containing a symlink per skill rather than a single symlink to
`shared/skills`.
