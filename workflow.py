#!/usr/bin/env python3
"""
Master workflow: simulate -> extract -> cleanup for TSMC 1.8V & 5V devices.

Usage:
  python workflow.py --outdir /mnt/hgfs/share/tsmc18_out

Flow:
  1.8V:  simulate all L (parallel) -> extract (parallel) -> delete raw
  5V:
    Phase 1: simulate L[0:5]  -> extract -> delete raw
    Phase 2: simulate L[5:9]  -> extract -> delete raw
    Phase 3: simulate L[9:13] -> extract -> delete raw
"""
import subprocess, sys, os, shutil, glob, time

OUTDIR = ''
FINE = False
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable or 'python3'
WORKERS = 5


def run(cmd, step_name):
    print('\n' + '=' * 60)
    print('STEP: %s' % step_name)
    print('CMD:  %s' % cmd)
    print('=' * 60)
    t0 = time.time()
    result = subprocess.run(cmd, shell=True, cwd=SCRIPT_DIR)
    if result.returncode != 0:
        print('\n*** FAILED at: %s ***' % step_name)
        sys.exit(1)
    print('  ... done in %.0fs' % (time.time() - t0))


def delete_raw(base, l_indices=None):
    """Delete raw directories. If l_indices is None, delete the entire base dir."""
    pattern = os.path.join(OUTDIR, base)
    for corner in ['tt', 'ff', 'ss', 'fs', 'sf']:
        corner_dir = pattern.replace('{corner}', corner)
        if not os.path.isdir(corner_dir):
            continue
        if l_indices is None:
            shutil.rmtree(corner_dir, ignore_errors=True)
        else:
            for i_str in l_indices:
                for entry in os.listdir(corner_dir):
                    if entry.startswith('L%s_' % i_str):
                        full = os.path.join(corner_dir, entry)
                        shutil.rmtree(full, ignore_errors=True)
    if l_indices is None:
        print('  Deleted entire raw dir for %s' % base)
    else:
        print('  Deleted raw for L indices: %s' % l_indices)


def main():
    global OUTDIR, FINE, WORKERS
    args = sys.argv[1:]

    if '--fine' in args:
        FINE = True
        args.remove('--fine')
    if '--outdir' in args:
        idx = args.index('--outdir')
        args.pop(idx)
        OUTDIR = args.pop(idx) if idx < len(args) else ''
    if '--workers' in args:
        idx = args.index('--workers')
        args.pop(idx)
        WORKERS = int(args.pop(idx)) if idx < len(args) else WORKERS

    if not OUTDIR:
        print('Usage: python workflow.py --outdir <path> [--fine] [--workers N]')
        sys.exit(1)

    fine_flag = '--fine' if FINE else ''
    print('OUTDIR:  %s' % OUTDIR)
    print('FINE:    %s' % FINE)
    print('WORKERS: %d' % WORKERS)

    # ===================================================================
    # 1.8V: simulate all L -> extract -> delete raw
    # ===================================================================
    run(f'{PYTHON} run_sim.py {fine_flag} --outdir {OUTDIR}',
        '1.8V simulation (all L)')
    run(f'{PYTHON} extract_new.py --voltage 18 {fine_flag} --outdir {OUTDIR} --workers {WORKERS}',
        '1.8V extraction')
    delete_raw('raw_tsmc18_{corner}', None)

    # ===================================================================
    # 5V Phase 1: L[0:5] = 0.5~1.0 um
    # ===================================================================
    run(f'{PYTHON} run_sim_5v.py {fine_flag} --outdir {OUTDIR} --L-range 0 5',
        '5V Phase 1 simulation (L=0.5~1.0)')
    run(f'{PYTHON} extract_new.py --voltage 5v {fine_flag} --outdir {OUTDIR} --L-range 0 5 --workers {WORKERS}',
        '5V Phase 1 extraction')
    delete_raw('raw_tsmc18_5v_{corner}',
               ['000', '001', '002', '003', '004'])

    # ===================================================================
    # 5V Phase 2: L[5:9] = 1.2~3.0 um
    # ===================================================================
    run(f'{PYTHON} run_sim_5v.py {fine_flag} --outdir {OUTDIR} --L-range 5 9',
        '5V Phase 2 simulation (L=1.2~3.0)')
    run(f'{PYTHON} extract_new.py --voltage 5v {fine_flag} --outdir {OUTDIR} --L-range 5 9 --workers {WORKERS}',
        '5V Phase 2 extraction')
    delete_raw('raw_tsmc18_5v_{corner}',
               ['005', '006', '007', '008'])

    # ===================================================================
    # 5V Phase 3: L[9:13] = 4.0~10.0 um
    # ===================================================================
    run(f'{PYTHON} run_sim_5v.py {fine_flag} --outdir {OUTDIR} --L-range 9 13',
        '5V Phase 3 simulation (L=4.0~10.0)')
    run(f'{PYTHON} extract_new.py --voltage 5v {fine_flag} --outdir {OUTDIR} --L-range 9 13 --workers {WORKERS}',
        '5V Phase 3 extraction')
    delete_raw('raw_tsmc18_5v_{corner}',
               ['009', '010', '011', '012'])

    print('\n' + '=' * 60)
    print('ALL DONE')
    print('=' * 60)


if __name__ == '__main__':
    main()
