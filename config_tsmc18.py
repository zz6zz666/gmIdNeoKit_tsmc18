"""
Configuration for TSMC 1.8V device sweep.
Output format compatible with gmIdSizing GUI (dash-separated filenames, row vectors).
"""
import numpy as np


def get_config(corner="tt", coarse=True):
    c = {}

    c['corner'] = corner
    c['modelfile'] = (
        '"/home/work/TM018/TSMC018/models/spectre/cmn018_gp2a_5v_v1d4.scs"'
        f' section={c["corner"]}'
    )
    c['modelinfo'] = 'tsmc18, BSIM4'
    c['temp'] = 300
    c['modeln'] = 'nch'
    c['modelp'] = 'pch'
    c['simcmd'] = (f'/opt/MMSIM151/bin/spectre -64 techsweep_tsmc18_{corner}.scs '
                   f'+log techsweep_tsmc18_{corner}.out')
    c['rundir_base'] = f'raw_tsmc18_{corner}'
    c['paramfile'] = f'techsweep_params_tsmc18_{corner}.scs'
    c['sweep'] = 'sweepvds_sweepvgs-sweep'
    c['sweep_noise'] = 'sweepvds_noise_sweepvgs_noise-sweep'

    if coarse:
        c['VGS_step'] = 0.02
        c['VDS_step'] = 0.02
        c['VSB_step'] = 0.15
        c['VGS_max'] = 1.8
        c['VDS_max'] = 1.8
        c['VSB_max'] = 0.3
        c['LENGTH'] = np.arange(0.18, 0.25 + 0.07 / 2, 0.07)
        c['savefilen'] = f'tsmc18_coarse-nch-{corner}'
        c['savefilep'] = f'tsmc18_coarse-pch-{corner}'
    else:
        c['VGS_step'] = 0.01
        c['VDS_step'] = 0.01
        c['VSB_step'] = 0.1
        c['VGS_max'] = 1.8
        c['VDS_max'] = 1.8
        c['VSB_max'] = 0.6
        c['LENGTH'] = np.array([0.18,0.2,0.25,0.3,0.35,0.5,0.6,0.7,0.8,1.0,1.5,2.0])
        c['savefilen'] = f'tsmc18-nch-{corner}'
        c['savefilep'] = f'tsmc18-pch-{corner}'

    c['VGS'] = np.arange(0, c['VGS_max'] + c['VGS_step'] / 2, c['VGS_step'])
    c['VDS'] = np.arange(0, c['VDS_max'] + c['VDS_step'] / 2, c['VDS_step'])
    c['VSB'] = np.flip(np.arange(0, c['VSB_max'] + c['VSB_step'] / 2, c['VSB_step']))
    c['WIDTH'] = 5
    c['NFING'] = 2

    # 19 output variables: 18 original + VDSAT for GUI compatibility
    c['outvars'] = [
        'ID','VT','IGD','IGS','GM','GMB','GDS',
        'CGG','CGS','CSG','CGD','CDG','CGB','CDD','CSS',
        'FUG','GMOVERID','SELF_GAIN','VDSAT',
    ]
    # Coeffs: ID,VT,IGD,IGS,GM,GMB,GDS,CGG,CGS,CSG,CGD,CDG,CGB,CDD,CSS,FUG,GMOVERID,SELF_GAIN,VDSAT
    c['n'] = [
        ('mn:ids','A',        [1, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:vth','V',        [0, 1,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:igd','A',        [0, 0,1,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:igs','A',        [0, 0,0,1,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:gm', 'S',        [0, 0,0,0,1,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:gmbs','S',       [0, 0,0,0,0,1,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:gds','S',        [0, 0,0,0,0,0,1, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:cgg','F',        [0, 0,0,0,0,0,0, 1, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:cgs','F',        [0, 0,0,0,0,0,0, 0,-1, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:cgd','F',        [0, 0,0,0,0,0,0, 0, 0, 0,-1, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:cgb','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0,-1, 0, 0, 0,0,0,0]),
        ('mn:cdd','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 1, 0, 0,0,0,0]),
        ('mn:cdg','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0,-1, 0, 0, 0, 0,0,0,0]),
        ('mn:css','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0,0,0,0]),
        ('mn:csg','F',        [0, 0,0,0,0,0,0, 0, 0,-1, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn:cjd','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 1, 0, 0,0,0,0]),
        ('mn:cjs','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0,0,0,0]),
        ('mn:fug','Hz',       [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 1,0,0,0]),
        ('mn:gmoverid','V',   [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,1,0,0]),
        ('mn:self_gain','rall',[0,0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,1,0]),
        ('mn:vdsat','V',      [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,1]),
    ]

    c['p'] = [
        ('mp:ids','A',        [-1,0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:vth','V',        [0,-1, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:igd','A',        [0, 0,-1, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:igs','A',        [0, 0, 0,-1,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:gm', 'S',        [0, 0, 0, 0,1,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:gmbs','S',       [0, 0, 0, 0,0,1,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:gds','S',        [0, 0, 0, 0,0,0,1, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:cgg','F',        [0, 0, 0, 0,0,0,0, 1, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:cgs','F',        [0, 0, 0, 0,0,0,0, 0,-1, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:cgd','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0,-1, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:cgb','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0,-1, 0, 0, 0,0,0,0]),
        ('mp:cdd','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 1, 0, 0,0,0,0]),
        ('mp:cdg','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0,-1, 0, 0, 0, 0,0,0,0]),
        ('mp:css','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0,0,0,0]),
        ('mp:csg','F',        [0, 0, 0, 0,0,0,0, 0, 0,-1, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp:cjd','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 1, 0, 0,0,0,0]),
        ('mp:cjs','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0,0,0,0]),
        ('mp:fug','Hz',       [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 1,0,0,0]),
        ('mp:gmoverid','V',   [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,1,0,0]),
        ('mp:self_gain','rall',[0,0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,1,0]),
        ('mp:vdsat','V',      [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,1]),
    ]

    c['outvars_noise'] = ['STH', 'SFL']
    c['n_noise'] = [('mn:id',''), ('mn:fn','')]
    c['p_noise'] = [('mp:id',''), ('mp:fn','')]

    c['_netlist_tmpl'] = (
        f'//techsweep_tsmc18_{corner}.scs ' '\n'
        'include  %s\n'
        f'include "{c["paramfile"]}" ' '\n'
        'save mn \n'
        'save mp \n'
        'parameters gs=0 ds=0 \n'
        'vnoi     (vx  0)         vsource dc=0  \n'
        'vdsn     (vdn vx)        vsource dc=ds  \n'
        'vgsn     (vgn 0)         vsource dc=gs  \n'
        'vbsn     (vbn 0)         vsource dc=-sb \n'
        'vdsp     (vdp vx)        vsource dc=-ds \n'
        'vgsp     (vgp 0)         vsource dc=-gs \n'
        'vbsp     (vbp 0)         vsource dc=sb  \n'
        '\n'
        'mn       (vdn vgn 0 vbn) %s  l=length*1e-6 w=%de-6 m=%d \n'
        'mp       (vdp vgp 0 vbp) %s  l=length*1e-6 w=%de-6 m=%d \n'
        '\n'
        'simOptions options gmin=1e-13 reltol=1e-4 vabstol=1e-6 iabstol=1e-10 '
        'temp=%d tnom=27 rawfmt=psfascii rawfile="%s" \n'
        'sweepvds sweep param=ds start=0 stop=%.10g step=%.10g { \n'
        '   sweepvgs dc param=gs start=0 stop=%.10g step=%.10g \n'
        '}\n'
        'sweepvds_noise sweep param=ds start=0 stop=%.10g step=%.10g { \n'
        '   sweepvgs_noise noise freq=1 oprobe=vnoi param=gs start=0 stop=%.10g step=%.10g \n'
        '}\n'
    )

    return c


def write_netlist(c, raw_dir):
    netlist = c['_netlist_tmpl'] % (
        c['modelfile'],
        c['modeln'], c['WIDTH'], c['NFING'],
        c['modelp'], c['WIDTH'], c['NFING'],
        c['temp'] - 273, raw_dir,
        c['VDS_max'], c['VDS_step'],
        c['VGS_max'], c['VGS_step'],
        c['VDS_max'], c['VDS_step'],
        c['VGS_max'], c['VGS_step'],
    )
    netlist_file = f'techsweep_tsmc18_{c["corner"]}.scs'
    with open(netlist_file, 'w') as fid:
        fid.write(netlist)
    return netlist_file
