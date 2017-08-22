from random import choice as h;r=round;g=range;a=int(input('How many spikes need positioning? > '));A=[r(i*0.05,2) for i in g(1,20)];B=[r(i*0.05,2) for i in g(4,20)];c=[]
for _ in g(a):d=[];d.append(h(A));d.append(h(B));c.append(d)
open('spikes','w').write(str(c))
