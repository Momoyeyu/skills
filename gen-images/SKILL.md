---
name: gen-images
description: Use when the user wants to generate images for blog posts or documents using AI image models. Supports any OpenAI-compatible provider. Triggers on "生成图片", "配图", "generate image", "gen image".
---

# gen-images

通过 OpenAI 兼容 API 生成配图，支持多服务商、多模型并行、人工挑选。

## 前置检查

1. 检查 `scripts/images.yaml` 是否存在，不存在则帮用户创建（参考 `${CLAUDE_SKILL_DIR}/templates/images.yaml.example`）
2. 检查 YAML 中 `api_key` 引用的环境变量是否已设置

## YAML 配置

```yaml
models:
  - id: google/gemini-3-pro-image-preview
    label: banana-pro
    # api_base/api_key 省略时默认 OpenRouter
  - id: gpt-image-1
    label: openai
    api_base: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}   # ${xxx} 读环境变量，也可写明文

images:
  - name: my-image
    output_dir: public/img/posts/my-post
    prompt: |
      Generate a ...
```

## 生成

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/gen-images.py           # 默认读 scripts/images.yaml
python3 ${CLAUDE_SKILL_DIR}/scripts/gen-images.py --force    # 强制重新生成
```

## 选图与清理（多模型时必做）

1. 展示所有 `<name>-<label>.png` 给用户对比
2. 用户选择后复制为 `<name>.png`，删除所有带后缀的临时文件
