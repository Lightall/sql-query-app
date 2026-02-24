from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import csv
import io
import json
from datetime import datetime

app = Flask(__name__)
DATABASE = 'test_database.db'

def init_database():
    """初始化数据库，创建测试表并插入数据"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 创建测试表：用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER,
            city TEXT,
            created_at TEXT
        )
    ''')

    # 创建测试表：订单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product TEXT NOT NULL,
            amount REAL,
            status TEXT,
            order_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 检查是否已有数据
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # 插入测试数据
        test_users = [
            ('张三', 'zhangsan@example.com', 25, '北京', '2024-01-15 10:30:00'),
            ('李四', 'lisi@example.com', 30, '上海', '2024-01-16 11:20:00'),
            ('王五', 'wangwu@example.com', 28, '广州', '2024-01-17 14:15:00'),
            ('赵六', 'zhaoliu@example.com', 35, '深圳', '2024-01-18 09:45:00'),
            ('钱七', 'qianqi@example.com', 22, '杭州', '2024-01-19 16:30:00'),
        ]
        cursor.executemany(
            'INSERT INTO users (name, email, age, city, created_at) VALUES (?, ?, ?, ?, ?)',
            test_users
        )

        test_orders = [
            (1, 'iPhone 15', 7999.00, 'completed', '2024-02-01 10:00:00'),
            (1, 'AirPods Pro', 1999.00, 'completed', '2024-02-02 11:30:00'),
            (2, 'MacBook Pro', 15999.00, 'pending', '2024-02-03 14:20:00'),
            (3, 'iPad Air', 4999.00, 'completed', '2024-02-04 09:15:00'),
            (4, 'Apple Watch', 2999.00, 'shipped', '2024-02-05 16:45:00'),
            (5, 'Magic Keyboard', 899.00, 'completed', '2024-02-06 13:20:00'),
        ]
        cursor.executemany(
            'INSERT INTO orders (user_id, product, amount, status, order_date) VALUES (?, ?, ?, ?, ?)',
            test_orders
        )

    conn.commit()
    conn.close()

def log_query(sql, status, error=None):
    """记录查询日志"""
    with open('query_audit.log', 'a', encoding='utf-8') as f:
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sql': sql,
            'status': status,
            'error': error
        }
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_query():
    """执行 SQL 查询"""
    try:
        data = request.get_json()
        sql = data.get('sql', '').strip()

        if not sql:
            return jsonify({'error': 'SQL 语句不能为空'}), 400

        # 安全检查：只允许 SELECT 语句
        sql_upper = sql.upper().strip()
        if not sql_upper.startswith('SELECT'):
            return jsonify({'error': '出于安全考虑，仅支持 SELECT 查询语句'}), 400

        # 执行查询
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
        cursor = conn.cursor()

        cursor.execute(sql)
        rows = cursor.fetchall()

        # 获取列名
        columns = [description[0] for description in cursor.description] if cursor.description else []

        # 转换为列表格式
        results = []
        for row in rows:
            results.append([row[col] for col in columns])

        conn.close()

        # 记录日志
        log_query(sql, 'success')

        return jsonify({
            'columns': columns,
            'data': results,
            'count': len(results)
        })

    except sqlite3.Error as e:
        error_msg = str(e)
        log_query(sql if 'sql' in locals() else '', 'error', error_msg)
        return jsonify({'error': f'SQL 执行错误: {error_msg}'}), 400
    except Exception as e:
        error_msg = str(e)
        log_query(sql if 'sql' in locals() else '', 'error', error_msg)
        return jsonify({'error': f'服务器错误: {error_msg}'}), 500

@app.route('/download', methods=['POST'])
def download_csv():
    """下载查询结果为 CSV 文件"""
    try:
        data = request.get_json()
        columns = data.get('columns', [])
        rows = data.get('data', [])

        # 创建 CSV 内容
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入列名
        writer.writerow(columns)

        # 写入数据
        for row in rows:
            writer.writerow(row)

        # 转换为字节流
        output.seek(0)
        bytes_output = io.BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8-sig'))  # 使用 UTF-8 BOM 以便 Excel 正确识别
        bytes_output.seek(0)

        return send_file(
            bytes_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'query_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )

    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/tables')
def get_tables():
    """获取数据库中的所有表信息"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = []

        for table_name in cursor.fetchall():
            table_name = table_name[0]
            # 获取表的列信息
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # 获取表的行数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            tables.append({
                'name': table_name,
                'columns': [{'name': col[1], 'type': col[2]} for col in columns],
                'row_count': row_count
            })

        conn.close()
        return jsonify({'tables': tables})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    print('=' * 60)
    print('SQL 查询应用已启动！')
    print('访问地址: http://localhost:5000')
    print('=' * 60)
    print('\n示例 SQL 查询：')
    print('  SELECT * FROM users;')
    print('  SELECT * FROM orders;')
    print('  SELECT u.name, o.product, o.amount FROM users u JOIN orders o ON u.id = o.user_id;')
    print('=' * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
