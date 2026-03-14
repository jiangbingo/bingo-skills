# Flowchart Slides Examples

## Example 1: AI Writing Workflow (4 Steps)

```html
<!-- Replace placeholders in template.html -->
{{TITLE}} = AI 写作工作流
{{SUBTITLE}} = 让 AI 帮你高效创作内容

Step 1:
- Icon: 📝
- Title: 输入主题
- Desc: 描述你想要写的文章主题和目标受众

Step 2:
- Icon: 🤖
- Title: AI 生成
- Desc: AI 自动生成初稿，包含大纲和核心内容

Step 3:
- Icon: ✏️
- Title: 编辑优化
- Desc: 根据需要调整风格、添加个人观点

Step 4:
- Icon: 🚀
- Title: 发布分享
- Desc: 一键发布到各大平台，触达读者
```

## Example 2: Product Demo (5 Steps)

```html
{{TITLE}} = 产品使用指南
{{SUBTITLE}} = 5分钟上手我们的产品

Step 1:
- Icon: 🔍
- Title: 发现商家
- Desc: 搜索并找到你的目标本地商家

Step 2:
- Icon: 🌐
- Title: 自动建站
- Desc: AI 一键生成专业营销网站

Step 3:
- Icon: 📧
- Title: 发送推广
- Desc: 自动发送个性化营销邮件

Step 4:
- Icon: 📊
- Title: 数据分析
- Desc: 实时查看推广效果和转化数据

Step 5:
- Icon: ✅
- Title: 成交转化
- Desc: 处理异议，完成销售闭环
```

## Example 3: Learning Path (6 Steps)

```html
{{TITLE}} = 编程入门路径
{{SUBTITLE}} = 从零开始学编程的完整路线

Step 1:
- Icon: 💻
- Title: 选择语言
- Desc: Python/JavaScript/Go 选择一门入门

Step 2:
- Icon: 📚
- Title: 学习基础
- Desc: 掌握变量、循环、函数等核心概念

Step 3:
- Icon: 🔨
- Title: 动手实践
- Desc: 完成小项目巩固所学知识

Step 4:
- Icon: 🗄️
- Title: 数据结构
- Desc: 学习数组、链表、树等常用结构

Step 5:
- Icon: 🌐
- Title: 框架应用
- Desc: 学习主流框架开发实际应用

Step 6:
- Icon: 🎯
- Title: 项目实战
- Desc: 独立完成完整项目，准备求职
```

## Icon Reference by Category

### Search & Discovery
| Icon | Use Case |
|------|----------|
| 🔍 | Search, find, discover |
| 🗺️ | Map, location, navigate |
| 👀 | View, observe, analyze |
| 🎯 | Target, goal, focus |

### Creation & Generation
| Icon | Use Case |
|------|----------|
| 🤖 | AI, automation, robot |
| ✨ | Magic, generate, create |
| 🎨 | Design, customize, style |
| ⚡ | Quick, fast, instant |

### Communication
| Icon | Use Case |
|------|----------|
| 📧 | Email, send, message |
| 📱 | Mobile, SMS, notify |
| 📢 | Announce, broadcast |
| 💬 | Chat, conversation |

### Processing
| Icon | Use Case |
|------|----------|
| ⚙️ | Configure, settings |
| 🔄 | Process, cycle, loop |
| 📊 | Analyze, data, metrics |
| 🔧 | Fix, repair, maintain |

### Completion
| Icon | Use Case |
|------|----------|
| ✅ | Done, complete, success |
| 🎉 | Celebrate, achievement |
| 🏆 | Win, award, top |
| 🚀 | Launch, deploy, ship |

### Content
| Icon | Use Case |
|------|----------|
| 📝 | Write, edit, note |
| 📄 | Document, file, page |
| 🖼️ | Image, media, visual |
| 📹 | Video, record, stream |

## Color Customization

### Tech Theme
```css
--card-1: #E8F4FD;  /* Blue */
--card-2: #E8F8F5;  /* Teal */
--card-3: #F0F4F8;  /* Slate */
--card-4: #E8F5E9;  /* Green */
```

### Warm Theme
```css
--card-1: #FFF3E0;  /* Orange */
--card-2: #FCE4EC;  /* Pink */
--card-3: #FFF8E1;  /* Amber */
--card-4: #FFEBEE;  /* Red */
```

### Cool Theme
```css
--card-1: #E8EAF6;  /* Indigo */
--card-2: #E1F5FE;  /* Light Blue */
--card-3: #E0F2F1;  /* Teal */
--card-4: #F3E5F5;  /* Purple */
```

## Layout Variations

### Horizontal (4-6 steps)
```css
.steps-container {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}
```

### Vertical (3-4 steps)
```css
.steps-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.step-card {
  width: 100%;
  max-width: 500px;
}
```

### Grid (6+ steps)
```css
.steps-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
```
