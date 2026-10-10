"""Per-character numbers for tripo_char.build(). Raw heights are in the Tripo model after orienting
(feet on Z0), read from <char>_tripo/_work/_probe.log and _diag.log."""
TRIPO = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/'
ASSETS = 'E:/game-dev-team/assets/'

CFG = {
    'trader': dict(
        id='trader', glb=TRIPO + 'trader/trader.glb', outdir=ASSETS + 'trader_tripo/', prefix='SK_Trader_',
        tex='T_TraderTripo_D.png', mat='M_TraderTripo', target_tris=1130, thick_torso=1.18, yaw=-90.0,
        neck_z=1.475, head_z=1.520, sh_x=0.22,          # chin line at 1.52 (probe: skin neck 1.48..1.51, beard from 1.52)
        hem_raw=0.91,                                   # sweater hem: trousers up to 0.90, dark sweater from 0.92
        collar=dict(pred=lambda c: c[0] - c[2] < 0.085, raw_cap=1.575),    # grey vest / dark sweater, not the stubble; bandana from 1.58
        neck_fit=True, nape_fill=True, skin_at=(0.0, -0.09, 1.52),
        planes=(0.900, 0.910, 1.532, 1.549)),
    'bandit': dict(
        id='bandit', glb=TRIPO + 'bandit/bandit.glb', outdir=ASSETS + 'bandit_tripo/', prefix='SK_Bandit_',
        tex='T_BanditTripo_D.png', mat='M_BanditTripo', target_tris=1130, thick_torso=1.18, yaw=-90.0,
        neck_z=1.535, head_z=1.580, sh_x=0.22,          # chin at 1.58 (probe: skin neck 1.51..1.57 in front)
        hem_raw=1.01,                                   # jacket bottom: light trousers up to 1.00, black leather from 1.02
        collar=dict(pred=lambda c: c[0] - c[2] < 0.085, raw_cap=1.615),    # black leather, not the hair; collar back reaches 1.61
        neck_fit=True, nape_fill=True, skin_at=(0.0, -0.09, 1.52),
        ears=dict(z=(1.60, 1.731), y=(-0.02, 0.10), x=0.082, keep=0.35),    # source ears reach |x| 0.114, head 0.075
        planes=(0.900, 0.910, 1.532, 1.549)),
    'elder': dict(
        id='elder', glb=TRIPO + 'elder/elder.glb', outdir=ASSETS + 'elder_tripo/', prefix='SK_Elder_',
        tex='T_ElderTripo_D.png', mat='M_ElderTripo', target_tris=950, thick_torso=1.10, yaw=-90.0,
        neck_z=1.515, head_z=1.560, sh_x=0.22,          # chin under the beard ~1.56; coat collar reaches 1.61
        coat=dict(hem_raw=0.75, skirt_full=0.76, skirt_top=0.84, heat_from=0.90, heat_full=0.96, trouser_at=(0.14, -0.10, 0.55)),   # hip joints at 0.837
        neck_fit=False, nape_fill=False,
        planes=(0.84, 0.90, 1.532, 1.549)),            # 0.84 / 0.90: loops on the coat where its weights change (hip joints, pelvis)
    'scientist': dict(
        id='scientist', glb=TRIPO + 'scientist/scientist.glb', outdir=ASSETS + 'scientist_tripo/', prefix='SK_Scientist_',
        tex='T_ScientistTripo_D.png', mat='M_ScientistTripo', target_tris=950, thick_torso=1.10, yaw=-90.0,
        neck_z=1.535, head_z=1.580, sh_x=0.22,          # chin at 1.58 (probe: turtleneck up to 1.56, skin from 1.58)
        coat=dict(hem_raw=0.60, skirt_full=0.76, skirt_top=0.84, heat_from=0.90, heat_full=0.96, trouser_at=(0.12, -0.03, 0.40)),   # lab coat down to raw z 0.60
        collar=dict(pred=lambda c: c[0] - c[2] < 0.085, raw_cap=1.625),    # turtleneck and coat collar (white / dark grey), not the brown hair; coat collar back reaches 1.62
        neck_fit=True, nape_fill=True, skin_at=(0.0, -0.09, 1.52),         # the neck line has to take both his own head and the hero head in the cap
        planes=(0.84, 0.90, 1.532, 1.549)),
}
