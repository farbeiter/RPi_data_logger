
import sys
import fifo

from collections import deque

d = deque([], maxlen=5)
l = []
for i in range(10) :
    d.appendleft(i)
    l.append(i)
    print("#", i)
    print(d)
    print(l)

e = deque(d, maxlen=3)

print( e)

#quit()

print("hello")
f = fifo.dFifo(3)
print(f.all())
for i in range(10) :
    f.put(float(i))
    print(f.all())
    print(f.num(), f.sum(), f.avr())
print("redim")
f.dim(10)
print(f.all())
print("###")
for i in range(10) :
    f.put(float(i))
    print(f.all())
    print(f.num(), f.sum(), f.avr())
print("redim")
f.dim(5)
print(f.all())
print("###")
for i in range(10) :
    f.put(float(i))
    print(f.all())
    print(f.num(), f.sum(), f.avr())
