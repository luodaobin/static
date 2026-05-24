# AGENT 规范 — 静态个人展示网站

本文件定义 AI Agent 在维护本项目时必须遵守的所有规则。

---

## 1. 项目定位

纯静态（HTML/CSS/JS）个人展示网站，部署在 Netlify，源码托管于 GitHub。
- 远程仓库：`https://github.com/luodaobin/static.git`
- 部署分支：`main`
- 技术栈：无框架，可选 Tailwind CDN，优先手写 CSS

---

## 2. 工程结构规范

```
static/
├── index.html              # 首页：导航页，自动渲染所有主题
├── assets/                 # 公共静态资源
│   ├── css/common.css      # 全局样式（导航、通用布局、响应式）
│   └── js/nav.js           # 主题列表 + 导航/卡片渲染逻辑
├── [主题名]/               # 每个主题独立目录（kebab-case 或小写）
│   ├── index.html          # 主题首页（含基础骨架 + 专属样式引入）
│   ├── assets/             # 主题专属 css/js/images
│   │   ├── css/
│   │   │   └── [主题].css
│   │   └── js/
│   │       └── [主题].js
│   └── README.md           # 主题说明（可选）
├── .gitignore
├── netlify.toml            # Netlify 部署配置（禁止随意修改）
├── AGENT.md                # 本文件
└── README.md               # 项目总说明
```

### 2.1 首页（index.html）规则
- 必须保持纯静态骨架，`nav.js` 负责动态渲染导航和主题卡片。
- 导航栏固定在顶部，背景使用 `backdrop-filter: blur()` 毛玻璃效果。
- 主题展示区域使用网格布局（`auto-fill, minmax(280px, 1fr)`），响应式适配移动端。
- 新增主题时，**必须同步更新 `nav.js` 中的 `themes` 数组**，而非直接修改 `index.html` 的 HTML。

### 2.2 nav.js 数据契约

```js
const themes = [
  // { name: "目录名", label: "展示名", desc: "简短描述" }
];
```

- **name**：主题目录名，必须与磁盘目录名完全一致，用于拼接链接 `./${name}/index.html`。
- **label**：导航栏和卡片上显示的名称。
- **desc**：卡片下方的简短描述（可选）。
- **排序**：数组顺序 = 创建时间顺序，新主题追加到数组末尾。

---

## 3. 创建新主题的执行逻辑

当用户说「我要创建一个 XXX 主题」时，按以下顺序执行：

### Step 1 — 变更清单确认
输出本次变更清单（目录、文件、需修改的现有文件）。

### Step 2 — 创建目录与文件
1. 在根目录新建 `XXX/` 目录（用户给的名称，统一转小写/kebab-case）。
2. 创建 `XXX/index.html`：
   - 包含完整 HTML5 骨架（lang="zh-CN", viewport, charset）。
   - 引入 `../assets/css/common.css` 保持导航一致性。
   - 引入 `assets/css/xxx.css` 作为主题专属样式。
   - 导航栏结构与首页一致，由 `nav.js` 渲染，或至少保留返回首页的链接。
   - 页面内容需体现该主题的独特风格（不能全站千篇一律）。
3. 创建 `XXX/assets/css/xxx.css`：主题专属样式。
4. （可选）创建 `XXX/assets/js/xxx.js` 和 `XXX/README.md`。

### Step 3 — 更新首页数据
编辑 `assets/js/nav.js`，在 `themes` 数组末尾追加：
```js
{ name: "xxx", label: "XXX", desc: "用户提供的描述或 AI 生成的简短说明" }
```

### Step 4 — 输出 Git 指令
```bash
git add .
git commit -m "feat: 添加XXX主题"
git push origin main
```

---

## 4. 风格与质量要求

- **首页风格**：现代、精美、大气。使用渐变、毛玻璃、圆角、微阴影、悬浮动效。
- **主题差异化**：每个主题必须有自己独特的配色或排版语言，禁止所有主题复制同一份 CSS。
- **响应式**：PC / 移动端自适应，导航栏在移动端变为汉堡菜单。
- **兼容性**：Chrome / Firefox / Safari / Edge 最新两版。
- **静态性**：不引入 Node 构建步骤，不生成需要编译的资源（除非用户明确要求）。

---

## 5. Git 与发布规则

### 5.1 远程仓库
- URL：`https://github.com/luodaobin/static.git`
- 分支：`main`（或 `master`，以本地初始化结果为准，优先 `main`）

### 5.2 首次初始化指令（当仓库未初始化时输出）
```bash
git init
git remote add origin https://github.com/luodaobin/static.git
git add .
git commit -m "init: 初始化静态个人展示网站"
git branch -M main
git push -u origin main
```

### 5.3 每次变更后输出
```bash
git add .
git commit -m "feat: 添加XXX主题"
git push origin main
```

### 5.4 Netlify 配置（netlify.toml）
禁止随意修改以下配置：
```toml
[build]
  publish = "."
  command = ""
[build.environment]
  NODE_VERSION = "18"
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

发布流程说明：
1. 在 Netlify 添加站点，关联 GitHub 仓库 `luodaobin/static`。
2. 构建设置：发布目录 `.`，构建命令留空。
3. 开启「自动部署」后，`main` 分支新提交会自动触发发布。

---

## 6. 验证 checklist（每次操作后自检）

- [ ] 主题目录已创建（`XXX/` 存在）。
- [ ] 主题包含 `index.html` 和专属样式。
- [ ] `nav.js` 中 `themes` 数组已追加新主题，且顺序正确。
- [ ] 首页导航渲染后包含新主题链接。
- [ ] `.gitignore` 已排除 `node_modules`、`.env`、IDE 文件。
- [ ] `netlify.toml` 完整且正确。
- [ ] Git 提交信息遵循约定式提交（`feat:` 添加主题）。

---

## 7. 禁止事项

- 禁止引入 React/Vue/Angular 等前端框架（保持纯静态）。
- 禁止在 `index.html` 中硬编码主题导航（必须通过 `nav.js` 渲染）。
- 禁止修改 `netlify.toml` 中的 `publish` 和 `command` 字段。
- 禁止在主题目录中使用中文目录名（URL 不安全），统一用英文/kebab-case。
