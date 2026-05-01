# 记账本 · 微信小程序

基于 Accounting 项目的微信小程序版本，通过 HTTP API 连接同一套 FastAPI 后端服务。

## 技术栈

- 微信原生框架（WXML + WXSS + JS）
- 自定义深色主题（#818CF8 主色调）

## 快速开始

1. 用微信开发者工具打开 `accounting-miniapp/` 目录
2. 在 `project.config.json` 中填入你的 `appid`
3. 确保后端服务已启动（默认 `http://localhost:8000`）
4. 开发环境中关闭"不校验合法域名"选项
5. 登录时填写后端服务器地址

## 项目结构

```
accounting-miniapp/
├── app.js              # 应用入口
├── app.json            # 全局配置（含 tabBar）
├── app.wxss            # 全局样式（CSS 变量）
├── project.config.json # 微信开发者工具配置
├── pages/
│   ├── index/          # 首页（收支概览 + 最近账单）
│   ├── bills/          # 账单列表（筛选 + 分页）
│   ├── add-bill/       # 记账页（数字键盘 + 分类选择）
│   ├── statistics/     # 统计页（分类占比 + 趋势）
│   ├── mine/           # 我的（账户/分类管理入口）
│   ├── accounts/       # 账户管理
│   ├── categories/     # 分类管理
│   └── login/          # 登录页
├── utils/
│   ├── request.js      # 网络请求封装
│   ├── api.js          # API 接口封装
│   ├── format.js       # 格式化工具
│   └── auth.js         # 认证管理
└── images/             # 图标资源
```

## 图标替换

`images/` 目录中的 tab 图标目前为 1x1 透明占位 PNG。你需要将它们替换为实际图标（81x81 px 的 PNG），或使用 iconfont 生成。

Tab 图标命名：
- `tab-home.png` / `tab-home-active.png` → 首页（灰色/紫色选中态）
- `tab-bills.png` / `tab-bills-active.png` → 账单
- `tab-stats.png` / `tab-stats-active.png` → 统计
- `tab-mine.png` / `tab-mine-active.png` → 我的

## 注意事项

- 需要先在微信公众平台注册小程序，获取 AppID
- 在 `project.config.json` 中填入你的 `appid`
- 服务器域名需在小程序后台配置（request 合法域名）
- 开发调试时可在开发者工具中勾选"不校验合法域名"
- 小程序不支持直接访问 localhost，请使用局域网 IP 或公网地址
- 后端需要创建至少一个用户（通过 Web 端注册或 admin 接口）
