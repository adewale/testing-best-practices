# Documentation-Code Sync Testing

Distinguish public contracts from implementation identity before pinning source
or outputs. See [implementation locks](implementation-coupling.md): retain
integrity and provenance controls while checking values, visible behavior or
public registries independently of private names and source serialization.


Use the code itself as the source of truth and verify docs match.

## Pattern: Every CLI command must be documented

```python
@pytest.mark.parametrize("command", cli.cli.commands.keys())
def test_commands_are_documented(documented_commands, command):
    assert command in documented_commands

@pytest.mark.parametrize("command", cli.cli.commands.values())
def test_commands_have_help(command):
    assert command.help, f"{command.name} is missing its help text"
```

## Pattern: Every plugin hook documented with correct signature

```python
def test_plugin_hooks_are_documented(plugin_hooks_content):
    for plugin in [n for n in dir(app.pm.hook) if not n.startswith("_")]:
        arg_names = [a for a in hook_caller.spec.argnames if a != "__multicall__"]
        expected = f"{plugin}({', '.join(arg_names)})"
        assert expected in plugin_hooks_content
```

## Pattern: Every setting/config documented

```python
def test_settings_are_documented(settings_headings):
    for setting in app.SETTINGS:
        assert setting.name in settings_headings
```

## Pattern: Verification claims in project docs

Testing docs, lessons-learned files, and agent instructions (CLAUDE.md, AGENTS.md)
are read by agents as instructions, so stale verification claims actively mislead.
Check the claims that drift:

- omit volatile test titles/counts from current instructions, or derive them
  from the runner; do not freeze a copied roster as a permanent gate;
- scripts and commands named in docs exist;
- statements such as "no CI" or "SKILL.md must stay under N lines" match the tree;
- version manifests that agents are told to read agree with `package.json`/`pyproject`;
- historical review dates identify the evidence's original subject; current
  verification requires relevant new evidence, not an automatic freshness ritual;
- skill frontmatter respects the spec (name matches directory, description ≤1024
  characters).

## When to add these

- CLI commands listed in README or docs
- Plugin/extension system with documented hooks
- Configuration settings described in docs
- Public API functions referenced in documentation
