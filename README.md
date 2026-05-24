# 静态个人展示网站

一个纯静态、多主题的个人展示站点，支持一键新增主题并自动同步导航。

## 目录结构

```
static/
├── index.html          # 首页（导航页）
├── assets/             # 公共静态资源
│   ├── css/
│   │   └── common.css  # 全局样式
│   └── js/
│       └── nav.js      # 导航与主题卡片渲染
├── [主题名]/           # 每个主题独立目录
│   ├── index.html      # 主题首页
│   ├── assets/         # 主题专属资源
│   └── README.md       # 主题说明（可选）
├── .gitignore
├── netlify.toml        # Netlify 部署配置
├── AGENT.md            # 项目规范与执行规则
└── README.md           # 本文件
```

## 快速开始

```bash
# 初始化 Git 并推送（首次）
git init
git remote add origin https://github.com/luodaobin/static.git
git add .
git commit -m "init: 初始化静态个人展示网站"
git push -u origin main
```

## 添加新主题

执行 `git add . && git commit -m "feat: 添加XXX主题"` 后推送即可。

## 部署

本仓库已配置 Netlify 自动部署：
1. 在 Netlify 关联 GitHub 仓库 `luodaobin/static`
2. 构建设置：发布目录为根目录，构建命令留空
3. 开启自动部署后，每次 `main` 分支推送将自动发布
