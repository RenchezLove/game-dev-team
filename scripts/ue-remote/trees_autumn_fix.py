import unreal
mel=unreal.MaterialEditingLibrary; eal=unreal.EditorAssetLibrary
mat=unreal.load_asset('/Game/Materials/M_TreeAutumn')
out=mel.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR); print('OUT',out.get_class().get_name())
pw,a2,al2=mel.get_inputs_for_material_expression(mat,out)
print('PW',pw.get_class().get_name(),'exp',pw.get_editor_property('const_exponent'),[i.get_class().get_name() if i else None for i in mel.get_inputs_for_material_expression(mat,pw)])
vc=mel.get_inputs_for_material_expression(mat,pw)[0]
al1=mel.get_inputs_for_material_expression(mat,al2)[0]; print('AL1',al1.get_class().get_name(),[i.get_class().get_name() for i in mel.get_inputs_for_material_expression(mat,al1)])
E=lambda c,x,y: mel.create_material_expression(mat,c,x,y); C=mel.connect_material_expressions
def K(v,y):
    n=E(unreal.MaterialExpressionConstant,-1300,y); n.set_editor_property('r',v); return n
def M(ch,y):
    n=E(unreal.MaterialExpressionComponentMask,-1150,y)
    for k in 'rgba': n.set_editor_property(k,k==ch)
    return n
r_=M('r',-400); g_=M('g',-340); b_=M('b',-280)
mx=E(unreal.MaterialExpressionMax,-1000,-380); ad=E(unreal.MaterialExpressionAdd,-880,-380); dv=E(unreal.MaterialExpressionDivide,-760,-360)
sb=E(unreal.MaterialExpressionSubtract,-640,-360); ml=E(unreal.MaterialExpressionMultiply,-520,-360); st=E(unreal.MaterialExpressionSaturate,-400,-360)
eps=K(0.001,-460); thr=K(1.5,-200); k4=K(4.0,-140)
ok=[C(vc,'',r_,''),C(vc,'',g_,''),C(vc,'',b_,''),C(r_,'',mx,'A'),C(b_,'',mx,'B'),C(mx,'',ad,'A'),C(eps,'',ad,'B'),C(g_,'',dv,'A'),C(ad,'',dv,'B'),C(dv,'',sb,'A'),C(thr,'',sb,'B'),C(sb,'',ml,'A'),C(k4,'',ml,'B'),C(ml,'',st,''),C(st,'',al1,'A')]
print('CONN all',all(ok),len(ok),[i for i,v in enumerate(ok) if not v])
print('AL1 now',[i.get_class().get_name() for i in mel.get_inputs_for_material_expression(mat,al1)])
mel.recompile_material(mat); s=mel.get_statistics(mat); print('STATS ps',s.num_pixel_shader_instructions,'save',eal.save_loaded_asset(mat,False))
