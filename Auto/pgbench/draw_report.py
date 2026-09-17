from pathlib import Path 
from pgbench_config import *
import re 
import matplotlib.pyplot as plt



def parse_name(path: Path) -> tuple[int, int, int] | None:
    m = re.search(r'S(\d+)MBL([10])C(\d+)', path.name)
    if m is not None:
        return (int(m.group(1)),int(m.group(2)),int(m.group(3)))
    return None

def parse_mean_results(path: Path) -> tuple[float, float]:
    text = path.read_text()
    m = re.findall(r'tps=([\d.]+);latency=([\d.]+)', text, re.MULTILINE)
    if m:
        results = [(float(tps), float(lat)) for tps, lat in m]
        mean_tps = sum([results[i][0] for i in range(len(results))])/float(len(results))
        mean_lat = sum([results[i][1] for i in range(len(results))])/float(len(results))
        return (mean_tps, mean_lat)
    return None

def process_files(path: Path):

    processed = []
    files = list(path.iterdir())
    for file in files:
        name_params = parse_name(file)
        mean_res = parse_mean_results(file)
        #processed.append(
        #    [name_params[0], name_params[1], name_params[2], mean_res[0], mean_res[1]])
        processed.append(
            {'shared_memory':name_params[0], 'with_lib': name_params[1], 'clients': name_params[2],
             'mean tps': mean_res[0], 'mean lat': mean_res[1]}
        )
    return processed
def draw_any(results: list[dict], name: str):
    configurations = [
        (512, 0),
        (512, 1),
        (1024, 0),
        (1024, 1),
    ]

    plt.figure(figsize=(10, 6))

    for shared_memory, with_lib in configurations:
        data = [
            result for result in results
            if result['shared_memory'] == shared_memory
            and result['with_lib'] == with_lib
        ]

        data.sort(key=lambda x: x['clients'])

        clients = [result['clients'] for result in data]
        val = [result[name] for result in data]

        # Цвет показывает объём shared_buffers:
        # 512 MB -> синий
        # 1024 MB -> красный
        color = 'blue' if shared_memory == 512 else 'red'

        # Стиль линии показывает наличие библиотеки:
        # with_lib=0 -> пунктир
        # with_lib=1 -> сплошная
        linestyle = '--' if with_lib == 0 else '-'

        label = (
            f'{shared_memory} MB, '
            f'pg_stat_statements='
            f'{"yes" if with_lib else "no"}'
        )

        plt.plot(
            clients,
            val,
            color=color,
            linestyle=linestyle,
            marker='o',
            label=label
        )

    plt.xlabel('Clients')
    plt.ylabel(name)
    plt.title(name)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def draw_tps(path: Path):
    draw_any(process_files(path), 'mean tps')

def draw_lat(path: Path):
    draw_any(process_files(path), 'mean lat')