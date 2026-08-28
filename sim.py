#!/usr/bin/env python3
"""Terminal-native LIF Neuron Euler Simulator."""
import math

dt = 0.1       # ms
T = 60.0       # total ms
steps = int(T / dt)

# Biophysical Parameters
tau_m = 10.0   # ms
v_rest = -70.0 # mV
v_reset = -65.0# mV
v_th = -50.0   # mV
R = 1.0        # GOhm
I = 24.0       # pA (Injected Current)

v = v_rest
trace = []
spikes = []

for step in range(steps):
    t = step * dt
    # Euler Integration: dv/dt = -(v - v_rest)/tau_m + (I*R)/tau_m
    dv = (-(v - v_rest) + R * I) / tau_m * dt
    v += dv
    
    if v >= v_th:
        trace.append(20.0) # Spike apex
        spikes.append(t)
        v = v_reset
    else:
        trace.append(v)

print("\n\033[1;36m=== LIF NEURON TERMINAL VOLTAGE TRACE (0 to 60 ms) ===\033[0m")
rows = 10
v_min, v_max = -75.0, 25.0
sample_step = max(1, len(trace) // 55)
sampled = trace[::sample_step]

for r in range(rows, -1, -1):
    level = v_min + (v_max - v_min) * (r / rows)
    line = [f"{level:5.0f} mV |"]
    for val in sampled:
        if abs(val - level) < (v_max - v_min) / (rows * 1.8):
            line.append("\033[1;35m*\033[0m" if val > -40 else "\033[1;32m.\033[0m")
        else:
            line.append(" ")
    print("".join(line))

print("         +" + "-" * len(sampled))
print(f"Spikes fired: \033[1;33m{len(spikes)}\033[0m at times: {[round(s, 1) for s in spikes]} ms\n")
