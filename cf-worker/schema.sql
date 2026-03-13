PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE,
  phone TEXT UNIQUE,
  nickname TEXT NOT NULL,
  avatar TEXT,
  password_hash TEXT NOT NULL,
  balance REAL DEFAULT 0,
  status INTEGER DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin_users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT,
  nickname TEXT,
  role TEXT DEFAULT 'admin',
  password_hash TEXT NOT NULL,
  status INTEGER DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scripts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT,
  content TEXT NOT NULL,
  output_type TEXT NOT NULL,
  parameters TEXT,
  status INTEGER DEFAULT 0,
  created_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_no TEXT UNIQUE NOT NULL,
  user_id INTEGER NOT NULL,
  task_type TEXT NOT NULL,
  parameters TEXT,
  status INTEGER DEFAULT 0,
  progress INTEGER DEFAULT 0,
  result_url TEXT,
  error_message TEXT,
  cost_amount INTEGER DEFAULT 1,
  created_at TEXT NOT NULL,
  completed_at TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS works (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  work_type TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  content_url TEXT NOT NULL,
  thumbnail_url TEXT,
  status INTEGER DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_no TEXT UNIQUE NOT NULL,
  user_id INTEGER NOT NULL,
  order_type TEXT NOT NULL,
  product_name TEXT,
  amount REAL NOT NULL,
  payment_method TEXT,
  status INTEGER DEFAULT 0,
  created_at TEXT NOT NULL,
  completed_at TEXT,
  remark TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_permissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  permission_type TEXT NOT NULL,
  payment_mode TEXT NOT NULL,
  total_count INTEGER DEFAULT 0,
  used_count INTEGER DEFAULT 0,
  expire_at TEXT,
  status INTEGER DEFAULT 1,
  created_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS system_config (
  key TEXT PRIMARY KEY,
  value TEXT,
  description TEXT,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_scripts_user_id ON scripts(user_id);
CREATE INDEX IF NOT EXISTS idx_works_user_id ON works(user_id);
