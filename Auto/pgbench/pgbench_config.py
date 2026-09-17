from pathlib import Path

#configure:
shared_buffers = ['512MB', '1024MB']
#pgbench_time = 60
libs = ['', 'pg_stat_statements']
client_nums = [1, 2, 4, 8, 16, 32, 64, 128]
iters = range(0, 3)
transactions = 10

#pgbench config
db = 'pgbench_test'
scale_factor = 50

#pgbench cluster config
host = 'localhost'
port = '5432'
user = 'admin'

pgdata = Path(__file__).resolve().parent / "../../Data/pgbench"
path_to_postgres_conf = pgdata / 'postgresql.conf'

#reports:
reports_path = Path(__file__).resolve().parent / "reports"
