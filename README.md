# 记账软件 (Accounting)

一款面向个人用户的跨平台记账应用，支持 Web 端和 Android 端，共用后端服务。

## 功能特点

### 基础记账
- 快速记账，支持多种收支类型
- 自定义分类和标签管理
- 支持为账单添加详细备注
- 批量数据导入导出（JSON/Excel）

### 数据分析
- 收支概览：总收支、结余等财务状况
- 分类统计：按分类分析收支情况
- 趋势分析：月度、年度收支对比
- 余额趋势：追踪账户余额变化

### AI 智能记账
- 自然语言输入，AI 自动解析并创建账单
- 智能分类，自动识别账单类型
- 支持配置多种 AI 大模型（OpenRouter）

### 账户管理
- 多账户支持（现金、银行卡、信用卡等）
- 账户余额自动计算

## 技术栈

| 端 | 技术 |
|---|------|
| Web 前端 | Vue 3 + TypeScript + Vite + Pinia |
| Android | Kotlin + Jetpack Compose + Material3 |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | SQLite |

## 项目结构

```
accounting/
├── android/          # Android 应用
├── web/             # Web 前端
├── server/          # 后端服务
├── docs/            # 文档
├── build-apk.ps1    # Android 打包脚本 (Windows)
├── build-apk.sh     # Android 打包脚本 (Linux/macOS)
├── deploy.ps1       # 部署脚本 (Windows)
└── deploy.sh        # 部署脚本 (Linux/macOS)
```

## 快速开始

### 后端启动

```bash
cd server
pip install -r requirements.txt
python run.py
```

后端服务将在 http://localhost:8000 启动

### Web 前端

```bash
cd web
npm install
npm run dev
```

访问 http://localhost:5173

### Android 应用

使用打包脚本构建 APK：

**Windows:**
```powershell
.\build-apk.ps1
```

**Linux/macOS:**
```bash
chmod +x build-apk.sh
./build-apk.sh
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的 API 文档。

## 部署

详见 `记账软件需求文档.md`

## License

MIT