#!/usr/bin/env python3
"""
Unified extraction script for 1.8V and 5V devices.
Produces .mat files compatible with gmIdSizing GUI format.

Usage:
  # Full extraction
  python extract_new.py --voltage 18 --fine --outdir <path> --workers 5

  # Incremental: only L range
  python extract_new.py --voltage 5v --fine --outdir <path> --L-range 0 5 --workers 5

  # Append to existing .mat
  python extract_new.py --voltage 5v --fine --outdir <path> --L-range 9 13 --workers 5
"""
import time, sys, os, numpy as np
from multiprocessing import Pool


def save_mat(filename, data_dict):
    import h5py
    with h5py.File(filename + '.mat', 'w') as f:
        for k, v in data_dict.items():
            if isinstance(v, str):
                dt = h5py.string_dtype()
                f.create_dataset(k, data=v, dtype=dt)
            else:
                f.create_dataset(k, data=np.array(v))
    print('  -> %s.mat' % filename)


def extract_one(raw_dir, c):
    from psf_reader import _read_all_traces, _parse_noise_psf

    dc_traces = _read_all_traces(raw_dir)

    dc_n, dc_p = {}, {}
    for (sig, units, coeffs) in c['n']:
        if sig in dc_traces:
            vals = dc_traces[sig].copy()
            for m, vname in enumerate(c['outvars']):
                if coeffs[m] != 0:
                    if vname not in dc_n:
                        dc_n[vname] = np.zeros_like(vals)
                    dc_n[vname] += vals * coeffs[m]

    for (sig, units, coeffs) in c['p']:
        if sig in dc_traces:
            vals = dc_traces[sig].copy()
            for m, vname in enumerate(c['outvars']):
                if coeffs[m] != 0:
                    if vname not in dc_p:
                        dc_p[vname] = np.zeros_like(vals)
                    dc_p[vname] += vals * coeffs[m]

    noise_n, noise_p = {}, {}
    noise_files = sorted([f for f in os.listdir(raw_dir) if f.endswith(".noise")])
    if noise_files:
        noise_data = [_parse_noise_psf(os.path.join(raw_dir, f)) for f in noise_files]
        nfiles = len(noise_files)

        for k, (sig, _) in enumerate(c['n_noise']):
            trace_name = sig.split(":")[0]
            field_name = sig.split(":")[1] if ":" in sig else ""
            nv = []
            for nd in noise_data:
                if field_name and trace_name in nd and isinstance(nd[trace_name], dict):
                    nv.append(nd[trace_name].get(field_name, 0.0))
                elif trace_name in nd and isinstance(nd[trace_name], (int, float)):
                    nv.append(nd[trace_name])
            if len(nv) == nfiles:
                noise_n[c['outvars_noise'][k]] = np.array(nv, dtype=np.float64)

        for k, (sig, _) in enumerate(c['p_noise']):
            trace_name = sig.split(":")[0]
            field_name = sig.split(":")[1] if ":" in sig else ""
            nv = []
            for nd in noise_data:
                if field_name and trace_name in nd and isinstance(nd[trace_name], dict):
                    nv.append(nd[trace_name].get(field_name, 0.0))
                elif trace_name in nd and isinstance(nd[trace_name], (int, float)):
                    nv.append(nd[trace_name])
            if len(nv) == nfiles:
                noise_p[c['outvars_noise'][k]] = np.array(nv, dtype=np.float64)

    return dc_n, dc_p, noise_n, noise_p


def make_mat_data(c, L_arr):
    nL = len(L_arr)
    nVGS = len(c['VGS'])
    nVDS = len(c['VDS'])
    nVSB = len(c['VSB'])
    d = {
        'INFO': c['modelinfo'], 'CORNER': c['corner'], 'TEMP': c['temp'],
        'NFING': np.array([[c['NFING']]]),
        'L': L_arr.reshape(1, -1),
        'W': np.array([[c['WIDTH']]]),
        'VGS': c['VGS'].reshape(1, -1),
        'VDS': c['VDS'].reshape(1, -1),
        'VSB': c['VSB'].reshape(1, -1),
    }
    for v in c['outvars']:
        d[v] = np.zeros((nVSB, nVDS, nVGS, nL))
    for v in c['outvars_noise']:
        d[v] = np.full((nVSB, nVDS, nVGS, nL), np.nan)
    return d


