# 🏠 安居房屋租赁平台 · 前端

基于 **Vue 3 + Vite + Element Plus** 的房屋租赁平台前端，包含**租客端 / 房东端 / 管理后台**三套界面，支持深色/浅色主题、滚动入场动画、内置 AI 租赁助手。

## 技术栈

- Vue 3（Composition API + `<script setup>`）
- Vue Router（history 模式）
- Element Plus（含暗色主题）
- Axios
- Vite

## 功能概览

- **租客端**：房源搜索/筛选、收藏、预约、下单支付、报修、评价、纠纷、好友聊天、个人中心
- **房东端**：房源管理、房态日历、订单、账单、评价、维修、营销
- **管理后台**：用户/房源/订单/公告/轮播图/纠纷/数据统计
- **通用**：账号/手机号注册登录、深色主题切换、AI 租赁助手、滚动动画

## 本地运行

```sh
npm install
npm run dev
```

默认访问 `http://localhost:5173`，后端接口默认 `http://localhost:8080/api`。

## 生产构建

```sh
npm run build
```

产物在 `dist/` 目录。

## 环境变量

复制 `.env.example` 为 `.env` 后按需修改：

| 变量 | 说明 |
|---|---|
| `VITE_API_BASE_URL` | 后端 API 地址，例如 `https://api.example.com/api` |

## 部署

前端是纯静态站点，构建后 `dist/` 可部署到任意静态托管：

- **Nginx**（推荐，前后端同机）：见 `nginx.conf.example`
- Vercel / Netlify：导入仓库，构建命令 `npm run build`，输出目录 `dist`

> ⚠️ 使用了 history 路由模式，静态服务器必须把未知路径重写回 `index.html`（SPA fallback），否则刷新子页面会 404。

## 相关仓库

- 后端仓库：`hotel-1.2/demo`（Spring Boot 3 + MyBatis-Plus）

