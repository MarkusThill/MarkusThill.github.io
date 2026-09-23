"""Execute this companion's plain Python cells and store standard notebook outputs.

A small CPU-only runner for environments without Jupyter installed. It executes
cells in one fresh namespace and captures stdout and Matplotlib display output.
It deliberately rejects magics; use Jupyter for notebooks that require them.
"""
import argparse
import base64
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import time

os.environ.setdefault('MPLBACKEND', 'Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT = ROOT / 'assets/jupyter/MarkusThill.github.io-jupyter/2025_09_27_online_estimate_cov_mu.ipynb'

def run(path, output_dir):
    os.environ['ONLINE_ESTIMATION_OUTPUT_DIR'] = str(output_dir)
    notebook = json.loads(path.read_text())
    namespace = {'__name__': '__main__'}
    count = 0
    started = time.perf_counter()
    summaries = []
    original_show = plt.show
    try:
        for index, cell in enumerate(notebook['cells']):
            if cell['cell_type'] != 'code':
                continue
            count += 1
            source = ''.join(cell['source'])
            cell['outputs'] = []
            cell['execution_count'] = count
            buffer = io.StringIO()
            def flush():
                value = buffer.getvalue()
                if value:
                    cell['outputs'].append({'output_type': 'stream', 'name': 'stdout', 'text': value.splitlines(keepends=True)})
                    buffer.seek(0); buffer.truncate(0)
            def capture_show(*args, **kwargs):
                flush()
                for number in plt.get_fignums():
                    fig = plt.figure(number)
                    png = io.BytesIO()
                    fig.savefig(png, format='png', bbox_inches='tight')
                    cell['outputs'].append({'output_type': 'display_data', 'metadata': {}, 'data': {
                        'image/png': base64.b64encode(png.getvalue()).decode('ascii'),
                        'text/plain': [f'Matplotlib figure with {len(fig.axes)} axes']}})
                    plt.close(fig)
            plt.show = capture_show
            with contextlib.redirect_stdout(buffer):
                exec(compile(source, f'{path.name}:cell-{index}', 'exec'), namespace)
            flush()
            text = ''.join(''.join(o.get('text', [])) for o in cell['outputs'] if o['output_type'] == 'stream')
            summaries.append({'cell': index, 'execution_count': count, 'stdout': text})
            print(f'Cell {index} passed', flush=True)
        path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False)+'\n')
    finally:
        plt.show = original_show
        plt.close('all')
    report = {'notebook': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'execution': 'All plain Python code cells, sequentially in a fresh namespace; stdout and figures captured. No Jupyter kernel required.',
        'python': platform.python_version(), 'numpy': np.__version__,
        'seconds': time.perf_counter()-started, 'code_cells': count, 'cells': summaries}
    # Diagnostics the notebook chose to expose, if present. Kept optional so that
    # restructuring the notebook does not break the runner.
    for key, name in [('finite_effective_size', 'n_mem_finite'),
                      ('limiting_effective_size', 'n_mem_limit'),
                      ('decay', 'lam'), ('observations_per_experiment', 'size'),
                      ('experiments', 'n_experiments')]:
        if name in namespace:
            report[key] = float(namespace[name])
    for key, name in [('predicted_mean_covariance', 'expected_Sigma_mean'),
                      ('empirical_mean_covariance', 'actual_Sigma_mean')]:
        if name in namespace:
            report[key] = np.asarray(namespace[name]).tolist()
    (HERE/'notebook-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='cells'},indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notebook', type=Path, default=DEFAULT)
    parser.add_argument('--output-dir', type=Path, default=ROOT/'assets/img/2026-online-estimation')
    args = parser.parse_args()
    run(args.notebook, args.output_dir)
