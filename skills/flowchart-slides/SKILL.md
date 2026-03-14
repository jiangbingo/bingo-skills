---
name: flowchart-slides
description: Generate cartoon-style HTML presentation slides with hand-drawn illustrations and step-by-step workflows. Creates visually appealing process diagrams perfect for tutorials, marketing demos, and training materials. Triggers: 流程图幻灯片, 演示文稿, 卡通风格, HTML slides, presentation, workflow demo, 教程幻灯片, 营销演示, 培训材料, process visualization, step-by-step guide, 手绘风格.
license: MIT
compatibility: No dependencies - pure HTML/CSS
metadata:
  version: "1.0.0"
  author: jiangbingo
---

# Flowchart Slides

Create beautiful cartoon-style HTML presentation slides with hand-drawn illustrations and clear step-by-step workflows.

## Quick Start

```bash
# Generate slides from topic
Use assets/template.html as base, customize content for user's topic

# Output: single HTML file, ready to open in browser
```

## Design Principles

### Visual Style

| Element | Specification |
|---------|---------------|
| **Overall** | Cartoon hand-drawn + business workflow |
| **Background** | White with subtle gray dotted grid |
| **Colors** | Soft pastels (light blue, pink, yellow) |
| **Typography** | Sans-serif, bold titles, clean body |
| **Illustrations** | Rounded hand-drawn style |
| **Decorations** | Stars, arrows, dotted lines |

### Layout Structure

```
┌─────────────────────────────────────┐
│         Page Title/Header           │
├─────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐           │
│  │ Step 1  │  │ Step 2  │  ...      │
│  │ [Icon]  │  │ [Icon]  │           │
│  │  Text   │  │  Text   │           │
│  └─────────┘  └─────────┘           │
└─────────────────────────────────────┘
```

## Color Palette

```css
/* Primary - Soft Pastels */
--blue-light: #E3F2FD;
--pink-light: #FCE4EC;
--yellow-light: #FFFDE7;
--green-light: #E8F5E9;
--purple-light: #F3E5F5;

/* Accents */
--yellow-bright: #FFEB3B;
--orange-bright: #FF9800;
--pink-bright: #E91E63;

/* Base */
--white: #FFFFFF;
--gray-grid: #F5F5F5;
--text-primary: #333333;
--text-secondary: #666666;
```

## Workflow

1. **Understand requirements** - Ask user about topic, steps, target audience
2. **Plan content** - Define 3-6 steps with clear descriptions
3. **Select illustrations** - Choose appropriate icons/images for each step
4. **Generate HTML** - Use template, customize content and colors
5. **Review output** - Ensure visual consistency and readability

## Step Card Pattern

Each step follows this structure:

```html
<div class="step-card">
  <div class="step-number">步骤 1</div>
  <div class="step-icon">
    <!-- SVG or emoji illustration -->
  </div>
  <div class="step-title">Step Title</div>
  <div class="step-desc">Brief description</div>
</div>
```

## Illustration Guidelines

| Step Type | Icon Suggestions |
|-----------|------------------|
| Search/Find | 🔍, magnifying glass, map |
| Generate/Create | 🤖, robot, magic wand |
| Send/Deliver | 📧, envelope, arrow |
| Complete/Success | ✅, handshake, trophy |
| Analyze | 📊, chart, graph |
| Configure | ⚙️, gear, settings |

## File Structure

```
flowchart-slides/
├── SKILL.md                    # This file
├── assets/
│   ├── template.html          # Base HTML template
│   ├── styles.css             # Core styles
│   └── illustrations/         # SVG icons (optional)
└── references/
    └── EXAMPLES.md            # More examples
```

## Usage Example

**User request:** "Create a 4-step guide for using AI to write blog posts"

**Output:**
1. Step 1: 输入主题 → 📝 keyboard icon
2. Step 2: AI生成 → 🤖 robot icon
3. Step 3: 编辑优化 → ✏️ pencil icon
4. Step 4: 发布分享 → 🚀 rocket icon

## Advanced Customization

For more options, see:
- [EXAMPLES.md](references/EXAMPLES.md) - Complete slide examples
