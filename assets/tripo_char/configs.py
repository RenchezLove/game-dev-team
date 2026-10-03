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
    'elder': dict(
        id='elder', glb=TRIPO + 'elder/elder.glb', outdir=ASSETS + 'elder_tripo/', prefix='SK_Elder_',
        tex='T_ElderTripo_D.png', mat='M_ElderTripo', target_tris=1060, thick_torso=1.10, yaw=-90.0,
        neck_z=1.515, head_z=1.560, sh_x=0.22,          # chin under the beard ~1.56; coat collar reaches 1.61
        coat=dict(hem_raw=0.75, skirt_top=0.92, skirt_full=0.80, trouser_at=(0.14, -0.10, 0.55)),
        neck_fit=False, nape_fill=False,
        planes=(1.532, 1.549)),
}
