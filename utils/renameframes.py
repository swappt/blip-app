from os import rename as R,listdir as L
from math import ceil as C,log10 as G
p=input('Enter the path of the files > ')+'/'
F=L(p)
l=C(G(len(F)))

for f in F:
  i=''
  ext='.'+f.split('.')[-1]
  appending_break = False
  appending = True
  for c in f:
    try:
      int(c)
      appending_break = True
      if appending:
        i += c
    except:
      if appending_break:
        appending = False
  n=''.join(['0' for j in range(l-len(c))])+i
  R(p+f,p+n+ext)
