import subprocess, re, argparse, matplotlib.pyplot as plt
from config import *

def reload_postgres_server():
    subprocess.run(f'pg_ctl restart -D {path_to_pgdata}', shell=True)

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

def set_shared_buffers(size: str):
    '''
        min: 128 kB
    '''
    set_postgresqlconf_param('shared_buffers', size)


def run_bench(iter: int, clients: int, transactions: int, db: str):
    
    results = {}
    for i in range(iter):
        result = subprocess.run(f'pgbench -c {clients} -j $(nproc) -t {transactions} {db}',
                                shell=True, capture_output=True)
        
        '''
        latency average = 3.858 ms
        initial connection time = 6.921 ms
        tps = 2592.096542 (without initial connection time)
        '''
        lat_aver = re.search('^\s*latency average = (\d+\.\d+)', result.stdout.decode(), re.MULTILINE)
        tps = re.search('^\s*tps = (\d+\.\d+)', result.stdout.decode(), re.MULTILINE)
        if lat_aver and tps:
            lat_aver = float(lat_aver.group(1))
            tps = float(tps.group(1))
        
        results[f'iteration: {i}'] = [lat_aver, tps]

    return results
    

def medium_values(result: dict):
    flen_res = float(len(result))
    lat = 0.0
    tps = 0.0
    for k in result:
        lat += result[k][0]
        tps += result[k][1]

    lat /= flen_res
    tps /= flen_res
    print(f'\nmedium latency: {lat}, medium tps: {tps}\n')

def draw_report(result: dict):
    x = range(1, len(result) + 1)

    lat = []
    tps = []
    for k in result:
        lat.append(result[k][0])
        tps.append(result[k][1])

    print(lat, tps)

    fig, ax = plt.subplots(2,1)

    ax[0].plot(x, lat, 'o-')
    ax[0].set_xlabel('Iteration')
    ax[0].set_ylabel('Latency, ms')
    ax[0].grid()

    ax[1].plot(x, tps, 'o-')
    ax[1].set_xlabel('Iteration')
    ax[1].set_ylabel('TPS, ms')
    ax[1].grid()

    plt.tight_layout()
    plt.show()

#create & delete extension

def delete_extension():
    for extension_name in extension_names:
        subprocess.run(f"psql -h {host} -p {port} -U {user} -d {db_name} "
                       f"-c 'DROP EXTENSION IF EXISTS {extension_name};'", shell=True)

def create_extension():
    for extension_name in extension_names:
        subprocess.run(f"psql -h {host} -p {port} -U {user} -d {db_name} "
                       f"-c 'CREATE EXTENSION {extension_name};'", shell=True)

def configure():
    set_shared_buffers(shared_buffers)
    set_shared_preload_libraries(librarie_names)

def main():

    subprocess.run('clear', shell=True)
    parser = argparse.ArgumentParser()

    parser.add_argument('--draw', choices=['yes', 'no'], required=False)
    args = parser.parse_args()
    
    configure()
    reload_postgres_server()
    if (args.withlib == 'yes'):
        create_extension()
    
    
    r = run_bench(iters, clients, transactions, 'pg_bench_test')
    
    
    if (args.withlib == 'yes'):
        delete_extension()

    if (args.draw == 'yes'):
        draw_report(r)
    medium_values(r)


if __name__ == '__main__':
    main()