# Отчёт по задаче 5 этапа 1
## Внимание! В данном отчёте приведены консольные логи. Я отделяю их от текста с помощью последовательности '=' Используйте поиск по '===================' для более быстрого ориентирования. Если в логах приведены какие-то комментарии, воспользуйтесь '~~~~~~~~~' при поиске комментариев.


Для выполнения этого задания я написал скрипт:
*Auto/pgbench/pgbench.py*

Данный скрипт поддерживает несколько опций:
    --init-cluster: инициализирует кластер для работы
    --init: инициализирует базу данных, создаёт рабочие таблицы для pgbench
    --run: запускает тесты. Результаты складываются в файлы.
        Файлы лежат в *Auto/pgbench/reports*
        Формат файлов S{количество разделяемой памяти}L{включена ли библиотека {0 или 1}}C{число клиентов}.report
    --draw: отображает графики tps/clients или latency/clients. Синий цвет - 512MB памяти, красный - 1024.
        Также выводится некоторая дополнительная информация в консоль. Например, среднеквадратичное отклонение.
        Данная функция находится в разработке.
    --clear: безвозвратно удаляет *Auto/pgbench/reports*. Будьте внимательны, используя эту функцию!!!

Какими возможностями pgbench я воспользовался во время выполнения задачи?
https://www.postgresql.org/docs/current/pgbench.html - источник, где я искал информацию

pgbench -i -s50 pgbench_test - инициализация рабочих таблиц в базе pgbench_test с увеличивающим фактором 50
Что такое увеличивающий фактор?

Значения строк в таблицах по умолчанию:
table                   # of rows
---------------------------------
pgbench_branches        1
pgbench_tellers         10
pgbench_accounts        100000
pgbench_history         0

При указании scale_factor с помощью -s, эти значения увеличиваются в scale_factor раз.
scale_factor = 1 по умолчанию. То есть -s указывает масштабный коэффициент, который увеличивает
таблицы для тестирования пропорционально этой величине. Конечно, pgbench позволяет задавать свои таблицы.
Но в примере я указал только дефолтные таблицы.

Когда таблицы созданы, можно приступить к тестированию.

pgbench -c 10 -j 2 -t 1000 pgbench_test - запуск теста с c=10 параллельными подключениями.
pgbench должен выполнить t=1000 транзакций на каждого клиента. Подключения будут обрабатываться j=2 процессами.

Для выполнения тестирования на моей машине я использовал параметр -j $(nproc) => -j=16

Параметры, которые я использовал для воспроизведения эксперимента:

```Python
#configure:
shared_buffers = ['512MB', '1024MB'] # размер разделяемой памяти. Скрипт сначала воиспроизводит тестирование с размером 512 мб, затем - с 1024 мб.
#pgbench_time = 60
libs = ['', 'pg_stat_statements'] # библиотеки, которые использует скрипт. Изначально тесты производятся без библотеки, а затем - с pg_stat_statements.
client_nums = [1, 2, 4, 8, 16, 32, 64, 128] # количество клиентов, которые используются для тестирования
iters = range(0, 3) # количество итераций. 3 итерации.
transactions = 1000 # количество транзакций на клиента

#pgbench config
db = 'pgbench_test' # база данных, где генерируются таблицы
scale_factor = 50 # масштабный коэффициент

#pgbench cluster config
host = 'localhost' # хост
port = '5432' # порт
user = 'admin' # пользователь

pgdata = Path(__file__).resolve().parent / "../../Data/pgbench" # путь к каталогу кластера
path_to_postgres_conf = pgdata / 'postgresql.conf' # путь к postgresql.conf (файл конфигурации)

#reports:
reports_path = Path(__file__).resolve().parent / "reports" # путь к папке с отчётами по тестированию

```


В ходе тестов было выявлено, что случай со 128 клиентами не обрабатывается:
=================================================================================================================
2026-09-17 12:49:53.738 MSK [24782] LOG:  could not receive data from client: Connection reset by peer
2026-09-17 12:49:53.865 MSK [24911] FATAL:  sorry, too many clients already
2026-09-17 12:49:53.865 MSK [24912] FATAL:  sorry, too many clients already
2026-09-17 12:49:53.866 MSK [24913] FATAL:  sorry, too many clients already
=================================================================================================================
Это связано с тем, что в postgresql.conf установлено значение максимальных подключений, которое
уступает числу подключений в ходе теста.

В ходе работы над отчётом, при рассмотрении этой проблемы, я узнал о возможности изменять конфиг изнутри
рабочего сервера с помощью. Если обратить внимание на функцию, работающую с конфигом, в моём автоматизирующем скрипте, там можно будет увидеть костыль:) Во время написания скрипта, я ещё не знал о такой возможности.

```bash
ALTER SYSTEM [option]
```

обновим параметр максимальных подключений:

================================================================================================================
└─$ psql -h localhost -p 5432 -U admin postgres
psql (17.11)
Type "help" for help.
postgres=# SHOW max_connections;
 max_connections
-----------------
 100
(1 row)

postgres=# ALTER SYSTEM SET max_connections TO '256';
ALTER SYSTEM
postgres=# SHOW max_connections;
 max_connections
-----------------
 100
(1 row)
================================================================================================================
Параметр не изменился? Нет, он изменился, но необходимо перезагрузить сервер.
================================================================================================================
postgres=# exit

┌──(admin㉿DESKTOP-NNMFN20)-[~/PostgresRepo]
└─$ pg_ctl restart -D Data/pgbench
waiting for server to shut down....2026-09-17 13:02:26.196 MSK [26011] LOG:  received fast shutdown request
2026-09-17 13:02:26.199 MSK [26011] LOG:  aborting any active transactions
2026-09-17 13:02:26.200 MSK [26011] LOG:  background worker "logical replication launcher" (PID 26017) exited with exit code 1
2026-09-17 13:02:26.201 MSK [26012] LOG:  shutting down
2026-09-17 13:02:26.202 MSK [26012] LOG:  checkpoint starting: shutdown immediate
2026-09-17 13:02:26.217 MSK [26012] LOG:  checkpoint complete: wrote 9 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.008 s, sync=0.003 s, total=0.017 s; sync files=5, longest=0.001 s, average=0.001 s; distance=26 kB, estimate=26 kB; lsn=2/67040B08, redo lsn=2/67040B08
2026-09-17 13:02:26.236 MSK [26011] LOG:  database system is shut down
 done
server stopped
waiting for server to start....2026-09-17 13:02:26.369 MSK [26404] LOG:  starting PostgreSQL 17.11 on x86_64-pc-linux-gnu, compiled by gcc (Debian 15.2.0-17) 15.2.0, 64-bit
2026-09-17 13:02:26.370 MSK [26404] LOG:  listening on IPv4 address "127.0.0.1", port 5432
2026-09-17 13:02:26.373 MSK [26404] LOG:  listening on Unix socket "/tmp/.s.PGSQL.5432"
2026-09-17 13:02:26.379 MSK [26407] LOG:  database system was shut down at 2026-09-17 13:02:26 MSK
2026-09-17 13:02:26.386 MSK [26404] LOG:  database system is ready to accept connections
 done
server started

┌──(admin㉿DESKTOP-NNMFN20)-[~/PostgresRepo]
└─$ psql -h localhost -p 5432 -U admin postgres
psql (17.11)
Type "help" for help.

postgres=# SHOW max_connections;
 max_connections
-----------------
 256
(1 row)

postgres=#
=================================================================================================================