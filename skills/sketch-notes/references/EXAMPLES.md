# Sketch Notes Examples

Complete examples for generating sketch-style presentations.

## Example 1: Developer Workflow (4 Steps)

```html
{{TITLE}} = 开发者工作流
{{SUBTITLE}} = 从想法到上线的完整流程

Step 1:
- Icon: 💡
- Title: <span class="highlight">需求分析</span>
- Desc: 理解需求，明确目标，制定计划

Step 2:
- Icon: 💻
- Title: 编码实现
- Desc: 编写代码，单元测试，代码审查

Step 3:
- Icon: 🔧
- Title: 测试部署
- Desc: 集成测试，预发验证，灰度发布

Step 4:
- Icon: 🚀
- Title: 上线监控
- Desc: 正式发布，性能监控，持续优化

{{SUMMARY}} = 每一步都很重要，保持专注，持续改进 ☕
```

## Example 2: Bug Fix Process (5 Steps)

```html
{{TITLE}} = Bug 修复指南
{{SUBTITLE}} = 工程师必备技能

Step 1:
- Icon: 🐛
- Title: <span class="highlight">复现问题</span>
- Desc: 确认Bug，收集日志，稳定复现

Step 2:
- Icon: 🔍
- Title: 定位根因
- Desc: 分析代码，找到问题源头

Step 3:
- Icon: ✏️
- Title: 编写修复
- Desc: 修改代码，添加测试用例

Step 4:
- Icon: ✅
- Title: 验证修复
- Desc: 本地测试，Code Review

Step 5:
- Icon: 🚀
- Title: 发布上线
- Desc: 合并代码，部署验证

{{SUMMARY}} = 好的Bug修复 = 彻底解决 + 防止回归 ✨
```

## Example 3: Code Review Checklist

```html
<!-- Special checklist variant -->

<div class="step-card">
  <span class="step-number">Code Review</span>
  <ul class="checklist">
    <li class="checked">代码逻辑正确</li>
    <li class="checked">命名清晰易懂</li>
    <li>单元测试覆盖</li>
    <li>无安全漏洞</li>
    <li>性能考虑周全</li>
  </ul>
</div>
```

## Example 4: Learning Path (6 Steps)

```html
{{TITLE}} = 前端学习路线
{{SUBTITLE}} = 从零到一的进阶指南

Step 1:
- Icon: 📝
- Title: HTML/CSS 基础
- Desc: 语义化标签，Flexbox，Grid布局

Step 2:
- Icon: ⚡
- Title: JavaScript 核心
- Desc: ES6+语法，DOM操作，异步编程

Step 3:
- Icon: ⚛️
- Title: React 框架
- Desc: 组件化开发，Hooks，状态管理

Step 4:
- Icon: 🎨
- Title: CSS 进阶
- Desc: 动画，响应式，CSS-in-JS

Step 5:
- Icon: 🛠️
- Title: 工程化工具
- Desc: Webpack，Vite，CI/CD

Step 6:
- Icon: 🚀
- Title: 项目实战
- Desc: 独立完成项目，准备作品集

{{SUMMARY}} = 持续学习，保持好奇，动手实践 📚
```

## Example 5: API Design Flow

```html
{{TITLE}} = API 设计流程
{{SUBTITLE}} = 构建优雅的接口

Step 1:
- Icon: 🎯
- Title: <span class="highlight">定义需求</span>
- Desc: 明确业务场景，梳理数据模型

Step 2:
- Icon: 📐
- Title: 设计规范
- Desc: RESTful风格，命名约定，版本管理

Step 3:
- Icon: 📝
- Title: 编写文档
- Desc: OpenAPI规范，示例代码，错误码

Step 4:
- Icon: 🔒
- Title: 安全考虑
- Desc: 认证授权，输入验证，限流控制

{{SUMMARY}} = 好的API设计 = 简洁 + 一致 + 可预测 ⚙️
```

## Color Theme Variations

### Vintage Sepia
```css
:root {
  --paper-bg: #F4ECD8;
  --coffee-stain: rgba(139, 90, 43, 0.18);
  --pencil-dark: #3D3229;
  --pencil-light: #6B5D4D;
}
```

### Blueprint Style
```css
:root {
  --paper-bg: #1A237E;
  --grid-line: rgba(255, 255, 255, 0.1);
  --pencil-dark: #FFFFFF;
  --pencil-light: #90CAF9;
  --blue-pencil: #FFEB3B;
}
```

### Green Engineer
```css
:root {
  --paper-bg: #C8E6C9;
  --coffee-stain: rgba(46, 125, 50, 0.15);
  --pencil-dark: #1B5E20;
  --pencil-light: #388E3C;
}
```

## Annotation Examples

Add handwritten-style annotations:

```html
<!-- Red pencil note -->
<span class="annotation" style="top: 20%; right: 10%;">
  ⬅ 重要！
</span>

<!-- Blue pencil note -->
<span class="annotation" style="bottom: 30%; left: 5%; color: var(--blue-pencil);">
  TODO: 添加更多细节
</span>

<!-- Highlighted text -->
<span class="highlight">关键步骤</span>
```

## Layout Variations

### Horizontal Steps
```css
.steps-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
}

.step-card {
  width: 200px;
}

.arrow-connector {
  display: inline-block;
  transform: rotate(-90deg);
}
```

### Two-Column Layout
```css
.steps-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 25px;
}

@media (max-width: 600px) {
  .steps-container {
    grid-template-columns: 1fr;
  }
}
```
