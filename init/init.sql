CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
ALTER SYSTEM SET enable_kill_query TO 'on';
ALTER SYSTEM SET track_counts = on;
CREATE ROLE user1 WITH LOGIN PASSWORD '1234';