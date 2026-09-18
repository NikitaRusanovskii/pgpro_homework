Отчёт вышел очень большой, около 1500 строк.
В целях упрощения работы с отчётом, я разделил фрагменты с размышлениями и выводами с помощью
знаков равно.

Используйте поиск по "============" чтобы найти эти разделения и быстро ориентироваться по тексту.

Также я оставлял некоторые комментарии к отладочной информации, чтобы ориентироваться по ним,
используйте поиск по "!!!!!!!"



1) Запустим сервер:

\========================================================

┌──(admin㉿DESKTOP-NNMFN20)-[~]
└─$ pg_ctl start -D pgdata_edu/
waiting for server to start....2026-09-13 17:18:39.224 MSK [65168] LOG:  starting PostgreSQL 17.11 on x86_64-pc-linux-gnu, compiled by gcc (Debian 15.2.0-17) 15.2.0, 64-bit
2026-09-13 17:18:39.225 MSK [65168] LOG:  listening on IPv4 address "127.0.0.1", port 5432
2026-09-13 17:18:39.232 MSK [65168] LOG:  listening on Unix socket "/tmp/.s.PGSQL.5432"
2026-09-13 17:18:39.248 MSK [65171] LOG:  database system was shut down at 2026-09-10 11:12:35 MSK
2026-09-13 17:18:39.271 MSK [65168] LOG:  database system is ready to accept connections
 done
server started

┌──(admin㉿DESKTOP-NNMFN20)-[~]
└─$

2) Подключимся к серверу:

\========================================================

┌──(admin㉿DESKTOP-NNMFN20)-[~]
└─$ psql -h localhost -p 5432 -U admin postgres
psql (17.11)
Type "help" for help.

postgres=#

\========================================================

3) Выполним SELECT pg_backend_pid(); Чтобы получить pid бекенда.

\========================================================

postgres=# SELECT pg_backend_pid();
 pg_backend_pid
----------------
          65239
(1 row)

postgres=#

\========================================================

4) В другой вкладке терминала запустим gdb, подключив его к данному процессу

\========================================================

┌──(admin㉿DESKTOP-NNMFN20)-[~]
└─$ gdb -p 65239
GNU gdb (Debian 17.2-1) 17.2
Copyright (C) 2025 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word".
Attaching to process 65239
Reading symbols from /home/admin/PostgresSQL/bin/postgres...
Reading symbols from /usr/lib/x86_64-linux-gnu/libz.so.1...
(No debugging symbols found in /usr/lib/x86_64-linux-gnu/libz.so.1)
Reading symbols from /usr/lib/x86_64-linux-gnu/libm.so.6...
(No debugging symbols found in /usr/lib/x86_64-linux-gnu/libm.so.6)
Reading symbols from /usr/lib/x86_64-linux-gnu/libicui18n.so.78...
(No debugging symbols found in /usr/lib/x86_64-linux-gnu/libicui18n.so.78)
Reading symbols from /usr/lib/x86_64-linux-gnu/libicuuc.so.78...
(No debugging symbols found in /usr/lib/x86_64-linux-gnu/libicuuc.so.78)
Reading symbols from /usr/lib/x86_64-linux-gnu/libc.so.6...
(No debugging symbols found in /usr/lib/x86_64-linux-gnu/libc.so.6)
Reading symbols from /lib64/ld-linux-x86-64.so.2...
(No debugging symbols found in /lib64/ld-linux-x86-64.so.2)
Reading symbols from /usr/lib/x86_64-linux-gnu/libstdc++.so.6...
(No debugging symbols found in /usr/lib/x86_64-linux-gnu/libstdc++.so.6)
Reading symbols from /usr/lib/x86_64-linux-gnu/libgcc_s.so.1...
(No debugging symbols found in /usr/lib/x86_64-linux-gnu/libgcc_s.so.1)
Reading symbols from /usr/lib/x86_64-linux-gnu/libicudata.so.78...
(No debugging symbols found in /usr/lib/x86_64-linux-gnu/libicudata.so.78)
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/usr/lib/x86_64-linux-gnu/libthread_db.so.1".
0x000079cce349a7d2 in ?? ()
   from /usr/lib/x86_64-linux-gnu/libc.so.6
(gdb)

\========================================================

5) Поставим точку останова на целевой функции: change_text

\========================================================

(gdb) b change_text
Breakpoint 1 at 0x74b230bf1187: file change_text.c, line 15.
(gdb)

\========================================================

6) Выполним простой запрос SELECT change_text('hello', ' ');
    Ожидаемый ответ: HELLO

    6.1) В gdb напишем continue для возобновления работы процесса бекенда
    6.2) Выполним запрос

\========================================================

Breakpoint 1, change_text (fcinfo=0x63b708fe2658) at change_text.c:15
15          text* dt = PG_GETARG_TEXT_PP(0); // запакованная varlena
(gdb)

\========================================================

7) Просмотрим стек вызовов

\========================================================

(gdb) bt
#0  change_text (fcinfo=0x63b708fe2658) at change_text.c:15
#1  0x000063b6ce276be6 in  (state=0x63b708fe2500,
    econtext=0x63b708fe22a8, isnull=0x7ffe1881aae7) at execExprInterp.c:772
#2  0x000063b6ce278c2e in StillValid (state=0x63b708fe2500,
    econtext=0x63b708fe22a8, isNull=0x7ffe1881aae7)
    at execExprInterp.c:1935
#3  0x000063b6ce2d6ec1 in ExecEvalExprSwitchContext (state=0x63b708fe2500,
    econtext=0x63b708fe22a8, isNull=0x7ffe1881aae7)
    at ../../../src/include/executor/executor.h:360
