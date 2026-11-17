SELECT array_contains(arr, (floor(random() * :n + 1)::int)) FROM bench_table;

SELECT array_contains_all(arr, ARRAY[(floor(random() * :n + 1)::int), (floor(random() * :n + 1)::int)]) FROM bench_table;

SELECT array_find_all(arr, (floor(random() * :n + 1)::int)) FROM bench_table;

SELECT array_index_of(arr, (floor(random() * :n + 1)::int)) FROM bench_table;

SELECT array_last_index_of(arr, (floor(random() * :n + 1)::int)) FROM bench_table;


SELECT array_filter(arr, 'x > ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_filter(arr, 'x < ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_filter(arr, 'x == ' || (floor(random() * :n + 1)::int)) FROM bench_table;
--SELECT array_filter(arr, 'x != ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_filter(arr, 'x >= ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_filter(arr, 'x <= ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_filter(
    arr,
    'x % ' || (floor(random() * :n + 1)::int) || '=' || (floor(random() * :n + 1)::int)) FROM bench_table;

SELECT array_reject(arr, 'x > ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_reject(arr, 'x < ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_reject(arr, 'x == ' || (floor(random() * :n + 1)::int)) FROM bench_table;
--SELECT array_reject(arr, 'x != ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_reject(arr, 'x >= ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_reject(arr, 'x <= ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_reject(
    arr,
    'x % ' || (floor(random() * :n + 1)::int) || '=' || (floor(random() * :n + 1)::int)) FROM bench_table;


SELECT array_partition(arr, 'x > ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_partition(arr, 'x < ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_partition(arr, 'x == ' || (floor(random() * :n + 1)::int)) FROM bench_table;
--SELECT array_partition(arr, 'x != ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_partition(arr, 'x >= ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_partition(arr, 'x <= ' || (floor(random() * :n + 1)::int)) FROM bench_table;
SELECT array_partition(
    arr,
    'x % ' || (floor(random() * :n + 1)::int) || '=' || (floor(random() * :n + 1)::int)) FROM bench_table;
