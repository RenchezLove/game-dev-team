import sys, os
sys.path.insert(0, sys.argv[1] + "/pylib")
from PIL import Image
import numpy as np
from collections import deque
out = sys.argv[1] + "/icons_out"
D = "C:/Users/pgr40/Desktop/GamdevAITeam/Иконки предметов инвентаря/"
sheets = [
 (D+"Иконки предметов инвентаря 1/ChatGPT Image 24 сент. 2026 г., 22_34_28.png",
  ["T_Item_Pistol","T_Item_Ammo9mm","T_Item_Knife","T_Item_CannedFood","T_Item_Water","T_Item_Medkit","T_Item_WolfHide","T_Item_Laptop","T_Item_Money"]),
 (D+"Иконки предметов инвентаря 2/ChatGPT Image 24 сент. 2026 г., 22_36_58.png",
  ["T_Item_Armor_T1_Head","T_Item_Armor_T1_Torso","T_Item_Armor_T1_Legs","T_Item_Armor_T2_Head","T_Item_Armor_T2_Torso","T_Item_Armor_T2_Legs","T_Item_Armor_T3_Head","T_Item_Armor_T3_Torso","T_Item_Armor_T3_Legs"]),
]
B=4
for path, names in sheets:
    im = Image.open(path).convert("RGBA"); a = np.array(im)
    H,W = a.shape[:2]
    print(path[-30:], "corner alpha", a[0,0,3], a[H-1,W-1,3], "min/max alpha", a[...,3].min(), a[...,3].max())
    m = a[...,3] > 16
    gh, gw = H//B, W//B
    g = m[:gh*B,:gw*B].reshape(gh,B,gw,B).any(axis=(1,3))
    lab = np.zeros(g.shape, int); n=0; comps=[]
    for y in range(gh):
        for x in range(gw):
            if g[y,x] and not lab[y,x]:
                n+=1; q=deque([(y,x)]); lab[y,x]=n; ys=[];xs=[]
                while q:
                    cy,cx=q.popleft(); ys.append(cy); xs.append(cx)
                    for dy in (-1,0,1):
                        for dx in (-1,0,1):
                            ny,nx=cy+dy,cx+dx
                            if 0<=ny<gh and 0<=nx<gw and g[ny,nx] and not lab[ny,nx]:
                                lab[ny,nx]=n; q.append((ny,nx))
                comps.append((len(ys),min(ys)*B,min(xs)*B,(max(ys)+1)*B,(max(xs)+1)*B,n))
    comps.sort(reverse=True)
    if len(comps)==8:
        c=[c for c in comps if c[3]-c[1]>700][0]; comps.remove(c); idn=c[5]; n+=1
        yy=np.arange(gh)[:,None]*B; sel=(lab==idn)&(yy>=824); lab[sel]=n
        for cid in (idn,n):
            ys,xs=np.nonzero(lab==cid); comps.append((len(ys),ys.min()*B,xs.min()*B,(ys.max()+1)*B,(xs.max()+1)*B,cid))
        comps.sort(reverse=True)
    print(" components:", len(comps), "sizes:", [c[0] for c in comps[:12]])
    big = comps[:9]
    big.sort(key=lambda c: ((c[1]+c[3])//2)//(H//3)*10 + ((c[2]+c[4])//2)//(W//3))
    for c,name in zip(big,names):
        _,y0,x0,y1,x1,idn = c
        keep = np.kron(lab==idn, np.ones((B,B),bool))
        sub = a[y0:y1,x0:x1].copy()
        k = keep[y0:y1,x0:x1]; sub[...,3] = np.where(k, sub[...,3], 0)
        h,w = sub.shape[:2]; s = int(max(h,w)*1.08)
        canvas = Image.new("RGBA",(s,s),(0,0,0,0))
        canvas.paste(Image.fromarray(sub),((s-w)//2,(s-h)//2))
        canvas.resize((256,256),Image.LANCZOS).save(f"{out}/{name}.png")
        print("  ",name,(x0,y0,x1,y1))
