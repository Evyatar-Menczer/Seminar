DATA_BASE = 'chinook.db'
ALL_TABLES_QUERY = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"