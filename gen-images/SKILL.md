---
name: gen-images
description: Use when the user wants to generate images for blog posts or documents using AI image models via OpenRouter. Triggers on "生成图片", "配图", "generate image", "gen image", or when discussing illustrations for articles.
---

# gen-images — AI 图片生成

通过 OpenRouter 调用 AI 图像模型生成配图，支持多模型并行、人工挑选。

## 前置检查

### 1. API Key

```bash
echo $OPENROUTER_API_KEY | head -c 10
```

有输出 → 继续。为空 → 告诉用户：

> 需要配置 OpenRouter API Key：
> ```bash
> export OPENROUTER_API_KEY="sk-or-v1-..."
> ```
> 获取地址：https://openrouter.ai/keys

### 2. 配置文件

检查项目根目录下 `scripts/images.yaml` 是否存在。

- 存在 → 继续
- 不存在 → 帮用户创建，参考 `${CLAUDE_SKILL_DIR}/templates/images.yaml.example`

## 配置图片

`scripts/images.yaml` 格式：

```yaml
models:
  - id: google/gemini-3-pro-image-preview
    label: banana-pro
  - id: openai/gpt-5.4-image-2
    label: gpt-image-2

images:
  - name: my-image          # 文件名前缀
    output_dir: public/img/posts/my-post
    prompt: |
      Generate a ...         # 英文 prompt，图中文字用中文
```

**当用户需要新配图时：**

1. 确认图片内容、用在哪篇文章
2. 编写英文 prompt（图中文字用中文标注）
3. 追加到 `scripts/images.yaml` 的 `images:` 列表
4. 在文章中插入 `![alt](/img/posts/<slug>/<name>.png)`

## 生成图片

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/gen-images.py                # 默认读 scripts/images.yaml
python3 ${CLAUDE_SKILL_DIR}/scripts/gen-images.py --force         # 强制重新生成
python3 ${CLAUDE_SKILL_DIR}/scripts/gen-images.py path/to/config  # 自定义配置路径
```

**区域限制：** 如果遇到 403 错误，需要在美国等地区运行。此时把命令告诉用户转交。

## 选图与清理（多模型时必做）

生成后每个图片会有 `<name>-<label>.png` 多个版本。**必须：**

1. 用 Read 工具展示每个版本给用户对比
2. 用户选择后，复制选中版本为 `<name>.png`
3. 删除所有带模型后缀的临时文件

```bash
cp output_dir/my-image-banana-pro.png output_dir/my-image.png
rm output_dir/my-image-banana-pro.png output_dir/my-image-gpt-image-2.png
```

## 支持的模型

| 标签 | 模型 | 特点 |
|------|------|------|
| `banana-pro` | Gemini 3 Pro Image | 手绘风格好 |
| `gpt-image-2` | GPT-5.4 Image 2 | 细节丰富 |
