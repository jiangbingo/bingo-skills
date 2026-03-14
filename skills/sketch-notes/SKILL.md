---
name: sketch-notes
description: Generate hand-drawn sketch style HTML presentations with graph paper background and vintage engineer's notebook aesthetic. Creates authentic-looking workflow diagrams with doodle icons, coffee stains, and paper textures. Perfect for technical documentation, developer tutorials, and engineering process visualization. Triggers: 手绘笔记, 涂鸦风格, 网格纸背景, 工程师笔记, sketch slides, hand-drawn presentation, notebook style, retro technical docs, engineer's notebook, 涂鸦幻灯片, 复古文档, 铅笔风格.
license: MIT
compatibility: No dependencies - pure HTML/CSS
metadata:
  version: "1.0.0"
  author: jiangbingo
---

# Sketch Notes

Create authentic hand-drawn sketch style presentations that look like an engineer's notebook - complete with graph paper background, coffee stains, and doodle icons.

## Visual Style

| Element | Description |
|---------|-------------|
| **Background** | Light gray graph paper with subtle coffee stains and paper texture |
| **Visual Style** | Hand-drawn / doodle sketch, wobbly lines, stick figures |
| **Typography** | Handwritten fonts (Caveat, Patrick Hand, Kalam) |
| **Layout** | Vertical step-by-step cards, connected by hand-drawn arrows |
| **Colors** | Black/white/gray primary, warm accents (brown stains, red pencil, blue icons) |
| **Decorations** | Scattered doodles (laptop, gear, coffee cup, broom, pencil) |

## Quick Start

Use `assets/template.html` as base, customize for user's workflow.

## Color Palette

```css
/* Base - Graph Paper */
--paper-bg: #F5F5F0;
--grid-line: #E0E0E0;
--grid-major: #D0D0D0;

/* Stains & Textures */
--coffee-stain: rgba(139, 90, 43, 0.15);
--paper-aged: rgba(245, 245, 240, 0.95);
--shadow: rgba(0, 0, 0, 0.1);

/* Sketch Colors */
--pencil-dark: #2C2C2C;
--pencil-light: #666666;
--pencil-faint: #999999;
--red-pencil: #C62828;
--blue-pencil: #1565C0;
--green-pencil: #2E7D32;

/* Accent */
--highlight-yellow: #FFF59D;
--highlight-pink: #F8BBD9;
```

## Typography

```css
/* Primary handwritten font */
font-family: 'Caveat', cursive;

/* Alternative options */
font-family: 'Patrick Hand', cursive;
font-family: 'Kalam', cursive;
font-family: 'Shadows Into Light', cursive;
```

Load from Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;600;700&family=Patrick+Hand&family=Kalam:wght@300;400;700&display=swap" rel="stylesheet">
```

## Layout Structure

```
┌──────────────────────────────────────────────┐
│  ☕  ┌─────────────────────────────────┐     │
│      │        PAGE TITLE               │     │
│      │    (hand-written, large)        │  ✏️ │
│      └─────────────────────────────────┘     │
│  ⚙️                                           │
│      ┌─────────────────────────────────┐     │
│      │  Step 1: [DOODLE ICON]          │     │
│      │  ─────────────────────          │     │
│      │  Description text here...       │     │
│      └─────────────────────────────────┘     │
│      │              ↓                    💻  │
│      ┌─────────────────────────────────┐     │
│      │  Step 2: [DOODLE ICON]          │     │
│      │  ─────────────────────          │     │
│      │  Description text here...       │     │
│      └─────────────────────────────────┘     │
│                                              │
│      ~ Summary text at bottom ~         🔧  │
└──────────────────────────────────────────────┘
```

## Step Card Pattern

```html
<div class="step-card">
  <div class="step-number">Step 1</div>
  <div class="step-doodle">
    <!-- SVG doodle icon -->
  </div>
  <h3 class="step-title">Title Here</h3>
  <p class="step-desc">Description text...</p>
</div>

<!-- Hand-drawn arrow connector -->
<div class="arrow-connector">
  <svg><!-- wobbly arrow --></svg>
</div>
```

## Doodle Icon Library

### Tech & Development
| Icon | SVG | Use Case |
|------|-----|----------|
| 💻 Laptop | `<path d="M...">` | Development, coding |
| ⚙️ Gear | `<circle> + <path>` | Configuration, settings |
| 📁 Folder | `<rect> + <path>` | Files, projects |
| 🔧 Wrench | `<path>` | Tools, fixes |

### Communication
| Icon | SVG | Use Case |
|------|-----|----------|
| 📧 Envelope | `<rect> + <path>` | Email, messages |
| 💬 Bubble | `<path>` | Chat, comments |
| 📢 Megaphone | `<path>` | Announcements |

### Actions
| Icon | SVG | Use Case |
|------|-----|----------|
| ✏️ Pencil | `<path>` | Write, edit |
| 🔍 Magnifier | `<circle> + <line>` | Search, find |
| ▶️ Play | `<polygon>` | Start, execute |
| ✓ Check | `<path>` | Complete, done |

### Objects
| Icon | SVG | Use Case |
|------|-----|----------|
| ☕ Coffee | `<path>` | Break, energy |
| 💡 Bulb | `<path>` | Ideas, insights |
| 📊 Chart | `<rect>` | Data, metrics |

## Hand-drawn Effects

### Wobbly Lines
```css
/* Using SVG filter for sketch effect */
.wobbly-border {
  filter: url(#sketch-filter);
}

/* Or using border-radius variation */
.sketch-box {
  border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px;
  border: 2px solid var(--pencil-dark);
}
```

### Paper Texture
```css
.paper-texture {
  background-image:
    /* Coffee stains */
    radial-gradient(ellipse at 20% 80%, var(--coffee-stain) 0%, transparent 50%),
    radial-gradient(ellipse at 85% 15%, var(--coffee-stain) 0%, transparent 40%),
    /* Grid lines */
    linear-gradient(var(--grid-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px),
    /* Base */
    var(--paper-bg);
  background-size: 100% 100%, 100% 100%, 20px 20px, 20px 20px, 100% 100%;
}
```

### Pencil Style Text
```css
.pencil-text {
  color: var(--pencil-dark);
  font-family: 'Caveat', cursive;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* Red pencil highlight */
.red-pencil {
  color: var(--red-pencil);
}

/* Blue pencil annotation */
.blue-pencil {
  color: var(--blue-pencil);
}
```

## Workflow

1. **Gather requirements** - Topic, steps, target audience
2. **Select doodle icons** - Choose appropriate hand-drawn icons
3. **Apply paper texture** - Graph paper + coffee stains
4. **Add hand-drawn elements** - Wobbly borders, sketch lines
5. **Include scattered doodles** - Random icons for authenticity
6. **Review authenticity** - Should look like real engineer's notes

## File Structure

```
sketch-notes/
├── SKILL.md                    # This file
├── assets/
│   ├── template.html          # Complete HTML template
│   ├── doodles.svg           # SVG doodle icons library
│   └── textures.css          # Paper texture & effects
└── references/
    ├── DOODLES.md            # Icon reference
    └── EXAMPLES.md           # Complete examples
```

## More Resources

- [DOODLES.md](references/DOODLES.md) - Complete doodle icon library
- [EXAMPLES.md](references/EXAMPLES.md) - Full slide examples
