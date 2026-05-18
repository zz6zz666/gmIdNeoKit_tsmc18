#!/usr/bin/env python3
"""5V device Spectre simulation runner (no data extraction)."""
import time, subprocess, sys, os
from multiprocessing import Pool
from config_tsmc18_5v import get_config, write_netlist


def run_sim_corner(args):
    corner, fine_flag, outdir, l_range = args
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    from config_tsmc18_5v import get_config, write_netlist
    c = get_config(corner, coarse=not fine_flag)

    L_n = c['LENGTH']
    L_p = c['LENGTH_p']
    all_L = sorted(set(L_n) | set(L_p))
    nVSB = len(c['VSB'])

    l_start, l_end = l_range
    l_start = max(0, l_start)
    l_end = min(len(all_L), l_end)

    idx_n = {v: list(L_n).index(v) for v in all_L if v in L_n}
    idx_p = {v: list(L_p).index(v) for v in all_L if v in L_p}

    c['rundir_base'] = os.path.join(outdir, c['rundir_base'])
    os.makedirs(c['rundir_base'], exist_ok=True)

    n_jobs = (l_end - l_start) * nVSB
    print()
    print("===== Corner: " + corner + "_5 =====")
    print("  L range %d..%d (%.3f..%.3f um) x %d VSB = %d jobs" %
          (l_start, l_end - 1, all_L[l_start], all_L[l_end - 1], nVSB, n_jobs))

    t_start = time.time()
    for ii in range(l_start, l_end):
        lval = all_L[ii]
        for j in range(nVSB):
            raw_dir = "%s/L%03d_%.3fum_VSB%03d_%+.2fV.raw" % (
                c['rundir_base'], ii, lval, j, c['VSB'][j])

            n_len = L_n[idx_n[lval]] if lval in idx_n else L_n[0]
            p_len = L_p[idx_p[lval]] if lval in idx_p else L_p[0]

            write_netlist(c, raw_dir)

            with open(c['paramfile'], 'w') as f:
                f.write('parameters nlength = %.10g\n' % n_len)
                f.write('parameters plength = %.10g\n' % p_len)
                f.write('parameters sb = %.10g\n' % c['VSB'][j])

            t0 = time.time()
            print(' [%s] L=%.3fum VSB=%+.2fV ... ' %
                  (c['corner'], lval, c['VSB'][j]), end='', flush=True)

            result = subprocess.run(c['simcmd'], shell=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    timeout=600)
            if result.returncode != 0:
                print('FAILED')
                print(result.stderr.decode()[-400:])
                return False
            print('OK (%.1fs)' % (time.time() - t0))
    print("  [%s] done in %.0fs" % (c['corner'], time.time() - t_start))
    return True


def main():
    args = sys.argv[1:]
    fine = '--fine' in args
    if fine:
        args.remove('--fine')
    outdir = ''
    if '--outdir' in args:
        idx = args.index('--outdir')
        args.pop(idx)
        outdir = args.pop(idx) if idx < len(args) else ''
    l_range = None
    if '--L-range' in args:
        idx = args.index('--L-range')
        args.pop(idx)
        if idx < len(args):
            s = int(args.pop(idx))
            e = int(args.pop(idx)) if idx < len(args) else s + 1
            l_range = (s, e)
    corners = args if args else ['tt', 'ff', 'ss', 'fs', 'sf']

    if l_range is None:
        from config_tsmc18_5v import get_config
        c = get_config(corners[0], coarse=not fine)
        all_L = sorted(set(c['LENGTH']) | set(c['LENGTH_p']))
        l_range = (0, len(all_L))

    if outdir:
        print('Output dir:', outdir)
    t0 = time.time()
    with Pool(len(corners)) as pool:
        results = pool.map(run_sim_corner, [(c, fine, outdir, l_range) for c in corners])
    failed = [corners[i] for i, r in enumerate(results) if not r]
    if failed:
        print('FAILED corners:', failed)
    print('Total: %.0fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