#4  0x000063b6ce2d6f2d in ExecProject (projInfo=0x63b708fe24f8)
    at ../../../src/include/executor/executor.h:394
#5  0x000063b6ce2d7129 in ExecResult (pstate=0x63b708fe2198)
    at nodeResult.c:135
#6  0x000063b6ce2912d4 in ExecProcNodeFirst (node=0x63b708fe2198)
    at execProcnode.c:464
#7  0x000063b6ce28424c in ExecProcNode (node=0x63b708fe2198)
    at ../../../src/include/executor/executor.h:278
#8  0x000063b6ce287188 in ExecutePlan (queryDesc=0x63b708f3e7f0,
    operation=CMD_SELECT, sendTuples=true, numberTuples=0,
    direction=ForwardScanDirection, dest=0x63b708fe0a60) at execMain.c:1705
#9  0x000063b6ce2848e3 in standard_ExecutorRun (queryDesc=0x63b708f3e7f0,
    direction=ForwardScanDirection, count=0, execute_once=false)
    at execMain.c:360
#10 0x000063b6ce284740 in ExecutorRun (queryDesc=0x63b708f3e7f0,
    direction=ForwardScanDirection, count=0, execute_once=false)
    at execMain.c:306
#11 0x000063b6ce547f25 in PortalRunSelect (portal=0x63b708f8edf0,
    forward=true, count=0, dest=0x63b708fe0a60) at pquery.c:922
#12 0x000063b6ce547bc9 in PortalRun (portal=0x63b708f8edf0,
    count=9223372036854775807, isTopLevel=true, run_once=true,
    dest=0x63b708fe0a60, altdest=0x63b708fe0a60, qc=0x7ffe1881ae80)
    at pquery.c:766
#13 0x000063b6ce5409c8 in exec_simple_query (
    query_string=0x63b708f130c0 "SELECT change_text('hello', ' ');")
    at postgres.c:1279
#14 0x000063b6ce545c7a in PostgresMain (dbname=0x63b708f4ac28 "postgres",
    username=0x63b708f4ac10 "admin") at postgres.c:4787
#15 0x000063b6ce53cc58 in BackendMain (startup_data=0x7ffe1881b18c "",
    startup_data_len=4) at backend_startup.c:105
#16 0x000063b6ce45a7ac in postmaster_child_launch (child_type=B_BACKEND,
    startup_data=0x7ffe1881b18c "", startup_data_len=4,
--Type <RET> for more, q to quit, c to continue without paging--
    client_sock=0x7ffe1881b1b0) at launch_backend.c:277
#17 0x000063b6ce460932 in BackendStartup (client_sock=0x7ffe1881b1b0)
    at postmaster.c:3582
#18 0x000063b6ce45dc02 in ServerLoop () at postmaster.c:1679
#19 0x000063b6ce45d568 in PostmasterMain (argc=3, argv=0x63b708f0d620)
    at postmaster.c:1377
#20 0x000063b6ce30c58b in main (argc=3, argv=0x63b708f0d620) at main.c:199
(gdb)

\========================================================

стек вызовов представляет собой последовательность вложенных вызовов функций, где нулевой фрейм - самая
последняя вызванная функция.

Описание функций (довольно в общих чертах):
Как мы можем видеть, сперва (что естественно) запускается main, далее в
новом процессе запускается postmaster и запускает ServerLoop. Далее вызывается postmaster_child_launch - функция, которая создает дочерний postmaster'у процесс.

Далее вызывается BackendMain функция. Это точка входа для конкретного backend. Она обслуживает
одно подключение. (Вероятно,BackendStartup, postmaster_child_launch и данная функция, были вызваны после того, как мы подключились через psql).

Далее вызывается PostgresMain - цикл, в котором бекенд обслуживает соединение с клиентом.

exec_simple_query отвечает за выполнение простых (пришедших по протоколу simple query protocol) запросов.
Как видно из окна отладки, она получила строковый аргумент, содержащий полный текст нашей команды.

PortalRun - функция, отвечающая за выполнение запроса, инкапсулированного в Portal.
Portal - структура, хранящая состояние исполнения запроса.

PortalRunSelect - отвечает за исполнение запросов, которые возвращают строки (обычно, селекты)

ExecutorRun - запуск исполнителя запроса

standart_ExecutorRun - стандартная реализация ExecutorRun. Запускает ExecutePlan для выполнения плана.

ExecutePlan - исполнитель плана запроса.

ExecProcNode - Вызывает функцию выполнения текущего узла плана, соответствующую типу узла.

ExecProcNodeFirst - первоначальная обработка узла перед его выполнением.

ExecResult - выполняет результирующий узел.

ExecProject - формирует результирующую строку.

ExecEvalExprSwitchContext - вычисление значения выражения SQL, автоматически переключает
контекст на нужный уровень.

ExecEvalExprStillValid - проверяет возможность продолжить интерпретацию выражения

ExecEvalExpr - интерпретирует выражение, вычисляя итоговое значение

8) Перейдём в нулевой фрейм

\========================================================

(gdb) frame 0
#0  change_text (fcinfo=0x63b708fe2658) at change_text.c:15
15          text* dt = PG_GETARG_TEXT_PP(0); // запакованная varlena
(gdb)

\========================================================

9) Просмотрим значение параметра, переданного в функцию (fcinfo)

\========================================================

(gdb) print fcinfo
$1 = (FunctionCallInfo) 0x63b708fe2658
(gdb) print *fcinfo
$2 = {flinfo = 0x63b708fe2608, context = 0x0, resultinfo = 0x0,
  fncollation = 100, isnull = false, nargs = 2, args = 0x63b708fe2678}
(gdb) print fcinfo.args[0]
$3 = {value = 109637780194152, isnull = false}
(gdb) print fcinfo.args[1]
$4 = {value = 32, isnull = false}
(gdb)
\========================================================

