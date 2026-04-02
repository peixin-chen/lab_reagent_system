# 实验室试剂管理系统 — 代码说明文档

> Flask + SQLite 后端 · Bootstrap 5 前端

---

## 目录

1. [项目概述](#1-项目概述)
2. [文件目录结构](#2-文件目录结构)
3. [后端文件详解](#3-后端文件详解)
4. [蓝图（业务逻辑）详解](#4-蓝图业务逻辑详解)
5. [前端模板详解](#5-前端模板详解)
6. [核心业务逻辑流程](#6-核心业务逻辑流程)
7. [常见修改指南](#7-常见修改指南)
8. [版本更新记录](#8-版本更新记录)
9. [部署与启动](#9-部署与启动)
10. [依赖版本说明](#10-依赖版本说明)

---

## 1. 项目概述

本系统是一套基于 Python Flask 框架开发的实验室试剂管理 Web 应用，使用 SQLite 数据库存储数据，前端使用 Bootstrap 5 构建响应式界面，可同时兼容手机和电脑访问。

### 1.1 主要功能

- **用户注册与登录**：支持用户名、姓名、密码自助注册；区分普通用户和管理员账户。
- **试剂库存管理**：以试剂柜为单位分组展示试剂，支持入库、领用操作，数量变化自动记录。
- **试剂搜索**：支持按试剂名称、CAS 号或货号进行模糊搜索，搜索结果同样支持入库/领用操作。
- **耗尽提醒**：试剂领用归零后自动生成提醒卡片，支持直接从提醒处补货入库。
- **CSV 导出**：所有登录用户均可按试剂柜导出试剂清单。
- **管理员功能**：管理用户、管理试剂柜（增删改）、查看操作记录、删除试剂/提醒。

### 1.2 技术栈

| 类别 | 技术/库 | 用途 |
|------|---------|------|
| 后端语言 | Python 3 | 程序运行环境 |
| Web 框架 | Flask 3.x | HTTP 路由、请求处理 |
| 数据库 ORM | Flask-SQLAlchemy 3.x | 数据库模型定义与查询 |
| 认证 | Flask-Login 0.6 | 用户会话与登录状态管理 |
| 数据库 | SQLite | 轻量级文件型数据库 |
| 前端 UI | Bootstrap 5.3 | 响应式布局与组件 |
| 图标 | Bootstrap Icons 1.11 | 界面图标 |

---

## 2. 文件目录结构

项目采用 Flask 蓝图（Blueprint）架构，将不同功能分拆到独立文件，便于维护和扩展。

```
lab_reagent/
├── run.py                  # ① 程序启动入口
├── app.py                  # ② Flask 应用工厂，初始化扩展与蓝图
├── config.py               # ③ 配置项（密钥、数据库路径、Cookie 时长）
├── extensions.py           # ④ 扩展实例（db、login_manager）
├── models.py               # ⑤ 数据库模型（表结构定义）
├── requirements.txt        # ⑥ Python 依赖列表
├── blueprints/
│   ├── __init__.py         # 空文件，使目录成为 Python 包
│   ├── auth.py             # ⑦ 认证蓝图：登录、注册、退出
│   ├── main.py             # ⑧ 主页蓝图：试剂列表、搜索、CSV 导出
│   ├── reagent.py          # ⑨ 试剂操作蓝图：入库、领用、新增、补货
│   └── admin.py            # ⑩ 管理员蓝图：用户/试剂柜/记录管理
├── templates/
│   ├── base.html           # 公共布局（导航栏、Flash 消息、脚本引入）
│   ├── login.html          # 登录页面
│   ├── register.html       # 注册页面
│   ├── index.html          # 主页（试剂表格 + 耗尽提醒）
│   ├── search.html         # 搜索结果页
│   └── admin/
│       ├── dashboard.html  # 管理控制面板
│       ├── users.html      # 用户管理
│       ├── cabinets.html   # 试剂柜管理
│       └── records.html    # 操作记录（分页）
└── static/
    ├── css/style.css       # 自定义全局样式
    └── js/main.js          # 全局 JavaScript（密码切换、防重提交等）
```

---

## 3. 后端文件详解

### 3.1 config.py — 配置文件

存放所有可调整的系统配置项，是修改系统行为最常用的入口。

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SECRET_KEY` | `'lab-reagent-secret-key-2024'` | 用于 Session 签名，**生产环境务必修改**为复杂随机字符串 |
| `SQLALCHEMY_DATABASE_URI` | `'sqlite:///lab_reagent.db'` | 数据库路径，SQLite 文件存储在项目根目录 |
| `REMEMBER_COOKIE_DURATION` | 未设置（默认 365 天） | 登录记住时长，可添加此项并设置为 `timedelta(days=30)` 等 |

> 💡 如需修改登录记住时长，在 `config.py` 顶部添加 `from datetime import timedelta`，然后在 `Config` 类中添加 `REMEMBER_COOKIE_DURATION = timedelta(days=30)`。

### 3.2 extensions.py — 扩展实例

创建 `db`（数据库）和 `login_manager`（登录管理器）的实例，但不在此处初始化（防止循环导入）。实际初始化在 `app.py` 的 `create_app()` 中完成。这是 Flask 项目的标准分离写法。

### 3.3 models.py — 数据模型

定义所有数据库表结构（SQLAlchemy ORM 模型）。共有 5 张表：

| 模型类名 | 对应表名 | 存储内容 |
|----------|----------|----------|
| `User` | `users` | 用户账号信息：用户名、姓名、密码哈希、是否管理员 |
| `Cabinet` | `cabinets` | 试剂柜信息：名称、位置、备注 |
| `Reagent` | `reagents` | 试剂条目：名称、CAS 号、货号、规格、数量、所属试剂柜、最近入库/领用时间 |
| `StockRecord` | `stock_records` | 每次入库或领用的操作记录，保存试剂名称、CAS、货号、规格等快照信息，试剂删除后记录保留（外键置空） |
| `DepletionAlert` | `depletion_alerts` | 试剂耗尽提醒：保存耗尽试剂的名称/CAS/货号/规格/所属试剂柜 |

> 💡 数据库文件 `lab_reagent.db` 在首次运行时自动创建，无需手动建表。删除该文件后，下次启动会重建空数据库（包括默认管理员账号）。

### 3.4 app.py — 应用工厂

使用工厂函数 `create_app()` 创建 Flask 应用实例，主要完成以下工作：

1. 初始化数据库（`db`）和登录管理器（`login_manager`）。
2. 注册两个 Jinja2 过滤器：`fmt_qty`（格式化数量，去除多余小数位）、`fmt_dt`（格式化时间为 `YYYY-MM-DD HH:MM`）。
3. 注册四个蓝图（`auth`、`main`、`reagent`、`admin`），其中 `reagent` 和 `admin` 带有 URL 前缀。
4. 调用 `db.create_all()` 建表，并通过 `_init_db()` 创建默认管理员账号（仅在不存在时创建）。

> 💡 如需更改默认管理员的用户名或密码，修改 `app.py` 中 `_init_db()` 函数内的 `username` 和 `generate_password_hash()` 参数，然后删除数据库文件重新启动即可。

---

## 4. 蓝图（业务逻辑）详解

### 4.1 auth.py — 认证蓝图

处理用户注册、登录、退出，URL 未设置前缀，直接挂载在根路径下。

| 路由 | 方法 | 功能说明 |
|------|------|----------|
| `/login` | GET / POST | 登录页面。POST 时校验用户名密码，成功后调用 `login_user()` 写入 Session Cookie |
| `/register` | GET / POST | 注册页面。POST 时校验各字段，用 `generate_password_hash()` 存储密码哈希 |
| `/logout` | GET | 退出登录，清除 Session，重定向到登录页 |

> 💡 密码从不以明文存储。`register` 时调用 `generate_password_hash()` 加密，`login` 时调用 `check_password_hash()` 验证，两者均来自 Werkzeug 库。

### 4.2 main.py — 主页蓝图

| 路由 | 方法 | 功能说明 |
|------|------|----------|
| `/` | GET | 主页。通过 URL 参数 `cabinet_id` 切换试剂柜，展示当前柜试剂列表和耗尽提醒 |
| `/search` | GET | 搜索页。接收 URL 参数 `q`，用 `ilike` 对名称、CAS 号和货号做不区分大小写的模糊查询 |
| `/export/cabinet/<id>` | GET | CSV 导出。将指定试剂柜的所有试剂信息导出为 CSV 文件，所有登录用户均可使用 |

**CSV 导出注意事项：**
- 文件带 UTF-8 BOM（`\ufeff`），Windows Excel 双击直接打开不会乱码。
- 文件名含中文（如"A柜_试剂清单.csv"），使用 RFC 5987 标准（`filename*=UTF-8''...`）对响应头进行编码，避免 HTTP 头 latin-1 编码报错。

### 4.3 reagent.py — 试剂操作蓝图（URL 前缀：`/reagent`）

处理所有试剂相关的增删操作，均为 POST 方法（表单提交），操作后重定向回来源页。

| 路由 | 功能说明 |
|------|----------|
| `/reagent/add` | 新增试剂。若名称+规格+CAS+货号完全匹配已有试剂，则改为执行入库操作，不重复建条目 |
| `/reagent/stock_in/<id>` | 入库操作。增加指定试剂的数量，更新 `last_stock_in` 时间，写入 `StockRecord` |
| `/reagent/withdrawal/<id>` | 领用操作。减少数量；若归零则删除试剂条目并创建 `DepletionAlert`；若不足则报错 |
| `/reagent/restock_alert/<id>` | 从耗尽提醒补货。重建试剂条目（或累加到已有同名试剂），然后删除该提醒 |

> 💡 领用逻辑中，判断是否归零使用的是 `new_qty <= 1e-9`（极小正数），而非精确等于 `0`，这是为了避免浮点数精度误差导致应该归零却未触发的问题。

### 4.4 admin.py — 管理员蓝图（URL 前缀：`/admin`）

所有路由均受 `@admin_required` 装饰器保护，非管理员访问会被拒绝并重定向主页。

| 路由 | 功能说明 |
|------|----------|
| `/admin/` | 控制面板。展示统计数据和最近 15 条操作记录 |
| `/admin/users` | 用户列表 |
| `/admin/users/delete/<id>` | 删除用户。删除前将其 `StockRecord` 记录的 `user_id` 置为 NULL，保留历史记录 |
| `/admin/cabinets` | 试剂柜列表 |
| `/admin/cabinets/add` | 新增试剂柜 |
| `/admin/cabinets/edit/<id>` | 修改试剂柜名称/位置/备注 |
| `/admin/cabinets/delete/<id>` | 删除试剂柜。通过 ORM cascade 配置，自动级联删除其下所有试剂和耗尽提醒 |
| `/admin/records` | 操作记录列表，支持按入库/领用筛选，每页 25 条分页显示 |
| `/admin/reagents/delete/<id>` | 删除试剂条目，可从主页或搜索页触发（通过隐藏字段 `ref` 区分来源） |
| `/admin/alerts/delete/<id>` | 删除耗尽提醒 |

---

## 5. 前端模板详解

所有页面模板均继承自 `base.html`，使用 Jinja2 的 `{% extends %}` / `{% block %}` 机制。

### 5.1 base.html — 公共布局

包含以下公共内容，所有页面自动继承：

- **顶部导航栏**：品牌 Logo、搜索框、主页链接、管理员下拉菜单、用户信息/退出按钮。
- **Flash 消息区**：展示后端 `flash()` 发出的提示信息，5 秒后自动消失（由 `main.js` 实现）。
- Bootstrap 5 CSS/JS 引入（CDN），Bootstrap Icons 引入，自定义 `style.css` 和 `main.js` 引入。
- `{% block content %}`：子模板在此处填充页面主体内容。
- `{% block scripts %}`：子模板在此处追加页面级 JavaScript。

### 5.2 index.html — 主页

主页是功能最复杂的模板，包含以下区域：

1. **页头按钮区**：右上角包含"导出 CSV"按钮（所有用户可见）和"新增试剂"按钮（选中试剂柜后显示）。
2. **试剂柜切换标签栏**：遍历所有试剂柜生成按钮，当前选中柜高亮，点击后通过 URL 参数 `cabinet_id` 切换。标签栏使用 `flex-wrap` 自动换行，手机端多个试剂柜时不再需要横向滚动。
3. **耗尽提醒卡片区**：遍历 `alerts` 列表，每张卡片显示试剂名/CAS/规格/耗尽时间，包含"补货"按钮和（管理员）删除按钮。
4. **试剂数据表格**：展示当前试剂柜的所有试剂，包括试剂名称、CAS 号、货号、规格、数量等信息；数量 ≤ 5 的行标黄色警告背景，每行有入库/领用/（管理员）删除按钮。
5. **模态框（4 个）**：新增试剂、入库、领用、补货——均为 Bootstrap Modal 弹窗，由页面底部 JavaScript 函数控制。

> 💡 表格在手机端会隐藏"规格""最近入库""最近领用"列（使用 Bootstrap 的 `d-none d-md-table-cell` / `d-none d-lg-table-cell` 类），将规格信息合并显示在试剂名称下方，确保手机可读。

### 5.3 search.html — 搜索页

结构与主页试剂表格类似，支持按试剂名称、CAS 号和货号搜索；结果表格额外增加了所属试剂柜列，并在每个操作表单中携带 `from_search` 隐藏字段，使入库/领用操作后能返回搜索结果而非主页。

### 5.4 管理员模板（admin/ 目录）

| 文件 | 特点说明 |
|------|----------|
| `dashboard.html` | 统计卡片（4 个）+ 快捷入口按钮 + 最近 15 条记录表格 |
| `users.html` | 用户列表，手机端合并角色信息到用户名下方，当前登录用户显示"当前用户"而非删除按钮 |
| `cabinets.html` | 卡片式布局展示试剂柜，每卡含编辑/删除/查看按钮，编辑通过模态框完成 |
| `records.html` | 带筛选（全部/入库/领用）和分页的操作记录表 |

---

## 6. 核心业务逻辑流程

### 6.1 入库流程

1. 用户点击主页/搜索结果中某试剂的"入库"按钮，前端 JavaScript 打开入库模态框，并将试剂 ID 填入表单 `action` 属性。
2. 用户输入入库数量后提交，POST 请求发送至 `/reagent/stock_in/<id>`。
3. 后端 `stock_in()` 函数：验证数量 > 0，执行 `reagent.quantity += quantity`，更新 `last_stock_in` 时间，调用 `_save_record()` 写入 `StockRecord`，提交数据库。
4. 重定向回来源页，Flash 显示成功提示。

### 6.2 领用与耗尽提醒流程

1. 与入库类似，POST 请求发送至 `/reagent/withdrawal/<id>`。
2. 计算新数量 `new_qty = reagent.quantity - quantity`。若 `new_qty < 0`，报错返回。
3. 若 `new_qty ≈ 0`（小于等于 1e-9）：先写入 `StockRecord`（保存历史），再创建 `DepletionAlert` 记录（保存试剂名/规格/CAS/试剂柜），最后删除 `Reagent` 条目。
4. 若 `new_qty > 0`：正常更新数量，写入记录。
5. 主页下次加载时，查询对应试剂柜的 `DepletionAlert` 并在页面顶部显示提醒卡片。

### 6.3 新增试剂的去重逻辑

用户填写新增试剂表单并提交至 `/reagent/add` 后，系统先查询当前试剂柜中是否存在名称（`name`）、规格（`specification`）、CAS 号（`cas_number`）三者完全一致的试剂：

- **若存在匹配项**：累加数量，更新入库时间，写入记录——相当于自动执行一次入库。
- **若不存在**：创建新的 `Reagent` 条目，同时写入初始入库记录。

> 💡 CAS 号为空时，系统将其与"CAS 号为空的试剂"进行匹配，不会将"无 CAS 号"的试剂与"有 CAS 号"的同名试剂视为相同。

---

## 7. 常见修改指南

### 7.1 修改登录记住时长

在 `config.py` 中添加：

```python
from datetime import timedelta

class Config:
    # ...原有配置...
    REMEMBER_COOKIE_DURATION = timedelta(days=30)  # 改为 30 天
```

常用时长写法：

| 写法 | 效果 |
|------|------|
| `timedelta(days=7)` | 7 天 |
| `timedelta(days=30)` | 30 天 |
| `timedelta(hours=8)` | 8 小时 |

如果不想使用持久化 Cookie（关闭浏览器即退出登录），可在 `blueprints/auth.py` 中将 `login_user(user, remember=True)` 改为 `login_user(user, remember=False)`。

### 7.2 修改默认管理员账号

找到 `app.py` 中的 `_init_db()` 函数，修改以下两处后删除数据库文件重启：

```python
username='admin',                           # 改为你想要的用户名
generate_password_hash('admin123'),         # 改为你想要的密码
```

### 7.3 修改低库存警告阈值

当前代码中"数量 ≤ 5"会将表格行标黄。修改 `templates/index.html` 和 `templates/search.html` 中以下两处（将 `5` 改为目标阈值）：

```html
{# 行背景色 #}
<tr class="{% if r.quantity <= 5 %}table-warning{% endif %}">

{# 数量徽章颜色 #}
{% elif r.quantity <= 5 %}bg-warning text-dark
```

### 7.4 新增一种管理员权限操作

1. 在 `blueprints/admin.py` 中添加新路由函数，加上 `@login_required` 和 `@admin_required` 装饰器。
2. 在对应的管理员模板中添加触发该路由的按钮或链接。
3. 若需要新页面，在 `templates/admin/` 目录下新建模板文件，并用 `{% extends 'base.html' %}` 继承。

### 7.5 更换数据库（MySQL / PostgreSQL）

只需修改 `config.py` 中的 `SQLALCHEMY_DATABASE_URI`，同时安装对应驱动：

```python
# MySQL 示例（需 pip install PyMySQL）
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/lab_reagent'

# PostgreSQL 示例（需 pip install psycopg2）
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/lab_reagent'
```

### 7.6 修改每页操作记录条数

在 `blueprints/admin.py` 中找到 `records()` 函数：

```python
pagination = q.order_by(...).paginate(page=page, per_page=25, ...)
```

将 `per_page=25` 改为所需数量即可。

### 7.7 手机端试剂柜按钮换行

当前 `templates/index.html` 中试剂柜标签栏使用 `flex-wrap`，试剂柜数量多时按钮自动换行，无需横向滚动。若要恢复横向滚动，将外层 `div` 加回 `overflow-auto`，并将内层改为 `flex-nowrap`。

---

## 8. 版本更新记录

### v1.2 更新内容

增加了操作文档供用户阅读。

### v1.1 更新内容

本版本主要围绕“试剂货号（product_number）”字段进行了功能扩展与文档同步，便于区分同名、同规格、同 CAS 但不同厂商或不同采购批次的试剂。

#### 8.1 新增字段

在试剂数据模型中新增了 **货号（product_number）** 字段，并同步扩展到以下业务数据中：

- `Reagent`：保存当前库存试剂的货号信息
- `StockRecord`：保存每次入库/领用操作对应的试剂货号
- `DepletionAlert`：保存耗尽提醒中的试剂货号

#### 8.2 新增/修改的功能

- **新增试剂**：表单中新增“货号”输入项
- **主页展示**：试剂列表新增“货号”列
- **搜索功能**：支持按“试剂名称 / CAS 号 / 货号”进行模糊搜索
- **耗尽提醒**：提醒信息中增加货号显示
- **补货逻辑**：从耗尽提醒补货时保留原试剂货号
- **CSV 导出**：导出文件中新增“货号”字段
- **操作记录**：入库/领用记录支持保存并展示货号信息

#### 8.3 业务逻辑调整

在 v1.0 中，系统判断“是否为同一种试剂”主要依据：

- 试剂名称
- CAS 号
- 规格
- 所属试剂柜

在 v1.1 中，判断条件调整为：

- 试剂名称
- CAS 号
- 货号
- 规格
- 所属试剂柜

也就是说，**即使名称、CAS 和规格相同，只要货号不同，系统也会将其视为不同试剂，不再自动合并库存。**

#### 8.4 数据库升级说明

由于系统已上线运行，新增字段后不能仅修改模型文件，还需要同步升级现有 SQLite 数据库表结构。

若数据库为旧版本，请执行以下 SQL：

```sql
ALTER TABLE reagents ADD COLUMN product_number VARCHAR(100);
ALTER TABLE stock_records ADD COLUMN product_number VARCHAR(100);
ALTER TABLE depletion_alerts ADD COLUMN product_number VARCHAR(100);
```

建议升级步骤：

- 先备份数据库文件 lab_reagent.db
- 执行上述 ALTER TABLE 语句
- 部署 v1.1 代码
- 重启系统并测试新增试剂、搜索、导出等功能

#### 8.5 兼容性说明

- 旧数据不会丢失
- 原有试剂记录的 product_number 默认可为空
- 未填写货号时，系统仍允许新增、搜索和导出
- 旧版本数据库若未执行升级 SQL，运行新版本代码时可能出现“字段不存在”的错误

---

## 9. 部署与启动

### 9.1 本地开发运行

```bash
# 1. 进入项目目录
cd lab_reagent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动（开发模式，支持自动重载）
python run.py

# 4. 浏览器访问
# http://localhost:5000
```

> 💡 首次启动会自动创建数据库文件 `lab_reagent.db` 和默认管理员账号（用户名 `admin`，密码 `admin123`），请登录后立即修改密码。

### 9.2 生产环境部署要点

- 将 `config.py` 中的 `SECRET_KEY` 改为足够复杂的随机字符串，不要使用默认值。
- 不要使用 Flask 内置开发服务器（`run.py`），应使用 Gunicorn 或 uWSGI 作为 WSGI 服务器。
- 生产环境推荐将 SQLite 换成 MySQL 或 PostgreSQL（见 7.5 节）。
- 通过 Nginx 或 Apache 做反向代理，并配置 HTTPS。

```bash
# 使用 Gunicorn 启动示例（需 pip install gunicorn）
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

---

## 10. 依赖版本说明

对应 `requirements.txt` 中的内容：

| 包名 | 版本 | 用途 |
|------|------|------|
| Flask | 3.0.3 | Web 框架核心，路由、请求、响应处理 |
| Flask-SQLAlchemy | 3.1.1 | SQLAlchemy ORM 与 Flask 的集成封装 |
| Flask-Login | 0.6.3 | 用户会话管理，提供 `login_user()`、`current_user` 等工具 |
| Werkzeug | 3.0.3 | Flask 底层依赖，提供密码哈希函数 `generate_password_hash` / `check_password_hash` |
| SQLAlchemy | 2.0.30 | ORM 引擎，由 Flask-SQLAlchemy 调用 |

> 💡 上述版本号为开发时使用版本，实际运行时小版本差异通常不影响功能。如遇兼容性问题，可统一升级到最新稳定版：`pip install --upgrade Flask Flask-SQLAlchemy Flask-Login`。
