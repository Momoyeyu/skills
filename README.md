# Skills

[English](README_en.md) | 中文

我的 AI Agent Skills 合集，适用于 Claude Code 等支持 [Agent Skills 规范](https://agentskills.io/specification) 的工具。

## 安装

将 skill 目录复制到 `~/.claude/skills/` 即可：

```bash
# 从仓库安装
git clone https://github.com/Momoyeyu/skills.git
cp -r skills/gen-images ~/.claude/skills/
cp -r skills/tdd ~/.claude/skills/

# 或从 .skill 文件安装（ZIP 格式）
unzip gen-images.skill -d ~/.claude/skills/
```

## Skills 列表

| 名称 | 说明 | 调用方式 |
|------|------|----------|
| [gen-images](gen-images/) | 通过 OpenRouter 调用 AI 图像模型生成配图，支持多模型并行、人工挑选 | `/gen-images` |
| [tdd](tdd/) | 测试驱动开发流程指导 | `/tdd` |

## 依赖

- **gen-images**: 需要 Python 3、pyyaml、[OpenRouter](https://openrouter.ai/) API Key

## 许可

[MIT](LICENSE)
