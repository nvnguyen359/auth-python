# Reset DB bằng init.sql 
#!/bin/bash
# Reset database: drop file SQLite và chạy init.sql

DB_FILE="./app/db/adocv1.db"
INIT_SQL="./app/db/migrations/init.sql"

echo "Resetting database..."
rm -f $DB_FILE
sqlite3 $DB_FILE < $INIT_SQL
echo "Database reset complete."
