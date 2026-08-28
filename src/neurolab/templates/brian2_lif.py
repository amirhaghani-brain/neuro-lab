#!/usr/bin/env python3
"""Brian 2 Leaky Integrate-and-Fire (LIF) Network Simulation Template."""

from brian2 import *
import matplotlib.pyplot as plt

# Start with a fresh brian environment
start_scope()
prefs.codegen.target = 'numpy'

# --- Simulation Parameters ---
duration = 500 * ms
num_neurons = 100

# --- Biophysical Constants ---
tau_m = 10 * ms
v_rest = -70 * mV
v_reset = -65 * mV
v_th = -50 * mV
R = 10 * Mohm

# --- Differential Equations ---
eqs = '''
dv/dt = (-(v - v_rest) + R * I) / tau_m : volt (unless refractory)
I : amp
'''

# --- Create Neuron Group ---
neurons = NeuronGroup(
    num_neurons,
    eqs,
    threshold='v > v_th',
    reset='v = v_reset',
    refractory=2 * ms,
    method='euler'
)

# Initialize membrane voltage and stochastic input currents
neurons.v = v_rest + rand(num_neurons) * (v_th - v_rest)
neurons.I = '(1.5 + 1.0 * rand()) * nA'

# --- Monitors ---
spike_mon = SpikeMonitor(neurons)
state_mon = StateMonitor(neurons, 'v', record=[0, 1, 2])

# --- Run Simulation ---
print(f"Running Brian 2 simulation for {duration}...")
run(duration)
print(f"Simulation completed. Total spikes fired: {spike_mon.num_spikes}")

# --- Plotting Results ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

# Raster plot
ax1.plot(spike_mon.t / ms, spike_mon.i, '.k', markersize=3)
ax1.set_ylabel('Neuron Index')
ax1.set_title('Spike Raster Plot')

# Voltage traces for selected neurons
for idx in [0, 1, 2]:
    ax2.plot(state_mon.t / ms, state_mon.v[idx] / mV, label=f'Neuron {idx}')
ax2.axhline(v_th / mV, color='r', linestyle='--', label='Threshold')
ax2.set_xlabel('Time (ms)')
ax2.set_ylabel('Membrane Potential (mV)')
ax2.set_title('Membrane Voltage Traces')
ax2.legend(loc='upper right')

plt.tight_layout()
plt.show()