value представлено типом данных Datum - универсальным типом для передачи значений.
(gdb) print ((char *)fcinfo.args[0].value + 4) Выводим значение Datum, начиная с 4 байта (тк первые 4 - заголовок)

Если быть точным, мы приводим значение fcinfo.args[0].value к char* и смещаем на 4 байта*

\========================================================

$18 = 0x63b708f1436c "hello~\177\177\177\177\177\177(" <- Вывод некрасивый, тк в Posgres строки не обязаны кончаться на \0
(gdb)
(gdb) print (char)fcinfo.args[1]->value
$9 = 32 ' ' <- пробельный символ из запроса

\========================================================

10) Посмотрим текст функции

\========================================================

(gdb) list 13,33
13      PG_FUNCTION_INFO_V1(change_text);
14      Datum change_text(PG_FUNCTION_ARGS) {
15          text* dt = PG_GETARG_TEXT_PP(0); // запакованная varlena
16          char symbol = PG_GETARG_CHAR(1);
17          int32 len = VARSIZE_ANY_EXHDR(dt);
18          text* new_dt = (text*)palloc(VARSIZE_ANY_EXHDR(dt) + VARHDRSZ);
19          SET_VARSIZE(new_dt, VARSIZE_ANY_EXHDR(dt) + VARHDRSZ);
20          for(int32 i = 0; i < len; i++) {
21              VARDATA_ANY(new_dt)[i] = VARDATA_ANY(dt)[i] ^ symbol;
22          }
23          PG_RETURN_TEXT_P(new_dt);
24      }
(gdb)

11) В целях отладки, например, нам понадобилось посмотреть изменение переменной new_dt
установим за ней слежение

\========================================================

(gdb) watch new_dt
Hardware watchpoint 2: new_dt
(gdb)

\========================================================

12) Отладчик останавливается именно там, где обновили значение new_dt, изменив содержание переменной.

\========================================================


(gdb) continue
Continuing.

Hardware watchpoint 2: new_dt

Old value = (text *) 0x7ffe1881a810
New value = (text *) 0x63b708fe4660
change_text (fcinfo=0x63b708fe2658) at change_text.c:19
19          SET_VARSIZE(new_dt, VARSIZE_ANY_EXHDR(dt) + VARHDRSZ);
(gdb)

\========================================================

Теперь проведём отладку нашей функции, с первым аргументом, равным NULL.
В ходе работы над этим заданием, я узнал, как Postgres обрабатывает NULL аргументы
в функциях, объвленных, как STRICT.

Попробуем отследить это в отладчике.
Поставим точку останова на ExecProject, выполним запрос.

\========================================================

0x000079c5c329a7d2 in ?? () from /usr/lib/x86_64-linux-gnu/libc.so.6
(gdb) b ExecProject
Breakpoint 1 at 0x62f9b18c05c2: ExecProject. (12 locations)
(gdb) c
Continuing.

Breakpoint 1.10, ExecProject (projInfo=0x62f9e594b558)
    at ../../../src/include/executor/executor.h:382
382             ExprContext *econtext = projInfo->pi_exprContext;
(gdb) print *projInfo
$1 = {type = T_ProjectionInfo, pi_state = {type = T_ExprState,
    flags = 6 '\006', resnull = false, resvalue = 0,
    resultslot = 0x62f9e594b478, steps = 0x62f9e594b668,
    evalfunc = 0x62f9b18a3bd7 <ExecInterpExprStillValid>,
    expr = 0x62f9e5921760,
    evalfunc_private = 0x62f9b18a1237 <ExecInterpExpr>, steps_len = 3,
    steps_alloc = 16, parent = 0x62f9e594b1f8, ext_params = 0x0,
    innermost_caseval = 0x0, innermost_casenull = 0x0,
    innermost_domainval = 0x0, innermost_domainnull = 0x0,
    escontext = 0x0}, pi_exprContext = 0x62f9e594b308}
(gdb)

\========================================================

Обратим внимание на аргумет, переданный в отслеживаемую функцию.
Это структура, внутри которой вложена структура pi_steps, в которой
содержатся некоторые интересные нам поля:
resnull, resvalue, steps, step_len

Steps - некоторая последовательность инструкций, которые должен выполнить исполнитель.
В нашем случае, steps состоит из 3 элементов.
resnull - флаг, указывающий, что вычисленное выражение = NULL
resvalue - значение, которое получим в результате выполнения выражения.

В нашем случае, steps содержит 3 элемента. Распечатаем их по очереди.

\========================================================

