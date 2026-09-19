import re, subprocess, argparse
from pgbench_config import *
from draw_report import draw_tps, draw_lat


def set_postgresqlconf_param(param: str, value: str):
    path = path_to_postgres_conf
    with open(path, 'r') as f:
        text = f.read()

    text = re.sub(
        rf'^(#?){re.escape(param)}\s*=.*$', # re.escape - экранирование
        f'{param} = \'{value}\'',
        text,
        flags=re.MULTILINE
    )

    with open(path, 'w') as f:
        f.write(text)

def set_shared_preload_libraries(libs: str):
    set_postgresqlconf_param('shared_preload_libraries', libs)

def set_shared_buffer(size: str):
    set_postgresqlconf_param('shared_buffers', size)

def delete_extension(lib: str):
    subprocess.run(f"psql -h {host} -p {port} -U {user} -d {db} "
                   f"-c 'DROP EXTENSION IF EXISTS {lib};'", shell=True)

def create_extension(lib: str):
    subprocess.run(f"psql -h {host} -p {port} -U {user} -d {db} "
                   f"-c 'CREATE EXTENSION IF NOT EXISTS {lib};'", shell=True)

def setup(shared_buffer: str, lib: str):
    set_shared_preload_libraries(lib)
    set_shared_buffer(shared_buffer)

def startup(lib: str):
    subprocess.run(f'pg_ctl start -D {pgdata}', shell=True)
    if (lib != ''):
        create_extension(lib)

def shutdown(lib: str):
    if (lib != ''):
        delete_extension(lib)
    subprocess.run(f'pg_ctl stop -D {pgdata}', shell=True)

def save(result: list, path: str | Path):
    with open(path, 'a') as file:
        file.write(f"(iter={result[0]}:[tps={result[1]};latency={result[2]}])\n")


def bench(client_num: int):
    result = subprocess.run(f'pgbench -c {client_num} -j $(nproc) -t {transactions} {db}',
                            shell=True, capture_output=True)
    
    lat_aver = re.search(r'^\s*latency average = (\d+\.\d+)', result.stdout.decode(), re.MULTILINE)
    tps = re.search(r'^\s*tps = (\d+\.\d+)', result.stdout.decode(), re.MULTILINE)
    if lat_aver and tps:
        lat_aver = float(lat_aver.group(1))
        tps = float(tps.group(1))

    return [tps, lat_aver]

def init_cluster():
    subprocess.run(f'pg_ctl init -D {pgdata} -o "-U {user}"', shell=True)

def init():
    startup('')
    subprocess.run(f'createdb -h {host} -p {port} -U {user} {db}', shell=True)
    subprocess.run(f'pgbench -i -s{scale_factor} {db}', shell=True)
    shutdown('')

def run():
    reports_path.mkdir(parents=True, exist_ok=True)
    for shared_buffer in shared_buffers:
        for lib in libs:
            setup(shared_buffer, lib)
            startup(lib)
            for client_num in client_nums:
                for i in iters:
                    result = [i] + bench(client_num)
                    save(result, (reports_path / f'S{shared_buffer}L{int(lib!='')}C{client_num}.report'))
            shutdown(lib)

def clear():
    # Be careful!!!!!!!!!!!!
    subprocess.run(f'rm -rf {reports_path}', shell=True)

def draw():
    draw_lat(reports_path)
    draw_tps(reports_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--init', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--draw', action='store_true')
    parser.add_argument('--clear', action='store_true')
    parser.add_argument('--init-cluster', action='store_true')

    args = parser.parse_args()
    
    if args.init_cluster:
        init_cluster()
    if args.init:
        init()
    if args.run:
        run()
    if args.draw:
        draw()
    if args.clear:
        clear()

if __name__ == '__main__':
    main()