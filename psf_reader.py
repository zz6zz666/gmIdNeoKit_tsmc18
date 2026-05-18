#!/usr/bin/env python3
"""PSF ASCII reader for Spectre output."""
import os, numpy as np

_read_all_traces_cache = None
_read_all_traces_key = None


def _parse_ascii_psf(filepath):
    traces_order, section, all_vals = [], "header", []
    with open(filepath, encoding='latin-1') as fh:
        for line in fh:
            s = line.strip()
            if not s: continue
            if s in ("HEADER","TYPE","SWEEP","TRACE","VALUE"):
                section = s.lower(); continue
            if section == "trace":
                parts = s.split(chr(34))
                if len(parts) >= 3: traces_order.append(parts[1])
            elif section == "value":
                if s.startswith(chr(34)):
                    parts = s.split(chr(34))
                    name = parts[1] if len(parts) >= 2 else ""
                    if name == "gs": continue
                    if len(parts) >= 3:
                        try: all_vals.append(float(parts[2].strip()))
                        except ValueError: all_vals.append(0.0)
    if not all_vals or not traces_order: return {}, 0
    n_traces = len(traces_order)
    n_points = len(all_vals) // n_traces
    data = np.array(all_vals, dtype=np.float64).reshape(n_points, n_traces)
    result = {}
    for idx, name in enumerate(traces_order):
        result[name] = data[:, idx].copy()
    return result, data.shape[0]


def _read_all_traces(raw_dir):
    global _read_all_traces_cache, _read_all_traces_key
    if raw_dir == _read_all_traces_key:
        return _read_all_traces_cache

    dc_files = sorted([f for f in os.listdir(raw_dir) if f.endswith(".dc")])
    if not dc_files:
        raise FileNotFoundError("No .dc files in " + raw_dir)

    data = {}
    for fname in dc_files:
        traces, _ = _parse_ascii_psf(os.path.join(raw_dir, fname))
        for name, vals in traces.items():
            data.setdefault(name, []).append(vals)

    n_vds = len(dc_files)
    result = {}
    for name, chunks in data.items():
        result[name] = np.concatenate(chunks).reshape(n_vds, -1)
    _read_all_traces_key = raw_dir
    _read_all_traces_cache = result
    return result


def cds_srr(outfile, sweep_path, signal_name):
    raw_dir = outfile if os.path.isdir(outfile) else outfile + ".raw"
    if not os.path.isdir(raw_dir): raw_dir = outfile
    traces = _read_all_traces(raw_dir)
    if signal_name not in traces:
        avail = list(traces.keys())[:15]
        raise KeyError(signal_name + " not found. Available: " + str(avail) + "...")
    class R: pass
    r = R()
    setattr(r, "A", traces[signal_name])
    return r


def _parse_noise_psf(filepath):
    with open(filepath, encoding='latin-1') as fh:
        lines = list(fh)
    value_start = None
    for i, line in enumerate(lines):
        if line.strip() == "VALUE":
            value_start = i
            break
    if value_start is None:
        return {}
    field_names = ["rd","rs","rgbi","rbpd","rbps","rbpb","rbdb","rbsb",
                   "id","igs","igd","igb","fn","total"]
    n_fields = len(field_names)
    result = {}
    i = value_start + 1
    while i < len(lines):
        s = lines[i].strip()
        i += 1
        if not s:
            continue
        if s.startswith('"gs"'):
            continue
        if s.startswith('"'):
            parts = s.split(chr(34))
            name = parts[1]
            rest = parts[2].strip() if len(parts) >= 3 else ""
            if rest.startswith("("):
                vals = []
                vals_read = 0
                while i < len(lines) and vals_read < n_fields:
                    ls = lines[i].strip()
                    i += 1
                    if not ls: continue
                    if ls == "(": continue
                    if ls == ")" or ls == ");": break
                    for token in ls.split():
                        try:
                            vals.append(float(token))
                            vals_read += 1
                        except ValueError:
                            pass
                if vals:
                    result[name] = {}
                    for fi, fname in enumerate(field_names):
                        if fi < len(vals):
                            result[name][fname] = vals[fi]
            else:
                try:
                    result[name] = float(rest)
                except ValueError:
                    result[name] = 0.0
    return result


def cds_innersrr(outfile, sweep_path, signal_name, mode, n_vgs=None):
    raw_dir = outfile if os.path.isdir(outfile) else outfile + ".raw"
    if not os.path.isdir(raw_dir):
        raw_dir = outfile
    noise_files = sorted([f for f in os.listdir(raw_dir) if f.endswith(".noise")])
    if not noise_files:
        traces = _read_all_traces(raw_dir)
        values = traces.get(signal_name, np.zeros((n_vgs or 91, n_vgs or 91)))
        class R: pass
        r = R()
        r.field_names = ["A","_","__","V","___"]
        for fn in r.field_names: setattr(r, fn, values)
        return r
    trace_name = signal_name.split(":")[0] if ":" in signal_name else signal_name
    field_name = signal_name.split(":")[1] if ":" in signal_name else ""
    all_vals = []
    for fname in noise_files:
        data = _parse_noise_psf(os.path.join(raw_dir, fname))
        if field_name and trace_name in data and isinstance(data[trace_name], dict):
            all_vals.append(data[trace_name].get(field_name, 0.0))
        elif trace_name in data and isinstance(data[trace_name], (int, float)):
            all_vals.append(data[trace_name])
    nfiles = len(noise_files)
    nvgs = n_vgs or 91
    if len(all_vals) == nfiles:
        values = np.array(all_vals, dtype=np.float64).reshape(nfiles, 1)
        values = np.broadcast_to(values, (nfiles, nvgs)).T
    else:
        values = np.zeros((nvgs, nfiles))
    class R: pass
    r = R()
    r.field_names = ["A","_","__","V","___"]
    for fn in r.field_names: setattr(r, fn, values)
    return r