def extract_corner(corner, fine, outdir, l_range, voltage):
    if voltage == '5v':
        from config_tsmc18_5v import get_config
    else:
        from config_tsmc18 import get_config

    c = get_config(corner, coarse=not fine)
    nVGS = len(c['VGS'])
    nVDS = len(c['VDS'])
    nVSB = len(c['VSB'])
    rundir_base = os.path.join(outdir, c['rundir_base'])

    if voltage == '5v':
        L_n = c['LENGTH']
        L_p = c['LENGTH_p']
        all_L = sorted(set(L_n) | set(L_p))
        idx_n = {v: list(L_n).index(v) for v in all_L if v in L_n}
        idx_p = {v: list(L_p).index(v) for v in all_L if v in L_p}
    else:
        L_n = c['LENGTH']
        L_p = c['LENGTH']
        all_L = list(L_n)
        idx_n = {v: i for i, v in enumerate(all_L)}
        idx_p = {v: i for i, v in enumerate(all_L)}

    l_start, l_end = l_range
    l_start = max(0, l_start)
    l_end = min(len(all_L), l_end)

    print()
    print('===== Corner: %s =====' % corner)
    print('L range: %d..%d (%.3f..%.3f um)' %
          (l_start, l_end - 1, all_L[l_start], all_L[l_end - 1]))

    fn_n = os.path.join(outdir, c['savefilen'])
    fn_p = os.path.join(outdir, c['savefilep'])
    import h5py

    mat_n_exists = os.path.exists(fn_n + '.mat')
    mat_p_exists = os.path.exists(fn_p + '.mat')
    append_mode = mat_n_exists and mat_p_exists

    if not append_mode:
        print('  Creating: %s.mat' % fn_n)
        print('  Creating: %s.mat' % fn_p)
        save_mat(fn_n, make_mat_data(c, L_n))
        save_mat(fn_p, make_mat_data(c, L_p))
    else:
        print('  Appending to existing .mat files')

    t0 = time.time()
    processed = 0

    with h5py.File(fn_n + '.mat', 'r+') as f_n, \
         h5py.File(fn_p + '.mat', 'r+') as f_p:

        for ii in range(l_start, l_end):
            lval = all_L[ii]
            for j in range(nVSB):
                raw_dir = '%s/L%03d_%.3fum_VSB%03d_%+.2fV.raw' % (
                    rundir_base, ii, lval, j, c['VSB'][j])

                t1 = time.time()
                dc_n, dc_p, noise_n, noise_p = extract_one(raw_dir, c)
                elapsed = time.time() - t1

                if lval in idx_n:
                    in_n = idx_n[lval]
                    for vname, vals in dc_n.items():
                        f_n[vname][j, :, :, in_n] = vals
                    for vname, vals in noise_n.items():
                        nfiles = len(vals)
                        out = np.broadcast_to(
                            vals.reshape(1, nfiles), (nVGS, nfiles)).T
                        f_n[vname][j, :, :, in_n] = out

                if lval in idx_p:
                    ip = idx_p[lval]
                    for vname, vals in dc_p.items():
                        f_p[vname][j, :, :, ip] = vals
                    for vname, vals in noise_p.items():
                        nfiles = len(vals)
                        out = np.broadcast_to(
                            vals.reshape(1, nfiles), (nVGS, nfiles)).T
                        f_p[vname][j, :, :, ip] = out

                processed += 1
                print(' [%s] L=%.3fum VSB=%+.2fV ... OK (%.1fs)' %
                      (c['corner'], lval, c['VSB'][j], elapsed))

    t_total = time.time() - t0
    print('  [%s] %d combos in %.0fs' % (corner, processed, t_total))

    # Verify
    ok = _verify(fn_n + '.mat', l_start, l_end, all_L, idx_n, nVSB)
    ok &= _verify(fn_p + '.mat', l_start, l_end, all_L, idx_p, nVSB)
    if ok:
        print('  Verify OK')
    else:
        print('  Verify FAILED')
    return ok


def _verify(fname, l_start, l_end, all_L, idx_map, nVSB):
    import h5py
    try:
        with h5py.File(fname, 'r') as f:
            id_data = np.array(f['ID'])
            for ii in range(l_start, l_end):
                lval = all_L[ii]
                if lval not in idx_map:
                    continue
                idx = idx_map[lval]
                a = id_data[0, :, :, idx].sum()
                b = id_data[nVSB - 1, :, :, idx].sum()
                if abs(a) < 1e-20 and abs(b) < 1e-20:
                    print('  WARN: L=%.3fum has near-zero ID' % lval)
                    return False
                if np.allclose(a, b):
                    print('  WARN: L=%.3fum same VSB (cache bug?)' % lval)
                    return False
        return True
    except Exception as e:
        print('  Verify error: %s' % e)
        return False


def _worker(args):
    return extract_corner(*args)


def main():
    args = sys.argv[1:]
    voltage = '18'
    fine = '--fine' in args
    if fine:
        args.remove('--fine')
    outdir = ''
    if '--outdir' in args:
        idx = args.index('--outdir')
        args.pop(idx)
        outdir = args.pop(idx) if idx < len(args) else ''
    if '--voltage' in args:
        idx = args.index('--voltage')
        args.pop(idx)
        voltage = args.pop(idx) if idx < len(args) else '18'
    l_range = None
    if '--L-range' in args:
        idx = args.index('--L-range')
        args.pop(idx)
        if idx < len(args):
            s = int(args.pop(idx))
            e = int(args.pop(idx)) if idx < len(args) else s + 1
            l_range = (s, e)
    workers = 1
    if '--workers' in args:
        idx = args.index('--workers')
        args.pop(idx)
        workers = int(args.pop(idx)) if idx < len(args) else 1

    corners = args if args else ['tt', 'ff', 'ss', 'fs', 'sf']
    if not l_range:
        if voltage == '5v':
            from config_tsmc18_5v import get_config
        else:
            from config_tsmc18 import get_config
        c0 = get_config(corners[0], coarse=not fine)
        if voltage == '5v':
            nL = len(sorted(set(c0['LENGTH']) | set(c0['LENGTH_p'])))
        else:
            nL = len(c0['LENGTH'])
        l_range = (0, nL)

    print('Voltage: %sV  Fine: %s  Outdir: %s  Workers: %d  L-range: %d-%d' %
          (voltage, fine, outdir if outdir else '.', workers,
           l_range[0], l_range[1] - 1))

    t0 = time.time()
    tasks = [(c, fine, outdir, l_range, voltage) for c in corners]

    if workers <= 1:
        results = [_worker(t) for t in tasks]
    else:
        with Pool(workers) as pool:
            results = pool.map(_worker, tasks)

    failed = [corners[i] for i, r in enumerate(results) if not r]
    if failed:
        print('FAILED corners:', failed)
        sys.exit(1)
    print('All done in %.0fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