(gdb) print projInfo->pi_state->steps[0]
$5 = {opcode = 108824564996787, resvalue = 0x62f9e5926438,
  resnull = 0x62f9e5926435, d = {fetch = {last_var = 0, fixed = false,
      known_desc = 0x1, kind = 0x0}, var = {attnum = 0, vartype = 0},
    wholerow = {var = 0x0, first = true, slow = false, tupdesc = 0x0,
      junkFilter = 0x0}, assign_var = {resultnum = 0, attnum = 0},
    assign_tmp = {resultnum = 0}, constval = {value = 0, isnull = true},
    func = {finfo = 0x0, fcinfo_data = 0x1, fn_addr = 0x0, nargs = 0,
      make_ro = false}, boolexpr = {anynull = 0x0, jumpdone = 1},
    qualexpr = {jumpdone = 0}, jump = {jumpdone = 0}, nulltest_row = {
      rowcache = {cacheptr = 0x0, tupdesc_id = 1}}, param = {paramid = 0,
      paramtype = 0}, cparam = {paramfunc = 0x0, paramarg = 0x1,
      paramid = 0, paramtype = 0}, casetest = {value = 0x0, isnull = 0x1},
    make_readonly = {value = 0x0, isnull = 0x1}, iocoerce = {
      finfo_out = 0x0, fcinfo_data_out = 0x1, finfo_in = 0x0,
      fcinfo_data_in = 0x0}, sqlvaluefunction = {svf = 0x0},
    nextvalueexpr = {seqid = 0, seqtypid = 0}, arrayexpr = {
      elemvalues = 0x0, elemnulls = 0x1, nelems = 0, elemtype = 0,
      elemlength = 0, elembyval = false, elemalign = 0 '\000',
      multidims = false}, arraycoerce = {elemexprstate = 0x0,
      resultelemtype = 1, amstate = 0x0}, row = {tupdesc = 0x0,
      elemvalues = 0x1, elemnulls = 0x0}, rowcompare_step = {finfo = 0x0,
      fcinfo_data = 0x1, fn_addr = 0x0, jumpnull = 0, jumpdone = 0},
    rowcompare_final = {rctype = 0}, minmax = {values = 0x0, nulls = 0x1,
      nelems = 0, op = IS_GREATEST, finfo = 0x0, fcinfo_data = 0x0},
    fieldselect = {fieldnum = 0, resulttype = 0, rowcache = {
        cacheptr = 0x1, tupdesc_id = 0}}, fieldstore = {fstore = 0x0,
      rowcache = 0x1, values = 0x0, nulls = 0x0, ncolumns = 0},
    sbsref_subscript = {subscriptfunc = 0x0, state = 0x1, jumpdone = 0},
    sbsref = {subscriptfunc = 0x0, state = 0x1}, domaincheck = {
      constraintname = 0x0, checkvalue = 0x1, checknull = 0x0,
      resulttype = 0, escontext = 0x0}, convert_rowtype = {inputtype = 0,
      outputtype = 0, incache = 0x1, outcache = 0x0, map = 0x0},
    scalararrayop = {element_type = 0, useOr = false, typlen = 0,
      typbyval = true, typalign = 0 '\000', finfo = 0x0,
      fcinfo_data = 0x0, fn_addr = 0x0}, hashedscalararrayop = {
      has_nulls = false, inclause = false, null_lhs_result = false,
      null_lhs_isnull = false, elements_tab = 0x1, finfo = 0x0,
      fcinfo_data = 0x0, saop = 0x0}, xmlexpr = {xexpr = 0x0,
      named_argvalue = 0x1, named_argnull = 0x0, argvalue = 0x0,
      argnull = 0x0}, json_constructor = {jcstate = 0x0}, aggref = {
      aggno = 0}, grouping_func = {clauses = 0x0}, window_func = {
--Type <RET> for more, q to quit, c to continue without paging--
      wfstate = 0x0}, subplan = {sstate = 0x0}, agg_deserialize = {
      fcinfo_data = 0x0, jumpnull = 1}, agg_strict_input_check = {
      args = 0x0, nulls = 0x1, nargs = 0, jumpnull = 0},
    agg_plain_pergroup_nullcheck = {setoff = 0, jumpnull = 0},
    agg_presorted_distinctcheck = {pertrans = 0x0, aggcontext = 0x1,
      jumpdistinct = 0}, agg_trans = {pertrans = 0x0, aggcontext = 0x1,
      setno = 0, transno = 0, setoff = 0}, is_json = {pred = 0x0},
    jsonexpr = {jsestate = 0x0}, jsonexpr_coercion = {targettype = 0,
      targettypmod = 0, omit_quotes = true, exists_coerce = false,
      exists_cast_to_int = false, exists_check_domain = false,
      json_coercion_cache = 0x0, escontext = 0x0}}}



    
