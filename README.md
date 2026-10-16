# Neeto skills

A reusable bundle for investigating Neeto issues, making focused fixes, checking behavior in a consuming app, and preparing PRs when authorized.

Start with [`address-this-issue`](skills/address-this-issue/SKILL.md). The bundle includes all nine skills it directly references, three further skill dependencies, and the reference files they need. Cross-skill links are relative, so the bundle works outside its author's machine.

## Install

Clone the repository and run the installer with Python 3:

```sh
git clone https://github.com/pratiksau/neeto-skills.git
cd neeto-skills
python3 scripts/install.py
```

The installer copies all 13 skill folders into `~/.agents/skills`, a user-level discovery directory in [Codex's skills documentation](https://developers.openai.com/codex/skills). It stops before copying anything if a destination skill already exists. Back up or move conflicting folders before trying again. Start a new Codex session after installation.

To install only for a project, run this from the cloned bundle:

```sh
python3 scripts/install.py --dest /path/to/project/.agents/skills
```

For an agent that reads a different skills directory, pass that directory with `--dest`. Keep all folders together because the workflow reads sibling skills. Installation copies files and does not configure MCP servers or authentication.

## Use

Give the agent an issue URL and invoke the main skill:

```text
Use $address-this-issue to investigate and fix https://github.com/OWNER/REPO/issues/123.
Keep the changes local. Do not push or create a PR.
```

For investigation only:

```text
Use $address-this-issue to investigate https://github.com/OWNER/REPO/issues/123.
Report the cause and evidence. Do not change code.
```

When delivery is intended, explicitly authorize commits, pushes, and PR creation. The skill preserves narrower instructions. NeetoDeploy logs require approval for the needed logs, and production database access requires separate authorization.

## Included skills

| Skill | Role |
| --- | --- |
| [address-this-issue](skills/address-this-issue/SKILL.md) | Main issue investigation, fix, verification, and handoff workflow |
| [nt-debug-bug-codex](skills/nt-debug-bug-codex/SKILL.md) | Trace error context, stack behavior, and triggers |
| [debug-agent](skills/debug-agent/SKILL.md) | Test hypotheses with runtime instrumentation |
| [karpathy-guidelines](skills/karpathy-guidelines/SKILL.md) | Keep changes focused and define observable results |
| [neeto-intent-and-reuse](skills/neeto-intent-and-reuse/SKILL.md) | Check product intent, shared owners, and existing capabilities |
| [dhh-rails-style](skills/dhh-rails-style/SKILL.md) | Ruby and Rails style references |
| [neeto-fix-and-verify](skills/neeto-fix-and-verify/SKILL.md) | Verify a fix through a real consuming app |
| [remove-ai-code-slop](skills/remove-ai-code-slop/SKILL.md) | Review unnecessary changes against nearby conventions |
| [simplify](skills/simplify/SKILL.md) | Improve readability while preserving behavior |
| [issue-to-pr-delivery](skills/issue-to-pr-delivery/SKILL.md) | Deliver validated changes when authorized |
| [build-simple-durable-systems](skills/build-simple-durable-systems/SKILL.md) | Architecture guidance used by neeto-fix-and-verify |
| [asd-ste100](skills/asd-ste100/SKILL.md) | Clear technical prose used by issue-to-pr-delivery |
| [unslop](skills/unslop/SKILL.md) | Writing guidance used by issue-to-pr-delivery |

## Required access and tools

Each recipient needs their own repository access and local product checkout. Use the project's documented runtime and setup, including mise, Overmind, frontend builds, databases, and workers when applicable.

- GitHub access through an authenticated `gh` CLI or a connected GitHub tool.
- Neeto Record MCP when an issue contains recording evidence. The workflow inspects screenshots through MCP.
- Codex's in-app browser for interface reproduction and checks. Browser restrictions supplied by the user still apply. A client without that capability must report the verification gap.
- Node.js and npm/npx for `debug-agent` when instrumentation is required. The workflow starts `npx debug-agent` locally and uses its reported endpoint and log path.
- Honeybadger access when fault evidence is needed. The debugging skill describes a fallback when its MCP integration is unavailable.
- NeetoDeploy integration only when approved deployment logs or production data are needed. Use your organization's current connection documentation.

Skills provide instructions. They do not grant access to private code, recordings, production systems, or customer data. If a required capability is missing, report the specific unverified criterion and continue useful work within scope.

## Bundle adaptations and credits

The main workflow coordinates the supporting skills as one process. Its scope, session isolation, verification, and cleanup rules take precedence when it invokes a supporting skill. Neeto repository conventions take precedence over general style advice.

This bundle replaces machine-specific skill links, packages stack references that were missing from the installed debugging plugin, and supplies portable integration references. Those references require the recipient's own configured tools and current organization documentation. The ASD skill's version is stored in frontmatter metadata. The original installed skills are unchanged.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for preserved attribution and license notices.
