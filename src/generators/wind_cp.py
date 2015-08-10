from __future__ import division
from math import log, pi, sqrt
import itertools

ws_maxcp = 7
cut_in_ws = 2.5
cut_out_ws = 25
ws_rated = 17
cp_max = 0.302
cp_rated = cp_max - 0.05

turbine_height = 7
roughness_l = 0.055
diameter = 7
ref_height = 10

def seq(start, end, step):
    """
    Purpose : support for float step in a range-like function
    """
    assert(step != 0)
    sample_count = abs(end - start) / step
    return itertools.islice(itertools.count(start, step), sample_count)

def cal_coefficiency(wsadj):    
    # wsadj = ws * log(turbine_height/roughness_l)/log(ref_height/roughness_l); 
    cp = 0    
    if wsadj <= cut_in_ws :
        cp = 0
    elif wsadj > cut_out_ws:
        cp = 0
    elif  wsadj > ws_rated:
        cp = cp_rated * pow(ws_rated,3) / pow(wsadj,3)
    else:
        m00 = pow((ws_maxcp/cut_in_ws - 1), 2)
        m01 = pow((ws_maxcp/cut_in_ws - 1), 3)
        m02 = 1
        m10 = pow((ws_maxcp / ws_rated - 1), 2)
        m11 = pow((ws_maxcp / ws_rated - 1), 3)
        m12 = 1 - cp_rated / cp_max
        detcp = m00 * m11 - m01*m10
        F = (m02 * m11 - m01 * m12) / detcp
        G = (m00 * m12 - m02 * m10) / detcp
        cp = cp_max * (1 - F * pow((ws_maxcp / wsadj - 1), 2) - G * pow((ws_maxcp / wsadj - 1), 3))
    return cp

def cal_available_power(diameter, ws):
    cp = cal_coefficiency(ws)
    avai_pow = 1/2 * pow(ws, 3) * 1.225 * pi * pow(diameter / 2 , 2)
    return avai_pow * cp / 10

powers = []
cps = []

for i in list(seq(0, 21, 0.1)):
    cps.append(cal_coefficiency(i))

for i in list(seq(0, 21, 0.1)):
    powers.append(cal_available_power(diameter, i))
    
import matplotlib.pylab as plt
fig, ax = plt.subplots(1,2)
ax[0].plot(list(seq(0, 21, 0.1)), powers)
ax[0].grid(True)
ax[0].set_title('Simulated Power Curve')
ax[0].set_ylabel('power(Kw)')
ax[0].set_ylim([0, 2500])

ax[1].plot(list(seq(0, 21, 0.1)), cps)
ax[1].grid(True)
ax[1].set_title('Simulated Efficient Curve')
ax[1].set_ylabel('power efficient')

# minor = []
# for i in range(0, 11):
#     minor.append(i * 200)    
# ax[0].set_yticks(minor)
# ax[0].set_ylim([0, 10000])

plt.show()