(gdb) print projInfo->pi_state->steps[1]
$6 = {opcode = 108824564996552, resvalue = 0x0, resnull = 0x0, d = {
    fetch = {last_var = 0, fixed = false, known_desc = 0x0, kind = 0x0},
    var = {attnum = 0, vartype = 0}, wholerow = {var = 0x0, first = false,
      slow = false, tupdesc = 0x0, junkFilter = 0x0}, assign_var = {
      resultnum = 0, attnum = 0}, assign_tmp = {resultnum = 0},
    constval = {value = 0, isnull = false}, func = {finfo = 0x0,
      fcinfo_data = 0x0, fn_addr = 0x0, nargs = 0, make_ro = false},
    boolexpr = {anynull = 0x0, jumpdone = 0}, qualexpr = {jumpdone = 0},
    jump = {jumpdone = 0}, nulltest_row = {rowcache = {cacheptr = 0x0,
        tupdesc_id = 0}}, param = {paramid = 0, paramtype = 0}, cparam = {
      paramfunc = 0x0, paramarg = 0x0, paramid = 0, paramtype = 0},
    casetest = {value = 0x0, isnull = 0x0}, make_readonly = {value = 0x0,
      isnull = 0x0}, iocoerce = {finfo_out = 0x0, fcinfo_data_out = 0x0,
      finfo_in = 0x0, fcinfo_data_in = 0x0}, sqlvaluefunction = {
      svf = 0x0}, nextvalueexpr = {seqid = 0, seqtypid = 0}, arrayexpr = {
      elemvalues = 0x0, elemnulls = 0x0, nelems = 0, elemtype = 0,
      elemlength = 0, elembyval = false, elemalign = 0 '\000',
      multidims = false}, arraycoerce = {elemexprstate = 0x0,
      resultelemtype = 0, amstate = 0x0}, row = {tupdesc = 0x0,
      elemvalues = 0x0, elemnulls = 0x0}, rowcompare_step = {finfo = 0x0,
      fcinfo_data = 0x0, fn_addr = 0x0, jumpnull = 0, jumpdone = 0},
    rowcompare_final = {rctype = 0}, minmax = {values = 0x0, nulls = 0x0,
      nelems = 0, op = IS_GREATEST, finfo = 0x0, fcinfo_data = 0x0},
    fieldselect = {fieldnum = 0, resulttype = 0, rowcache = {
        cacheptr = 0x0, tupdesc_id = 0}}, fieldstore = {fstore = 0x0,
      rowcache = 0x0, values = 0x0, nulls = 0x0, ncolumns = 0},
    sbsref_subscript = {subscriptfunc = 0x0, state = 0x0, jumpdone = 0},
    sbsref = {subscriptfunc = 0x0, state = 0x0}, domaincheck = {
      constraintname = 0x0, checkvalue = 0x0, checknull = 0x0,
      resulttype = 0, escontext = 0x0}, convert_rowtype = {inputtype = 0,
      outputtype = 0, incache = 0x0, outcache = 0x0, map = 0x0},
    scalararrayop = {element_type = 0, useOr = false, typlen = 0,
      typbyval = false, typalign = 0 '\000', finfo = 0x0,
      fcinfo_data = 0x0, fn_addr = 0x0}, hashedscalararrayop = {
      has_nulls = false, inclause = false, null_lhs_result = false,
      null_lhs_isnull = false, elements_tab = 0x0, finfo = 0x0,
      fcinfo_data = 0x0, saop = 0x0}, xmlexpr = {xexpr = 0x0,
      named_argvalue = 0x0, named_argnull = 0x0, argvalue = 0x0,
      argnull = 0x0}, json_constructor = {jcstate = 0x0}, aggref = {
      aggno = 0}, grouping_func = {clauses = 0x0}, window_func = {
      wfstate = 0x0}, subplan = {sstate = 0x0}, agg_deserialize = {
--Type <RET> for more, q to quit, c to continue without paging--
      fcinfo_data = 0x0, jumpnull = 0}, agg_strict_input_check = {
      args = 0x0, nulls = 0x0, nargs = 0, jumpnull = 0},
    agg_plain_pergroup_nullcheck = {setoff = 0, jumpnull = 0},
    agg_presorted_distinctcheck = {pertrans = 0x0, aggcontext = 0x0,
      jumpdistinct = 0}, agg_trans = {pertrans = 0x0, aggcontext = 0x0,
      setno = 0, transno = 0, setoff = 0}, is_json = {pred = 0x0},
    jsonexpr = {jsestate = 0x0}, jsonexpr_coercion = {targettype = 0,
      targettypmod = 0, omit_quotes = false, exists_coerce = false,
      exists_cast_to_int = false, exists_check_domain = false,
      json_coercion_cache = 0x0, escontext = 0x0}}}




(gdb) print projInfo->pi_state->steps[2]
$7 = {opcode = 108824564994771, resvalue = 0x0, resnull = 0x0, d = {
    fetch = {last_var = 0, fixed = false, known_desc = 0x0, kind = 0x0},
    var = {attnum = 0, vartype = 0}, wholerow = {var = 0x0, first = false,
      slow = false, tupdesc = 0x0, junkFilter = 0x0}, assign_var = {
      resultnum = 0, attnum = 0}, assign_tmp = {resultnum = 0},
    constval = {value = 0, isnull = false}, func = {finfo = 0x0,
      fcinfo_data = 0x0, fn_addr = 0x0, nargs = 0, make_ro = false},
    boolexpr = {anynull = 0x0, jumpdone = 0}, qualexpr = {jumpdone = 0},
    jump = {jumpdone = 0}, nulltest_row = {rowcache = {cacheptr = 0x0,
        tupdesc_id = 0}}, param = {paramid = 0, paramtype = 0}, cparam = {
      paramfunc = 0x0, paramarg = 0x0, paramid = 0, paramtype = 0},
    casetest = {value = 0x0, isnull = 0x0}, make_readonly = {value = 0x0,
      isnull = 0x0}, iocoerce = {finfo_out = 0x0, fcinfo_data_out = 0x0,
      finfo_in = 0x0, fcinfo_data_in = 0x0}, sqlvaluefunction = {
      svf = 0x0}, nextvalueexpr = {seqid = 0, seqtypid = 0}, arrayexpr = {
      elemvalues = 0x0, elemnulls = 0x0, nelems = 0, elemtype = 0,
      elemlength = 0, elembyval = false, elemalign = 0 '\000',
      multidims = false}, arraycoerce = {elemexprstate = 0x0,
      resultelemtype = 0, amstate = 0x0}, row = {tupdesc = 0x0,
      elemvalues = 0x0, elemnulls = 0x0}, rowcompare_step = {finfo = 0x0,
      fcinfo_data = 0x0, fn_addr = 0x0, jumpnull = 0, jumpdone = 0},
    rowcompare_final = {rctype = 0}, minmax = {values = 0x0, nulls = 0x0,
      nelems = 0, op = IS_GREATEST, finfo = 0x0, fcinfo_data = 0x0},
    fieldselect = {fieldnum = 0, resulttype = 0, rowcache = {
        cacheptr = 0x0, tupdesc_id = 0}}, fieldstore = {fstore = 0x0,
      rowcache = 0x0, values = 0x0, nulls = 0x0, ncolumns = 0},
    sbsref_subscript = {subscriptfunc = 0x0, state = 0x0, jumpdone = 0},
    sbsref = {subscriptfunc = 0x0, state = 0x0}, domaincheck = {
      constraintname = 0x0, checkvalue = 0x0, checknull = 0x0,
      resulttype = 0, escontext = 0x0}, convert_rowtype = {inputtype = 0,
      outputtype = 0, incache = 0x0, outcache = 0x0, map = 0x0},
    scalararrayop = {element_type = 0, useOr = false, typlen = 0,
      typbyval = false, typalign = 0 '\000', finfo = 0x0,
      fcinfo_data = 0x0, fn_addr = 0x0}, hashedscalararrayop = {
      has_nulls = false, inclause = false, null_lhs_result = false,
      null_lhs_isnull = false, elements_tab = 0x0, finfo = 0x0,
      fcinfo_data = 0x0, saop = 0x0}, xmlexpr = {xexpr = 0x0,
      named_argvalue = 0x0, named_argnull = 0x0, argvalue = 0x0,
      argnull = 0x0}, json_constructor = {jcstate = 0x0}, aggref = {
      aggno = 0}, grouping_func = {clauses = 0x0}, window_func = {
      wfstate = 0x0}, subplan = {sstate = 0x0}, agg_deserialize = {
--Type <RET> for more, q to quit, c to continue without paging--
      fcinfo_data = 0x0, jumpnull = 0}, agg_strict_input_check = {
      args = 0x0, nulls = 0x0, nargs = 0, jumpnull = 0},
    agg_plain_pergroup_nullcheck = {setoff = 0, jumpnull = 0},
    agg_presorted_distinctcheck = {pertrans = 0x0, aggcontext = 0x0,
      jumpdistinct = 0}, agg_trans = {pertrans = 0x0, aggcontext = 0x0,
      setno = 0, transno = 0, setoff = 0}, is_json = {pred = 0x0},
    jsonexpr = {jsestate = 0x0}, jsonexpr_coercion = {targettype = 0,
      targettypmod = 0, omit_quotes = false, exists_coerce = false,
      exists_cast_to_int = false, exists_check_domain = false,
      json_coercion_cache = 0x0, escontext = 0x0}}}
