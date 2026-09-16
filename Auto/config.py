iters = 100
clients = 10
transactions = 1000

db_name = 'pg_bench_test'
host = 'localhost'
port = '5432'
user = 'admin'


path_to_pgdata = '/home/admin/pg_bench'

path_to_postgres_conf = f'{path_to_pgdata}/postgresql.conf'

#configure:
librarie_names = 'pg_stat_statements'
extension_names = ['pg_stat_statements']

shared_buffers = '512MB'
