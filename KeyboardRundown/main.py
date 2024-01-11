import matplotlib.pyplot as plt
import matplotlib.animation as animation
from os import startfile
from PIL import Image, ImageFont, ImageDraw
import scipy
import numpy as np
import math
import imagegen
import time
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent


#---------------------------
dataname= "log1_V2.0.txt"

filename = "test2.mp4"

framerate = 60
length = 10

qwertyline = 5060837.822014924




dpi = 300

xfactor = 1/60
yfactor = 1/1000000


xlabel_ = "t in minutes"
ylabel_ = "Score in Mio"


smooth = True
fixatzero = False

showkeyboard = True
show = True
#----------------------------

datastr = root_dir / "BestKeyboardLayout" / "logs" / dataname

#time estimate
with open("timeestimates.txt", "r") as d1:
    lines = d1.readlines()
    tt = 0
    for line in lines:
        tt += float(line)
    tt = tt/len(lines)

t = framerate*length*tt # tt ~ 0.3566666666666667
print(f"estimated time: {int(t/60)}:{int(t)%60}")

fig, ax = plt.subplots(2, 1)
data = []

if filename == "default" or filename == "" or filename is None: filename = dataname # default filename
with open(datastr, "r") as file:
    for line in file.read().split("\n"):
        if "---------------------" in line: break
        line = line.split("; ")
        data.append({"time": float(line[1])*xfactor, "score": float(line[2])*yfactor, "keyboard": eval(line[3])})



fulltime = data[len(data) - 1]["time"]
stepsize = fulltime/(length*framerate)


x = []
y = []
graph = ax[0].plot(data[0]["time"], data[0]["score"], c="b")[0]
if qwertyline >= 0: reference = ax[0].hlines(qwertyline*yfactor, xmin= 0, xmax=data[len(data)-1]["time"]*2, linestyles="--", colors="grey")
yl = [0, data[0]["score"]*1.1]
ax[0].set(xlim=[0, data[0]["time"]*1.2], ylim=yl, ylabel= ylabel_, xlabel= xlabel_)
plt.ticklabel_format(style='plain', useOffset=False, axis='y')
if showkeyboard: plt.subplots_adjust(hspace=0.5)


if fixatzero:
    nn = 0
    while stepsize > data[nn]["time"]:
        nn += 1
    FIRSTTIME = data[nn]["time"]
else: FIRSTTIME = 0
def anim(frame):
    frame += 1
    t = frame*stepsize
    print(f"{frame}/{length*framerate}")

    while t > data[0]["time"]:
        data.pop(0)

    if smooth:
        if len(x) != 0 and data[0]["score"] == y[len(y)-1]: x.pop(len(x)-1); y.pop(len(y)-1)

    x.append(t-FIRSTTIME)
    y.append(data[0]["score"])

    graph.set_xdata(x)
    graph.set_ydata(y)

    if t != 0: ax[0].set(xlim=[0, t*1.2], ylim=yl)

    if showkeyboard:
        # imagegen.generatekeyboard(data[0]["keyboard"]).save("C:\\Users\\max.stephan\\Desktop\\Projects\\KeyboardRundown\\modifiedkeyboard.png")
        # pic = plt.imread("C:\\Users\\max.stephan\\Desktop\\Projects\\KeyboardRundown\\modifiedkeyboard.png")
        pic = np.asarray(imagegen.generatekeyboard(data[0]["keyboard"]))
        ax[1].clear()
        ax[1].imshow(pic)
        ax[1].axis("off")

    return ax






fr = length*framerate
t1 = time.time()
ani = animation.FuncAnimation(fig=fig, func=anim, frames=fr, interval=stepsize, repeat=False)
ani.save(filename, fps= framerate, dpi=dpi)
totaltime = time.time() - t1
print(totaltime)
with open("timeestimates.txt", "a") as d2:
    d2.write("\n" + str(totaltime/fr))

if show: startfile(filename)


# #computing theoretical limit:
# X = np.array(x)
# Y = np.array(y)
#
# vals = scipy.optimize.curve_fit(lambda t, a, b, c: a + b*np.exp(c * t), X, Y, p0= (1, 0.95, -0.1))
# a_, b_, c_ = vals[0]
# print(f"{a_}  +  {b_} * e^({c_}*x)")
#
# f = lambda xx : a_ + b_*np.exp(c_ * xx)
#
# _x = np.linspace(0, fulltime, fr)
# _y = f(_x)
#
# plt.plot(_x, _y, c="red")
# plt.show()





