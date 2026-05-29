# Skills

English | [中文](README.md)

My personal AI Agent Skills collection, compatible with Claude Code and other tools that support the [Agent Skills specification](https://agentskills.io/specification).

## Installation

Copy the skill directory to `~/.claude/skills/`:

```bash
# Install from repo
git clone https://github.com/Momoyeyu/skills.git
cp -r skills/gen-images ~/.claude/skills/
cp -r skills/tdd ~/.claude/skills/

# Or install from .skill file (ZIP format)
unzip gen-images.skill -d ~/.claude/skills/
```

## Skills

| Name | Description | Invoke |
|------|-------------|--------|
| [gen-images](gen-images/) | Generate blog images via OpenRouter AI models, with multi-model parallel generation and manual selection | `/gen-images` |
| [tdd](tdd/) | Test-Driven Development workflow guide | `/tdd` |

## Dependencies

- **gen-images**: Requires Python 3, pyyaml, [OpenRouter](https://openrouter.ai/) API Key

## License

[MIT](LICENSE)
