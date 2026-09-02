-- Run this once against your MySQL server to create the database.
-- Example:  mysql -u root -p < init_db.sql
--
-- Tables themselves are created automatically by SQLAlchemy on app
-- startup (see app/database.py), so this file only needs to create
-- the schema/database itself.

CREATE DATABASE IF NOT EXISTS ai_study_assistant
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