(gdb)


\========================================================

Можем видеть:

step 0: opcode = 108824564996787 = 0x62f9b18a1ab3
step 1: opcode = 108824564996552 = 0x62f9b18a19c8
step 2: opcode = 108824564994771 = 0x62f9b18a12d3

Воспользуемся обратной таблицей диспетчеризации и определим,
какой opcode к какому типу инструкций относится.

\========================================================

(gdb) p reverse_dispatch_table
$14 = {{opcode = 0x62f9b18a12d3 <ExecInterpExpr+156>, op = EEOP_DONE}, {
    opcode = 0x62f9b18a12fa <ExecInterpExpr+195>,
    op = EEOP_INNER_FETCHSOME}, {
    opcode = 0x62f9b18a1330 <ExecInterpExpr+249>,
    op = EEOP_OUTER_FETCHSOME}, {
    opcode = 0x62f9b18a1366 <ExecInterpExpr+303>,
    op = EEOP_SCAN_FETCHSOME}, {
    opcode = 0x62f9b18a139f <ExecInterpExpr+360>, op = EEOP_INNER_VAR}, {
    opcode = 0x62f9b18a143b <ExecInterpExpr+516>, op = EEOP_OUTER_VAR}, {
    opcode = 0x62f9b18a14d7 <ExecInterpExpr+672>, op = EEOP_SCAN_VAR}, {
    opcode = 0x62f9b18a1573 <ExecInterpExpr+828>, op = EEOP_INNER_SYSVAR},
  {opcode = 0x62f9b18a15a2 <ExecInterpExpr+875>, op = EEOP_OUTER_SYSVAR}, {
    opcode = 0x62f9b18a15d1 <ExecInterpExpr+922>, op = EEOP_SCAN_SYSVAR}, {
    opcode = 0x62f9b18a1600 <ExecInterpExpr+969>, op = EEOP_WHOLEROW}, {
    opcode = 0x62f9b18a162e <ExecInterpExpr+1015>,
    op = EEOP_ASSIGN_INNER_VAR}, {
    opcode = 0x62f9b18a172d <ExecInterpExpr+1270>,
    op = EEOP_ASSIGN_OUTER_VAR}, {
    opcode = 0x62f9b18a182c <ExecInterpExpr+1525>,
    op = EEOP_ASSIGN_SCAN_VAR}, {
    opcode = 0x62f9b18a192b <ExecInterpExpr+1780>, op = EEOP_ASSIGN_TMP}, {
    opcode = 0x62f9b18a19c8 <ExecInterpExpr+1937>,
    op = EEOP_ASSIGN_TMP_MAKE_RO}, {
    opcode = 0x62f9b18a1ab3 <ExecInterpExpr+2172>, op = EEOP_CONST}, {
    opcode = 0x62f9b18a1ae9 <ExecInterpExpr+2226>, op = EEOP_FUNCEXPR}, {
    opcode = 0x62f9b18a1b56 <ExecInterpExpr+2335>,
    op = EEOP_FUNCEXPR_STRICT}, {
    opcode = 0x62f9b18a1c25 <ExecInterpExpr+2542>,
    op = EEOP_FUNCEXPR_FUSAGE}, {
    opcode = 0x62f9b18a1c53 <ExecInterpExpr+2588>,
    op = EEOP_FUNCEXPR_STRICT_FUSAGE}, {
    opcode = 0x62f9b18a1c81 <ExecInterpExpr+2634>,
    op = EEOP_BOOL_AND_STEP_FIRST}, {
    opcode = 0x62f9b18a1c8c <ExecInterpExpr+2645>,
    op = EEOP_BOOL_AND_STEP}, {
    opcode = 0x62f9b18a1cfe <ExecInterpExpr+2759>,
    op = EEOP_BOOL_AND_STEP_LAST}, {
    opcode = 0x62f9b18a1d61 <ExecInterpExpr+2858>,
    op = EEOP_BOOL_OR_STEP_FIRST}, {
    opcode = 0x62f9b18a1d6c <ExecInterpExpr+2869>,
    op = EEOP_BOOL_OR_STEP}, {
--Type <RET> for more, q to quit, c to continue without paging--
    opcode = 0x62f9b18a1ddb <ExecInterpExpr+2980>,
    op = EEOP_BOOL_OR_STEP_LAST}, {
    opcode = 0x62f9b18a1e3b <ExecInterpExpr+3076>,
    op = EEOP_BOOL_NOT_STEP}, {
    opcode = 0x62f9b18a1e85 <ExecInterpExpr+3150>, op = EEOP_QUAL}, {
    opcode = 0x62f9b18a1f0a <ExecInterpExpr+3283>, op = EEOP_JUMP}, {
    opcode = 0x62f9b18a1f35 <ExecInterpExpr+3326>,
    op = EEOP_JUMP_IF_NULL}, {
    opcode = 0x62f9b18a1f80 <ExecInterpExpr+3401>,
    op = EEOP_JUMP_IF_NOT_NULL}, {
    opcode = 0x62f9b18a1fce <ExecInterpExpr+3479>,
    op = EEOP_JUMP_IF_NOT_TRUE}, {
    opcode = 0x62f9b18a2033 <ExecInterpExpr+3580>,
    op = EEOP_NULLTEST_ISNULL}, {
    opcode = 0x62f9b18a206f <ExecInterpExpr+3640>,
    op = EEOP_NULLTEST_ISNOTNULL}, {
    opcode = 0x62f9b18a20bc <ExecInterpExpr+3717>,
    op = EEOP_NULLTEST_ROWISNULL}, {
    opcode = 0x62f9b18a20ea <ExecInterpExpr+3763>,
    op = EEOP_NULLTEST_ROWISNOTNULL}, {
    opcode = 0x62f9b18a2118 <ExecInterpExpr+3809>,
    op = EEOP_BOOLTEST_IS_TRUE}, {
    opcode = 0x62f9b18a2158 <ExecInterpExpr+3873>,
    op = EEOP_BOOLTEST_IS_NOT_TRUE}, {
    opcode = 0x62f9b18a21d3 <ExecInterpExpr+3996>,
    op = EEOP_BOOLTEST_IS_FALSE}, {
    opcode = 0x62f9b18a224e <ExecInterpExpr+4119>,
    op = EEOP_BOOLTEST_IS_NOT_FALSE}, {
    opcode = 0x62f9b18a228e <ExecInterpExpr+4183>, op = EEOP_PARAM_EXEC}, {
    opcode = 0x62f9b18a22bc <ExecInterpExpr+4229>,
    op = EEOP_PARAM_EXTERN}, {
    opcode = 0x62f9b18a22ea <ExecInterpExpr+4275>,
    op = EEOP_PARAM_CALLBACK}, {
    opcode = 0x62f9b18a231e <ExecInterpExpr+4327>,
    op = EEOP_CASE_TESTVAL}, {
    opcode = 0x62f9b18a2394 <ExecInterpExpr+4445>,
    op = EEOP_DOMAIN_TESTVAL}, {
    opcode = 0x62f9b18a240a <ExecInterpExpr+4563>,
    op = EEOP_MAKE_READONLY}, {
    opcode = 0x62f9b18a2460 <ExecInterpExpr+4649>, op = EEOP_IOCOERCE}, {
    opcode = 0x62f9b18a2671 <ExecInterpExpr+5178>,
--Type <RET> for more, q to quit, c to continue without paging--
    op = EEOP_IOCOERCE_SAFE}, {
    opcode = 0x62f9b18a2698 <ExecInterpExpr+5217>, op = EEOP_DISTINCT}, {
    opcode = 0x62f9b18a27ab <ExecInterpExpr+5492>,
    op = EEOP_NOT_DISTINCT}, {
    opcode = 0x62f9b18a289b <ExecInterpExpr+5732>, op = EEOP_NULLIF}, {
    opcode = 0x62f9b18a29bc <ExecInterpExpr+6021>,
    op = EEOP_SQLVALUEFUNCTION}, {
    opcode = 0x62f9b18a29e3 <ExecInterpExpr+6060>,
    op = EEOP_CURRENTOFEXPR}, {
    opcode = 0x62f9b18a2a0a <ExecInterpExpr+6099>,
    op = EEOP_NEXTVALUEEXPR}, {
    opcode = 0x62f9b18a2a31 <ExecInterpExpr+6138>, op = EEOP_ARRAYEXPR}, {
    opcode = 0x62f9b18a2a58 <ExecInterpExpr+6177>, op = EEOP_ARRAYCOERCE},
  {opcode = 0x62f9b18a2a86 <ExecInterpExpr+6223>, op = EEOP_ROW}, {
    opcode = 0x62f9b18a2aad <ExecInterpExpr+6262>,
    op = EEOP_ROWCOMPARE_STEP}, {
    opcode = 0x62f9b18a2bfb <ExecInterpExpr+6596>,
    op = EEOP_ROWCOMPARE_FINAL}, {
    opcode = 0x62f9b18a2d29 <ExecInterpExpr+6898>, op = EEOP_MINMAX}, {
    opcode = 0x62f9b18a2d50 <ExecInterpExpr+6937>, op = EEOP_FIELDSELECT},
  {opcode = 0x62f9b18a2d7e <ExecInterpExpr+6983>,
    op = EEOP_FIELDSTORE_DEFORM}, {
    opcode = 0x62f9b18a2dac <ExecInterpExpr+7029>,
    op = EEOP_FIELDSTORE_FORM}, {
    opcode = 0x62f9b18a2dda <ExecInterpExpr+7075>,
    op = EEOP_SBSREF_SUBSCRIPTS}, {
    opcode = 0x62f9b18a2e3d <ExecInterpExpr+7174>, op = EEOP_SBSREF_OLD}, {
    opcode = 0x62f9b18a2e3f <ExecInterpExpr+7176>,
    op = EEOP_SBSREF_ASSIGN}, {
    opcode = 0x62f9b18a2e3f <ExecInterpExpr+7176>,
    op = EEOP_SBSREF_FETCH}, {
    opcode = 0x62f9b18a2e73 <ExecInterpExpr+7228>,
    op = EEOP_CONVERT_ROWTYPE}, {
    opcode = 0x62f9b18a2ea1 <ExecInterpExpr+7274>,
    op = EEOP_SCALARARRAYOP}, {
    opcode = 0x62f9b18a2ec8 <ExecInterpExpr+7313>,
    op = EEOP_HASHED_SCALARARRAYOP}, {
    opcode = 0x62f9b18a2ef6 <ExecInterpExpr+7359>,
    op = EEOP_DOMAIN_NOTNULL}, {
    opcode = 0x62f9b18a2f1d <ExecInterpExpr+7398>,
    op = EEOP_DOMAIN_CHECK}, {
--Type <RET> for more, q to quit, c to continue without paging--
    opcode = 0x62f9b18a2f44 <ExecInterpExpr+7437>, op = EEOP_XMLEXPR}, {
    opcode = 0x62f9b18a2f6b <ExecInterpExpr+7476>,
    op = EEOP_JSON_CONSTRUCTOR}, {
    opcode = 0x62f9b18a2f99 <ExecInterpExpr+7522>, op = EEOP_IS_JSON}, {
    opcode = 0x62f9b18a2fc0 <ExecInterpExpr+7561>,
    op = EEOP_JSONEXPR_PATH}, {
    opcode = 0x62f9b18a3001 <ExecInterpExpr+7626>,
    op = EEOP_JSONEXPR_COERCION}, {
    opcode = 0x62f9b18a302f <ExecInterpExpr+7672>,
    op = EEOP_JSONEXPR_COERCION_FINISH}, {
    opcode = 0x62f9b18a3056 <ExecInterpExpr+7711>, op = EEOP_AGGREF}, {
    opcode = 0x62f9b18a30ee <ExecInterpExpr+7863>,
    op = EEOP_GROUPING_FUNC}, {
    opcode = 0x62f9b18a3115 <ExecInterpExpr+7902>, op = EEOP_WINDOW_FUNC},
  {opcode = 0x62f9b18a31b6 <ExecInterpExpr+8063>,
    op = EEOP_MERGE_SUPPORT_FUNC}, {
    opcode = 0x62f9b18a31e4 <ExecInterpExpr+8109>, op = EEOP_SUBPLAN}, {
    opcode = 0x62f9b18a3212 <ExecInterpExpr+8155>,
    op = EEOP_AGG_STRICT_DESERIALIZE}, {
    opcode = 0x62f9b18a324d <ExecInterpExpr+8214>,
    op = EEOP_AGG_DESERIALIZE}, {
    opcode = 0x62f9b18a3300 <ExecInterpExpr+8393>,
    op = EEOP_AGG_STRICT_INPUT_CHECK_ARGS}, {
    opcode = 0x62f9b18a338e <ExecInterpExpr+8535>,
    op = EEOP_AGG_STRICT_INPUT_CHECK_NULLS}, {
    opcode = 0x62f9b18a3415 <ExecInterpExpr+8670>,
    op = EEOP_AGG_PLAIN_PERGROUP_NULLCHECK}, {
    opcode = 0x62f9b18a34a2 <ExecInterpExpr+8811>,
    op = EEOP_AGG_PLAIN_TRANS_INIT_STRICT_BYVAL}, {
    opcode = 0x62f9b18a35c7 <ExecInterpExpr+9104>,
    op = EEOP_AGG_PLAIN_TRANS_STRICT_BYVAL}, {
    opcode = 0x62f9b18a36b6 <ExecInterpExpr+9343>,
    op = EEOP_AGG_PLAIN_TRANS_BYVAL}, {
    opcode = 0x62f9b18a378f <ExecInterpExpr+9560>,
    op = EEOP_AGG_PLAIN_TRANS_INIT_STRICT_BYREF}, {
    opcode = 0x62f9b18a38b1 <ExecInterpExpr+9850>,
    op = EEOP_AGG_PLAIN_TRANS_STRICT_BYREF}, {
    opcode = 0x62f9b18a399d <ExecInterpExpr+10086>,
    op = EEOP_AGG_PLAIN_TRANS_BYREF}, {
    opcode = 0x62f9b18a3a61 <ExecInterpExpr+10282>,
    op = EEOP_AGG_PRESORTED_DISTINCT_SINGLE}, {
--Type <RET> for more, q to quit, c to continue without paging--
    opcode = 0x62f9b18a3adc <ExecInterpExpr+10405>,
    op = EEOP_AGG_PRESORTED_DISTINCT_MULTI}, {
    opcode = 0x62f9b18a3b57 <ExecInterpExpr+10528>,
    op = EEOP_AGG_ORDERED_TRANS_DATUM}, {
    opcode = 0x62f9b18a3b85 <ExecInterpExpr+10574>,
    op = EEOP_AGG_ORDERED_TRANS_TUPLE}}
(gdb)

\========================================================

Итого:
step 0: EEOP_CONST
step 1: EEOP_ASSIGN_TMP_MAKE_RO
step 2: EEOP_DONE

Значит, на этапе исполнения запроса, STRICT уже обработан.
В данном случае, нулевой шаг устанавливает значение NULL.
В этом можно убедиться, взглянув на одно из полей в структуре:
constval = {value = 0, isnull = true}

Значит, решение о том, что результат выражения должен быть равен NULL было принято ещё раньше.
Нужно посмотреть момент, когда формируются steps

\========================================================