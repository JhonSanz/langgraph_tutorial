

## crear la data de pruebas

- docker exec -i postgres_db psql -U myuser -d mydatabase < populate/postgres_sales.sql
- docker exec -i mysql_db mysql -umyuser -pmypassword mydatabase < populate/mysql_hr.sql