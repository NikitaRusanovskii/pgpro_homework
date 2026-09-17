# Отчет по задаче 3 этапа 1.

Расширение состоит из файлов 4 типов:
Makefile 
Control-file (информация о расширении)
Source-files \[опц.]
SQL-files \[опц.]

Control файл содержит мета-информацию о расширении. Postgres использует его при установке расширения в базу данных.

SQL файл содержит описание SQL-объектов. В примитивном случае, он содержит объявление функции с указанием соответствующей ей функции на языке C, реализованной в динамической библиотеке.

C файлы содержат непосредственно логику функций расширения. Они используют API Postgres для получения аргументов и возвращения результатов. API предоставляет удобные макросы, с помощью которых от разработчика скрываются многие сложности организации расширения, а также типы, используемые в Postgres.

Makefile используется для сборки расширения. В нем используется PGXS - инфраструктура для сборки расширений Postgres.

Для выполнения этого задания, мной была выбрана идея написания примитивного XOR шифровщика
для типа данных text по ключу типа данных char.

Исходные файлы расширения можно найти по пути *PostgresRepo/Ext/demo_extension/*

Соберём, проверим работоспособность и протестируем:
\========================================================
┌──(env)(admin㉿DESKTOP-NNMFN20)-[~/PostgresRepo/Ext/demo_extension]
└─$ make && make install
gcc -Wall -Wmissing-prototypes -Wpointer-arith -Wdeclaration-after-statement -Werror=vla -Wendif-labels -Wmissing-format-attribute -Wimplicit-fallthrough=3 -Wcast-function-type -Wshadow=compatible-local -Wformat-security -fno-strict-aliasing -fwrapv -fexcess-precision=standard -Wno-format-truncation -Wno-stringop-truncation -g -ggdb -O0 -fno-omit-frame-pointer -fPIC -fvisibility=hidden -I. -I./ -I/home/admin/PostgresRepo/Build/PostgreSQL_17_11/include/postgresql/server -I/home/admin/PostgresRepo/Build/PostgreSQL_17_11/include/postgresql/internal -g -O0 -D_GNU_SOURCE    -c -o change_text.o change_text.c
gcc -Wall -Wmissing-prototypes -Wpointer-arith -Wdeclaration-after-statement -Werror=vla -Wendif-labels -Wmissing-format-attribute -Wimplicit-fallthrough=3 -Wcast-function-type -Wshadow=compatible-local -Wformat-security -fno-strict-aliasing -fwrapv -fexcess-precision=standard -Wno-format-truncation -Wno-stringop-truncation -g -ggdb -O0 -fno-omit-frame-pointer -fPIC -fvisibility=hidden change_text.o -L/home/admin/PostgresRepo/Build/PostgreSQL_17_11/lib   -Wl,--as-needed -Wl,-rpath,'/home/admin/PostgresRepo/Build/PostgreSQL_17_11/lib',--enable-new-dtags -fvisibility=hidden -shared -o change_text.so
/usr/bin/mkdir -p '/home/admin/PostgresRepo/Build/PostgreSQL_17_11/share/postgresql/extension'
/usr/bin/mkdir -p '/home/admin/PostgresRepo/Build/PostgreSQL_17_11/share/postgresql/extension'
/usr/bin/mkdir -p '/home/admin/PostgresRepo/Build/PostgreSQL_17_11/lib/postgresql'
/usr/bin/install -c -m 644 .//change_text.control '/home/admin/PostgresRepo/Build/PostgreSQL_17_11/share/postgresql/extension/'
/usr/bin/install -c -m 644 .//change_text--1.0.sql  '/home/admin/PostgresRepo/Build/PostgreSQL_17_11/share/postgresql/extension/'
/usr/bin/install -c -m 755  change_text.so '/home/admin/PostgresRepo/Build/PostgreSQL_17_11/lib/postgresql/'
\========================================================

В некоторых версиях Postgres может понадобиться явное указание USE_PGXS=1 при использовании команд make, однако на версии 17.11, с которой я работаю, отсутствие явного указания флага никак не влияет на сборку и работоспособность расширения.

Запустим сервер, на который хотим установить расширение:
\========================================================
┌──(env)(admin㉿DESKTOP-NNMFN20)-[~/PostgresRepo/Ext/demo_extension]
└─$ pg_ctl start -D ../../Data/pgdata_edu
pg_ctl: another server might be running; trying to start server anyway
waiting for server to start....2026-09-17 23:30:31.416 MSK [36049] LOG:  starting PostgreSQL 17.11 on x86_64-pc-linux-gnu, compiled by gcc (Debian 15.2.0-17) 15.2.0, 64-bit
2026-09-17 23:30:31.417 MSK [36049] LOG:  listening on IPv4 address "127.0.0.1", port 5432
2026-09-17 23:30:31.421 MSK [36049] LOG:  listening on Unix socket "/tmp/.s.PGSQL.5432"
2026-09-17 23:30:31.429 MSK [36052] LOG:  database system was interrupted; last known up at 2026-09-15 16:43:16 MSK
2026-09-17 23:30:31.725 MSK [36052] LOG:  database system was not properly shut down; automatic recovery in progress
2026-09-17 23:30:31.732 MSK [36052] LOG:  redo starts at 0/1656538
2026-09-17 23:30:31.732 MSK [36052] LOG:  invalid record length at 0/1656640: expected at least 24, got 0
2026-09-17 23:30:31.732 MSK [36052] LOG:  redo done at 0/1656608 system usage: CPU: user: 0.00 s, system: 0.00 s, elapsed: 0.00 s
2026-09-17 23:30:31.741 MSK [36050] LOG:  checkpoint starting: end-of-recovery immediate wait
2026-09-17 23:30:31.761 MSK [36050] LOG:  checkpoint complete: wrote 3 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.007 s, sync=0.002 s, total=0.022 s; sync files=2, longest=0.002 s, average=0.001 s; distance=0 kB, estimate=0 kB; lsn=0/1656640, redo lsn=0/1656640
2026-09-17 23:30:31.768 MSK [36049] LOG:  database system is ready to accept connections
 done
server started

\========================================================
Подключимся к серверу с помощью psql:
\========================================================
┌──(env)(admin㉿DESKTOP-NNMFN20)-[~/PostgresRepo/Ext/demo_extension]
└─$ psql -h localhost -p 5432 -U admin postgres
psql (17.11)
Type "help" for help.

postgres=#
\========================================================
Создадим расширение в нашей базе:
\========================================================
postgres=# \dx
                 List of installed extensions
  Name   | Version |   Schema   |         Description
---------+---------+------------+------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
(1 row)

postgres=# CREATE EXTENSION change_text;
CREATE EXTENSION
postgres=# \dx
                      List of installed extensions
    Name     | Version |   Schema   |            Description
-------------+---------+------------+-----------------------------------
 change_text | 1.0     | public     | PostgreSQL extension: change_text
 plpgsql     | 1.0     | pg_catalog | PL/pgSQL procedural language
(2 rows)

postgres=#
\========================================================
Видим, что расширение успешно создалось. Оно находится в public схеме.
\========================================================
postgres=# SELECT change_text('hello', '1');
 change_text
-------------
 YT]]^
(1 row)


postgres=# SELECT change_text('YT]]^', '1');
 change_text
-------------
 hello
(1 row)
\========================================================

Расширение прекрасно работает. Стоит отметить, что результат функции может состоять из непечатаемых символов, которые Postgres может выводить на экран в 16-ричном виде. В таком случае функция не предполагает выполнения операции расшифровки.