"""
Configuration for TSMC 5V device sweep.
Output format compatible with gmIdSizing GUI (dash-separated filenames, row vectors).
"""
import numpy as np


def get_config(corner="tt", coarse=True):
    c = {}

    c['corner'] = corner
    c['modelfile'] = (
        '"/home/work/TM018/TSMC018/models/spectre/cmn018_gp2a_5v_v1d4.scs"'
        f' section={c["corner"]}_5'
    )
    c['modelinfo'] = 'tsmc18, BSIM4, 5V'
    c['temp'] = 300
    c['modeln'] = 'nch_5'
    c['modelp'] = 'pch_5'
    c['simcmd'] = (f'/opt/MMSIM151/bin/spectre -64 techsweep_tsmc18_5v_{corner}.scs '
                   f'+log techsweep_tsmc18_5v_{corner}.out')
    c['rundir_base'] = f'raw_tsmc18_5v_{corner}'
    c['paramfile'] = f'techsweep_params_tsmc18_5v_{corner}.scs'
    c['sweep'] = 'sweepvds_sweepvgs-sweep'
    c['sweep_noise'] = 'sweepvds_noise_sweepvgs_noise-sweep'

    if coarse:
        c['VGS_step'] = 0.05
        c['VDS_step'] = 0.05
        c['VSB_step'] = 0.5
        c['VGS_max'] = 5.5
        c['VDS_max'] = 5.5
        c['VSB_max'] = 5.0
        c['LENGTH'] = np.array([0.6, 0.7, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 5.0])
        c['LENGTH_p'] = np.array([0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 5.0])
        c['savefilen'] = f'tsmc18_coarse-nch_5-{corner}'
        c['savefilep'] = f'tsmc18_coarse-pch_5-{corner}'
    else:
        c['VGS_step'] = 0.025
        c['VDS_step'] = 0.025
        c['VSB_step'] = 0.25
        c['VGS_max'] = 5.5
        c['VDS_max'] = 5.5
        c['VSB_max'] = 5.0
        c['LENGTH'] = np.round(np.concatenate([np.arange(0.6, 3.05, 0.05),
                                                [3.5, 4.0, 5.0, 6.0, 8.0, 10.0]]), 3)
        c['LENGTH_p'] = np.round(np.concatenate([np.arange(0.5, 3.05, 0.05),
                                                  [3.5, 4.0, 5.0, 6.0, 8.0, 10.0]]), 3)
        c['savefilen'] = f'tsmc18-nch_5-{corner}'
        c['savefilep'] = f'tsmc18-pch_5-{corner}'

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
        ('mn5:ids','A',        [1, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:vth','V',        [0, 1,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:igd','A',        [0, 0,1,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:igs','A',        [0, 0,0,1,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:gm', 'S',        [0, 0,0,0,1,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:gmbs','S',       [0, 0,0,0,0,1,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:gds','S',        [0, 0,0,0,0,0,1, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:cgg','F',        [0, 0,0,0,0,0,0, 1, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:cgs','F',        [0, 0,0,0,0,0,0, 0,-1, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:cgd','F',        [0, 0,0,0,0,0,0, 0, 0, 0,-1, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:cgb','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0,-1, 0, 0, 0,0,0,0]),
        ('mn5:cdd','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 1, 0, 0,0,0,0]),
        ('mn5:cdg','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0,-1, 0, 0, 0, 0,0,0,0]),
        ('mn5:css','F',        [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0,0,0,0]),
        ('mn5:csg','F',        [0, 0,0,0,0,0,0, 0, 0,-1, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mn5:fug','Hz',       [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 1,0,0,0]),
        ('mn5:gmoverid','V',   [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,1,0,0]),
        ('mn5:self_gain','rall',[0,0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,1,0]),
        ('mn5:vdsat','V',      [0, 0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,1]),
    ]

    c['p'] = [
        ('mp5:ids','A',        [-1,0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:vth','V',        [0,-1, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:igd','A',        [0, 0,-1, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:igs','A',        [0, 0, 0,-1,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:gm', 'S',        [0, 0, 0, 0,1,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:gmbs','S',       [0, 0, 0, 0,0,1,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:gds','S',        [0, 0, 0, 0,0,0,1, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:cgg','F',        [0, 0, 0, 0,0,0,0, 1, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:cgs','F',        [0, 0, 0, 0,0,0,0, 0,-1, 0, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:cgd','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0,-1, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:cgb','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0,-1, 0, 0, 0,0,0,0]),
        ('mp5:cdd','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 1, 0, 0,0,0,0]),
        ('mp5:cdg','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0,-1, 0, 0, 0, 0,0,0,0]),
        ('mp5:css','F',        [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0,0,0,0]),
        ('mp5:csg','F',        [0, 0, 0, 0,0,0,0, 0, 0,-1, 0, 0, 0, 0, 0, 0,0,0,0]),
        ('mp5:fug','Hz',       [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 1,0,0,0]),
        ('mp5:gmoverid','V',   [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,1,0,0]),
        ('mp5:self_gain','rall',[0,0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,1,0]),
        ('mp5:vdsat','V',      [0, 0, 0, 0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,1]),
    ]

    c['outvars_noise'] = ['STH', 'SFL']
    c['n_noise'] = [('mn5:id',''), ('mn5:fn','')]
    c['p_noise'] = [('mp5:id',''), ('mp5:fn','')]

    c['_netlist_tmpl'] = (
        f'//techsweep_tsmc18_5v_{corner}.scs' '\n'
        'include  %s\n'
        f'include "{c["paramfile"]}"' '\n'
        'save mn5:ids mn5:vth mn5:igd mn5:igs mn5:gm mn5:gmbs mn5:gds '
        'mn5:cgg mn5:cgs mn5:cgd mn5:cgb mn5:cdd mn5:cdg mn5:css mn5:csg mn5:cjd mn5:cjs '
        'mn5:fug mn5:gmoverid mn5:self_gain mn5:vdsat\n'
        'save mp5:ids mp5:vth mp5:igd mp5:igs mp5:gm mp5:gmbs mp5:gds '
        'mp5:cgg mp5:cgs mp5:cgd mp5:cgb mp5:cdd mp5:cdg mp5:css mp5:csg mp5:cjd mp5:cjs '
        'mp5:fug mp5:gmoverid mp5:self_gain mp5:vdsat\n'
        'parameters gs=0 ds=0\n'
        'vnoi     (vx  0)         vsource dc=0\n'
        'vdsn     (vdn vx)        vsource dc=ds\n'
        'vgsn     (vgn 0)         vsource dc=gs\n'
        'vbsn     (vbn 0)         vsource dc=-sb\n'
        'vdsp     (vdp vx)        vsource dc=-ds\n'
        'vgsp     (vgp 0)         vsource dc=-gs\n'
        'vbsp     (vbp 0)         vsource dc=sb\n'
        '\n'
        'mn5      (vdn vgn 0 vbn) %s  l=nlength*1e-6 w=%de-6 m=%d\n'
        'mp5      (vdp vgp 0 vbp) %s  l=plength*1e-6 w=%de-6 m=%d\n'
        '\n'
        'simOptions options gmin=1e-13 reltol=1e-4 vabstol=1e-6 iabstol=1e-10 '
        'temp=%d tnom=27 rawfmt=psfascii rawfile="%s"\n'
        'sweepvds sweep param=ds start=0 stop=%.10g step=%.10g {\n'
        '   sweepvgs dc param=gs start=0 stop=%.10g step=%.10g\n'
        '}\n'
        'sweepvds_noise sweep param=ds start=0 stop=%.10g step=%.10g {\n'
        '   sweepvgs_noise noise freq=1 oprobe=vnoi param=gs start=0 stop=%.10g step=%.10g\n'
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
    netlist_file = f'techsweep_tsmc18_5v_{c["corner"]}.scs'
    with open(netlist_file, 'w') as fid:
        fid.write(netlist)
    return netlist_file
