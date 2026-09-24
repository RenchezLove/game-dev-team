import sys,os; sys.path.insert(0, sys.argv[1]+"/pylib")
from PIL import Image; import numpy as np; from collections import deque
d=sys.argv[1]+"/icons_out"
for f in sorted(os.listdir(d)):
    a=np.array(Image.open(d+"/"+f)); m=a[...,3]>8; H,W=m.shape
    lab=np.zeros(m.shape,int); n=0; sizes={}
    for y in range(H):
        for x in range(W):
            if m[y,x] and not lab[y,x]:
                n+=1; q=deque([(y,x)]); lab[y,x]=n; c=0
                while q:
                    cy,cx=q.popleft(); c+=1
                    for ny,nx in ((cy+1,cx),(cy-1,cx),(cy,cx+1),(cy,cx-1),(cy+1,cx+1),(cy-1,cx-1),(cy+1,cx-1),(cy-1,cx+1)):
                        if 0<=ny<H and 0<=nx<W and m[ny,nx] and not lab[ny,nx]: lab[ny,nx]=n; q.append((ny,nx))
                sizes[n]=c
    big=max(sizes,key=sizes.get); small=[s for k,s in sizes.items() if k!=big]
    keep=(lab==big)|(~m)
    for k,s in sizes.items():
        if k!=big and s>=0.02*sizes[big]: keep|=(lab==k)
    removed=int(((~keep)&m).sum()); a[...,3]=np.where(keep,a[...,3],0)
    Image.fromarray(a).save(d+"/"+f); print(f, "pieces", len(sizes), "removed px", removed)
