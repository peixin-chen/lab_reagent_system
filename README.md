# 实验室试剂管理系统

> 基于 Flask + SQLite + Bootstrap 5 的实验室试剂库存管理系统
> 支持用户登录注册、试剂柜分类管理、试剂入库/领用、耗尽提醒、CSV 导出，以及管理员后台管理功能。

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [默认管理员账户](#默认管理员账户)
- [数据库模型说明](#数据库模型说明)
- [代码结构说明](#代码结构说明)
- [核心业务流程](#核心业务流程)
- [页面说明](#页面说明)
- [路由一览](#路由一览)
- [常见二次开发位置](#常见二次开发位置)
- [版本更新记录](#版本更新记录)
- [后续可优化方向](#后续可优化方向)

---

## 项目简介

本项目是一个面向实验室日常管理场景的 Web 系统，用于维护试剂库存信息。系统以**试剂柜**为分类单位管理试剂条目，支持：

- 用户注册、登录、退出
- 试剂新增、入库、领用
- 按试剂柜查看库存
- 按试剂名称 / CAS 号 / 货号搜索
- 试剂耗尽后自动生成补货提醒
- 导出某个试剂柜下的试剂清单 CSV
- 管理员后台查看统计数据、用户、试剂柜、操作记录
- 管理员直接在前台页面编辑试剂信息

系统前端基于 Bootstrap 5，兼容电脑端与手机端；后端使用 Flask + SQLAlchemy，默认数据库为 SQLite，开箱可运行。

---

## 功能特性

### 普通用户功能

- 登录 / 注册 / 退出
- 查看试剂柜列表
- 按试剂柜浏览试剂
- 搜索试剂（名称、CAS 号、货号）
- 新增试剂
- 对现有试剂执行入库
- 对现有试剂执行领用
- 导出试剂柜 CSV
- 查看用户操作手册

### 管理员功能

- 查看后台统计面板
- 查看全部用户并删除用户
- 新增 / 编辑 / 删除试剂柜
- 查看入库 / 领用操作记录（支持分页和筛选）
- 删除试剂
- 删除耗尽提醒
- **直接编辑试剂信息（v1.3 新增）**

---

## 技术栈

| 类别 | 技术 |
|---|---|
| 后端语言 | Python 3 |
| Web 框架 | Flask 3.0.3 |
| ORM | Flask-SQLAlchemy 3.1.1 / SQLAlchemy 2.0.30 |
| 登录认证 | Flask-Login 0.6.3 |
| 安全工具 | Werkzeug 3.0.3 |
| 数据库 | SQLite |
| 前端 UI | Bootstrap 5 |
| 图标 | Bootstrap Icons |

---

## 项目结构

```text
lab_reagent_system/
├── README.md
├── USER_DOC.md
└── lab_reagent_system/
    ├── app.py
    ├── config.py
    ├── extensions.py
    ├── models.py
    ├── requirements.txt
    ├── run.py
    ├── blueprints/
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── main.py
    │   ├── reagent.py
    │   └── admin.py
    ├── templates/
    │   ├── base.html
    │   ├── index.html
    │   ├── login.html
    │   ├── register.html
    │   ├── search.html
    │   └── admin/
    │       ├── dashboard.html
    │       ├── users.html
    │       ├── cabinets.html
    │       └── records.html
    └── static/
        └── docs/
            └── USER_DOC.pdf
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/peixin-chen/lab_reagent_system.git
cd lab_reagent_system/lab_reagent_system
```

### 2. 创建虚拟环境

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动项目

```bash
python run.py
```

默认运行地址：

```text
http://127.0.0.1:6700
```

或局域网访问：

```text
http://你的IP地址:6700
```

### 5. 首次启动说明

项目首次启动时会自动：

- 创建 SQLite 数据库文件 `lab_reagent.db`
- 自动建表
- 初始化默认管理员账户（若不存在）

---

## 配置说明

配置文件位于：

```python
lab_reagent_system/config.py
```

默认配置如下：

```python
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lab-reagent-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'lab_reagent.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### 可调整项

#### 修改密钥

生产环境建议通过环境变量设置：

```bash
export SECRET_KEY='your-secret-key'
```

#### 修改数据库

如切换为 MySQL：

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/lab_reagent'
```

如切换为 PostgreSQL：

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/lab_reagent'
```

---

## 默认管理员账户

默认管理员在 `app.py` 中初始化：

```python
username='admin'
password='admin123'
```

首次运行后若数据库中不存在该用户，会自动创建。

> 建议部署前自行修改默认账号密码，并删除旧数据库后重新初始化。

---

## 数据库模型说明

模型定义位于：

```python
lab_reagent_system/models.py
```

系统包含 5 张核心表。

### 1. User

用户表，用于登录认证和权限控制。

字段示例：

- `id`：主键
- `username`：用户名（唯一）
- `name`：姓名
- `password_hash`：密码哈希
- `is_admin`：是否管理员
- `created_at`：创建时间

### 2. Cabinet

试剂柜表。

字段示例：

- `id`
- `name`：试剂柜名称
- `location`：位置
- `description`：备注
- `created_at`

关系：

- 一个试剂柜下可以有多个 `Reagent`
- 一个试剂柜下可以有多个 `DepletionAlert`

### 3. Reagent

当前库存中的试剂表。

字段示例：

- `id`
- `name`：试剂名称
- `cas_number`：CAS 号
- `product_number`：货号
- `specification`：规格
- `quantity`：当前数量
- `cabinet_id`：所属试剂柜
- `last_stock_in`：最近入库时间
- `last_withdrawal`：最近领用时间
- `created_at`

### 4. StockRecord

库存操作记录表，保存每次入库或领用行为。

字段示例：

- `reagent_id`
- `reagent_name`
- `cas_number`
- `product_number`
- `specification`
- `cabinet_name`
- `user_id`
- `user_name`
- `quantity`
- `operation_type`：`in` 或 `out`
- `timestamp`

> 这里会保存操作时的试剂快照信息，因此即使试剂后来被删除，历史记录仍可保留。

### 5. DepletionAlert

耗尽提醒表。

字段示例：

- `reagent_name`
- `cas_number`
- `product_number`
- `specification`
- `cabinet_id`
- `created_at`

作用：

- 当试剂领用后数量归零，会删除库存条目并新增一条耗尽提醒
- 用户可根据提醒直接执行补货

---

## 代码结构说明

## 1. `run.py`

项目启动入口。

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6700)
```

作用：

- 调用应用工厂 `create_app()`
- 以调试模式启动服务
- 监听 `6700` 端口

---

## 2. `app.py`

Flask 应用工厂，负责组装整个应用。

主要职责：

- 创建 Flask 实例
- 加载配置
- 初始化 `db` 与 `login_manager`
- 注册自定义 Jinja2 过滤器
- 注册蓝图
- 建表
- 初始化默认管理员账号

### 关键点

#### （1）应用工厂模式

```python
def create_app(config_class=Config):
```

这种写法方便后续拆分环境配置、做测试或部署。

#### （2）登录管理器

```python
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录后再访问此页面'
```

未登录时访问需要权限的页面，会自动跳转到登录页。

#### （3）模板过滤器

- `fmt_qty`：格式化数量，去掉不必要的小数尾巴
- `fmt_dt`：格式化时间为 `YYYY-MM-DD HH:MM`

#### （4）初始化管理员

```python
def _init_db():
```

若数据库中不存在 `admin` 用户，则自动创建默认管理员。

---

## 3. `config.py`

集中管理配置项。

当前代码中已支持：

- `SECRET_KEY`
- `DATABASE_URL`
- `SQLALCHEMY_TRACK_MODIFICATIONS`

如果后续要增加：

- Session 生命周期
- 上传目录
- 日志配置
- 邮件配置

都建议继续放在这里统一管理。

---

## 4. `extensions.py`

用于放 Flask 扩展实例，避免循环导入。

```python
db = SQLAlchemy()
login_manager = LoginManager()
```

这是 Flask 项目里很常见的组织方式。

---

## 5. `models.py`

负责定义数据库表结构与模型关系。

这个文件的设计重点有两个：

### （1）库存表与记录表分离

`Reagent` 表只表示**当前库存状态**，而 `StockRecord` 表表示**历史操作行为**。
这样可以做到：

- 当前页展示简洁
- 历史记录不丢失
- 删除试剂后仍能保留操作历史

### （2）耗尽即删除库存条目

当某试剂领用至 0 时：

- 从 `Reagent` 删除
- 在 `DepletionAlert` 新建提醒

这样首页只展示“仍有库存”的试剂，逻辑更清晰。

---

## 6. `blueprints/auth.py`

负责用户认证相关逻辑。

### 路由

- `/login`
- `/register`
- `/logout`

### 主要逻辑

#### 登录

- 读取用户名与密码
- 查询用户
- 用 `check_password_hash()` 验证密码
- 成功后 `login_user(user, remember=True)`

#### 注册

- 校验用户名、姓名、密码、确认密码
- 检查用户名是否重复
- 使用 `generate_password_hash()` 存储加密密码

#### 退出

- 调用 `logout_user()`
- 返回登录页

---

## 7. `blueprints/main.py`

负责普通用户主流程页面。

### 路由

- `/`：主页
- `/search`：搜索页
- `/export/cabinet/<int:cabinet_id>`：导出 CSV
- `/user-doc`：下载用户操作手册 PDF

### 主要逻辑

#### 首页 `index()`

- 查询所有试剂柜
- 根据 `cabinet_id` 确定当前试剂柜
- 查询该柜下所有试剂
- 查询该柜下所有耗尽提醒
- 渲染 `index.html`

#### 搜索 `search()`

支持对以下字段做模糊搜索：

- `Reagent.name`
- `Reagent.cas_number`
- `Reagent.product_number`

#### CSV 导出 `export_cabinet()`

导出逻辑做了两个细节优化：

1. 写入 UTF-8 BOM，避免 Windows Excel 打开乱码
2. 对中文文件名使用 RFC 5987 编码，避免响应头报错

#### 用户手册 `user_doc()`

从：

```text
static/docs/USER_DOC.pdf
```

中直接返回 PDF 文件，供登录用户查看。

---

## 8. `blueprints/reagent.py`

这是项目最核心的业务文件，负责所有试剂相关操作。

### 路由

- `/reagent/add`
- `/reagent/edit/<int:reagent_id>`
- `/reagent/stock_in/<int:reagent_id>`
- `/reagent/withdrawal/<int:reagent_id>`
- `/reagent/restock_alert/<int:alert_id>`

### 8.1 `_save_record()`：统一保存操作记录

该辅助函数会在以下场景复用：

- 新增试剂
- 入库
- 领用
- 补货

这样能避免重复代码，也保证记录表格式统一。

---

### 8.2 `add()`：新增试剂

新增时不是无脑插入，而是先执行**去重判断**。

去重条件为：

- 同一试剂柜
- 名称相同
- 规格相同
- CAS 相同
- 货号相同

#### 结果分两种

- **已存在**：不新建条目，直接累加数量，等价于自动入库
- **不存在**：创建新试剂，并写入初始入库记录

这个设计能有效避免重复试剂条目污染库存数据。

---

### 8.3 `edit()`：编辑试剂（v1.3 新增重点）

这是 v1.3 新增的重要功能。

特点：

- 只有管理员可编辑
- 支持修改：
  - 试剂名称
  - CAS 号
  - 货号
  - 规格
  - 数量
- 会检查编辑后是否和同试剂柜中的其它试剂重复
- 若从搜索页进入编辑，会借助 `from_search` 参数返回搜索页
- 若从首页进入编辑，则返回原试剂柜页面

这部分配合 `index.html` 和 `search.html` 中新增的“编辑”按钮与编辑模态框使用。

---

### 8.4 `stock_in()`：入库

逻辑：

1. 校验数量必须大于 0
2. 累加 `reagent.quantity`
3. 更新 `last_stock_in`
4. 写入 `StockRecord`
5. 返回原页面

---

### 8.5 `withdrawal()`：领用

逻辑：

1. 校验数量必须大于 0
2. 计算领用后剩余量 `new_qty`
3. 如果库存不足，直接报错
4. 写入操作记录
5. 分两种情况处理：

#### 情况 A：仍有剩余

- 更新数量
- 更新 `last_withdrawal`

#### 情况 B：领用后归零

- 创建 `DepletionAlert`
- 删除 `Reagent`
- 提示用户该试剂已耗尽，并生成补货提醒

> 代码中使用 `new_qty <= 1e-9` 判断是否视为归零，用来规避浮点数精度误差。

---

### 8.6 `restock_alert()`：从耗尽提醒补货

逻辑：

- 根据提醒信息重新恢复试剂
- 若对应试剂已存在，则直接累加数量
- 若不存在，则新建试剂
- 删除提醒
- 写入操作记录

这样用户可以从耗尽提醒直接完成“补货恢复库存”。

---

## 9. `blueprints/admin.py`

负责管理员后台管理。

### 权限控制

文件内定义了 `admin_required` 装饰器，用于拦截非管理员访问：

```python
def admin_required(f):
```

所有管理路由都要求：

- 已登录
- 是管理员

---

### 路由

- `/admin/`：控制台
- `/admin/users`
- `/admin/users/delete/<int:user_id>`
- `/admin/cabinets`
- `/admin/cabinets/add`
- `/admin/cabinets/edit/<int:cabinet_id>`
- `/admin/cabinets/delete/<int:cabinet_id>`
- `/admin/records`
- `/admin/reagents/delete/<int:reagent_id>`
- `/admin/alerts/delete/<int:alert_id>`

---

### 9.1 控制台 `dashboard()`

展示：

- 用户数量
- 试剂柜数量
- 当前试剂数量
- 耗尽提醒数量
- 最近 15 条操作记录

---

### 9.2 用户管理

- 按创建时间倒序显示用户
- 支持删除用户
- 删除前会把该用户历史记录中的 `user_id` 置空，保留记录内容
- 禁止删除当前登录用户自己

---

### 9.3 试剂柜管理

支持：

- 新增
- 编辑
- 删除

删除试剂柜时，由 ORM 的级联配置自动删除：

- 该试剂柜下所有试剂
- 该试剂柜下所有耗尽提醒

---

### 9.4 操作记录管理

- 支持按 `in` / `out` 筛选
- 支持分页
- 默认每页 25 条

---

### 9.5 删除试剂

删除试剂时，会先把对应历史记录里的 `reagent_id` 置为 `NULL`，再删当前库存条目，确保历史记录可继续展示。

如果删除入口来自搜索页，还会自动跳回原搜索结果。

---

### 9.6 删除耗尽提醒

管理员可删除提醒卡片，删除后返回所属试剂柜首页。

---

## 核心业务流程

## 1. 新增试剂

```text
提交新增表单
→ 校验字段
→ 查询是否已有相同试剂（同柜 + 名称 + CAS + 货号 + 规格）
→ 已存在：数量累加 + 写入记录
→ 不存在：创建试剂 + 写入记录
→ 返回页面
```

---

## 2. 入库流程

```text
点击“入库”
→ 打开模态框
→ 提交数量
→ 更新库存数量
→ 更新最近入库时间
→ 写入操作记录
→ 返回页面
```

---

## 3. 领用流程

```text
点击“领用”
→ 打开模态框
→ 提交数量
→ 校验库存是否足够
→ 写入操作记录
→ 若仍有库存：更新数量
→ 若已归零：创建耗尽提醒 + 删除试剂
→ 返回页面
```

---

## 4. 补货流程

```text
看到耗尽提醒
→ 点击“补货”
→ 输入补货数量
→ 若已有同试剂库存：累加
→ 否则重建试剂条目
→ 删除提醒
→ 写入操作记录
→ 返回页面
```

---

## 5. 编辑试剂流程（v1.3）

```text
管理员点击“编辑”
→ 打开编辑模态框
→ 修改名称/CAS/货号/规格/数量
→ 后端校验
→ 检查是否与同柜其他试剂重复
→ 保存修改
→ 返回首页或搜索页
```

---

## 页面说明

## `base.html`

所有页面的基础模板，负责：

- 顶部导航栏
- 搜索框
- Flash 消息提示
- Bootstrap / Icons / 公共脚本引入
- 公共布局结构

---

## `index.html`

系统主页，功能最完整。

包含：

- 当前试剂柜选择
- 试剂表格
- 耗尽提醒卡片
- 新增试剂模态框
- 入库模态框
- 领用模态框
- 补货模态框
- **编辑试剂模态框（v1.3）**

同时做了移动端适配，例如：

- 低优先级列在小屏幕上隐藏
- 多个试剂柜按钮自动换行
- 规格等信息在手机端合并展示

---

## `search.html`

搜索结果页。

特点：

- 支持显示所属试剂柜
- 可直接执行入库 / 领用 / 删除 / 编辑
- 使用隐藏字段 `from_search` 保证操作后仍回到搜索结果页

---

## `login.html` / `register.html`

分别对应登录页和注册页。

---

## `templates/admin/*`

管理员后台模板：

- `dashboard.html`：统计总览
- `users.html`：用户管理
- `cabinets.html`：试剂柜管理
- `records.html`：记录管理

---

## 路由一览

### 认证

| 路由 | 方法 | 说明 |
|---|---|---|
| `/login` | GET / POST | 登录 |
| `/register` | GET / POST | 注册 |
| `/logout` | GET | 退出 |

### 普通业务

| 路由 | 方法 | 说明 |
|---|---|---|
| `/` | GET | 首页 |
| `/search` | GET | 搜索 |
| `/export/cabinet/<int:cabinet_id>` | GET | 导出 CSV |
| `/user-doc` | GET | 下载用户手册 |

### 试剂操作

| 路由 | 方法 | 说明 |
|---|---|---|
| `/reagent/add` | POST | 新增试剂 |
| `/reagent/edit/<int:reagent_id>` | POST | 编辑试剂 |
| `/reagent/stock_in/<int:reagent_id>` | POST | 入库 |
| `/reagent/withdrawal/<int:reagent_id>` | POST | 领用 |
| `/reagent/restock_alert/<int:alert_id>` | POST | 根据提醒补货 |

### 管理后台

| 路由 | 方法 | 说明 |
|---|---|---|
| `/admin/` | GET | 控制台 |
| `/admin/users` | GET | 用户列表 |
| `/admin/users/delete/<int:user_id>` | POST | 删除用户 |
| `/admin/cabinets` | GET | 试剂柜列表 |
| `/admin/cabinets/add` | POST | 新增试剂柜 |
| `/admin/cabinets/edit/<int:cabinet_id>` | POST | 编辑试剂柜 |
| `/admin/cabinets/delete/<int:cabinet_id>` | POST | 删除试剂柜 |
| `/admin/records` | GET | 操作记录 |
| `/admin/reagents/delete/<int:reagent_id>` | POST | 删除试剂 |
| `/admin/alerts/delete/<int:alert_id>` | POST | 删除耗尽提醒 |

---

## 常见二次开发位置

### 修改默认管理员账号

文件：

```python
app.py
```

修改 `_init_db()` 中的用户名和密码哈希。

---

### 修改低库存预警阈值

文件：

- `templates/index.html`
- `templates/search.html`

将类似判断：

```jinja2
{% if r.quantity <= 5 %}
```

中的 `5` 改为你需要的阈值。

---

### 修改操作记录分页数量

文件：

```python
blueprints/admin.py
```

找到：

```python
paginate(page=page, per_page=25, error_out=False)
```

修改 `per_page` 即可。

---

### 修改监听端口

文件：

```python
run.py
```

修改：

```python
port=6700
```

---

### 修改数据库类型

文件：

```python
config.py
```

修改 `SQLALCHEMY_DATABASE_URI`。

---

### 新增一个管理员页面

建议步骤：

1. 在 `blueprints/admin.py` 中新增路由
2. 添加 `@login_required` 和 `@admin_required`
3. 在 `templates/admin/` 下新增模板
4. 在后台页面加入入口按钮

---

## 版本更新记录

### v1.3

- 新增：管理员可在主页和搜索页直接编辑试剂信息
- 前端新增编辑按钮与编辑模态框
- 后端新增 `/reagent/edit/<int:reagent_id>` 路由
- 编辑时会检查同试剂柜下是否出现重复试剂条目

### v1.2

- 增加用户操作文档

### v1.1

- 新增 `product_number`（货号）字段
- 搜索支持货号
- CSV 导出增加货号
- 耗尽提醒增加货号
- 操作记录保存货号
- 补货逻辑保留货号

---

## 后续可优化方向

如果后续继续迭代，这个项目还可以考虑增加：

- 低库存阈值可配置化
- 操作记录按用户 / 时间范围 / 试剂名筛选
- Excel 导出
- 图片上传（试剂标签、危险品标识）
- 权限分级（管理员 / 普通成员 / 访客）
- Docker 部署
- 单元测试与表单校验优化
- 数据库迁移工具（如 Flask-Migrate）
- API 化与前后端分离

---

## License

该项目当前仓库未单独声明 License。
如需开源发布，建议补充 `LICENSE` 文件并明确使用协议。
```

你这版 README 已经可以直接用。
如果你愿意，我下一步可以继续帮你做一版 **更适合 GitHub 展示风格的 README**，比如加上项目截图占位、功能流程图、徽章、部署说明和更漂亮的目录结构。