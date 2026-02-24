# SQL 查询工具

一个简单易用的 Web SQL 查询工具，支持在线执行 SQL 查询并导出结果。

## 功能特性

✨ **核心功能**
- 🔍 在线执行 SQL 查询
- 📊 实时显示查询结果
- ⬇️ 导出结果为 CSV 文件
- 🗄️ 自动显示数据库表结构
- 📝 查询日志记录

🎨 **用户体验**
- 美观的渐变色界面设计
- 响应式布局，支持各种屏幕尺寸
- 示例查询一键填充
- 支持快捷键 Ctrl/Cmd + Enter 执行查询
- 实时错误提示

🔒 **安全特性**
- 仅支持 SELECT 查询（只读模式）
- SQL 注入防护
- 查询审计日志

## 技术栈

**后端：**
- Python 3.x
- Flask 3.0
- SQLite 3

**前端：**
- HTML5 + CSS3
- 原生 JavaScript
- Fetch API

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

### 3. 访问应用

打开浏览器访问：`http://localhost:5000`

## 测试数据

应用启动时会自动创建两张测试表并插入数据：

### users 表
- id（主键）
- name（姓名）
- email（邮箱）
- age（年龄）
- city（城市）
- created_at（创建时间）

### orders 表
- id（主键）
- user_id（用户ID，外键）
- product（产品名称）
- amount（金额）
- status（状态）
- order_date（订单日期）

## 示例查询

```sql
-- 查询所有用户
SELECT * FROM users;

-- 查询已完成的订单
SELECT * FROM orders WHERE status = 'completed';

-- 联表查询用户订单信息
SELECT u.name, u.city, o.product, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id
ORDER BY o.amount DESC;

-- 按城市统计用户
SELECT city, COUNT(*) as user_count, AVG(age) as avg_age
FROM users
GROUP BY city;
```

## 文件结构

```
sql-query-app/
├── app.py                  # Flask 后端应用
├── templates/
│   └── index.html         # 前端页面
├── requirements.txt       # Python 依赖
├── README.md             # 说明文档
├── test_database.db      # SQLite 数据库（自动创建）
└── query_audit.log       # 查询日志（自动创建）
```

## API 接口

### 执行查询
- **URL**: `/execute`
- **方法**: `POST`
- **请求体**: `{"sql": "SELECT * FROM users"}`
- **返回**: 查询结果（JSON 格式）

### 下载结果
- **URL**: `/download`
- **方法**: `POST`
- **请求体**: `{"columns": [...], "data": [...]}`
- **返回**: CSV 文件

### 获取表信息
- **URL**: `/tables`
- **方法**: `GET`
- **返回**: 数据库表结构信息

## 安全说明

⚠️ **重要提示**：
- 本工具仅支持 SELECT 查询，禁止 INSERT、UPDATE、DELETE 等写操作
- 仅适用于开发和测试环境
- 生产环境使用需要添加：
  - 用户认证和授权
  - 更严格的 SQL 过滤
  - 查询超时控制
  - 结果集大小限制

## 开发者

需要修改或扩展功能？主要文件说明：

- `app.py`: 修改后端逻辑、API 接口
- `templates/index.html`: 修改前端界面和交互
- `init_database()`: 修改测试数据表结构

## License

MIT License
