#!/usr/bin/env python3
"""NEURON Biophysical Soma Simulation Template."""

from neuron import h, gui
import matplotlib.pyplot as plt

# --- 1. Morphology & Biophysics ---
soma = h.Section(name='soma')
soma.L = 20.0       # Length in micrometers
soma.diam = 20.0    # Diameter in micrometers

# Insert standard Hodgkin-Huxley ionic mechanisms
soma.insert('hh')
soma.gnabar_hh = 0.12   # Sodium conductance (S/cm2)
soma.gkbar_hh = 0.036   # Potassium conductance (S/cm2)
soma.gl_hh = 0.0003     # Leak conductance (S/cm2)
soma.el_hh = -54.3      # Leak reversal potential (mV)

# --- 2. Stimulation (Current Clamp) ---
stim = h.IClamp(soma(0.5))
stim.delay = 10.0   # Stimulation start delay (ms)
stim.dur = 40.0     # Pulse duration (ms)
stim.amp = 0.5      # Amplitude (nA)

# --- 3. Instrumentation & Recording ---
time_vec = h.Vector().record(h._ref_t)
v_vec = h.Vector().record(soma(0.5)._ref_v)

# --- 4. Simulation Control ---
h.finitialize(-65.0) # Initial resting voltage (mV)
h.continuerun(70.0)  # Run simulation to t = 70 ms

print(f"NEURON simulation finished. Recorded {len(time_vec)} time points.")

# --- 5. Visualization ---
plt.figure(figsize=(10, 4))
plt.plot(time_vec, v_vec, color='#1f77b4', lw=2, label='Soma $V_m$')
plt.axvspan(stim.delay, stim.delay + stim.dur, color='gold', alpha=0.2, label='Current Clamp Active')
plt.xlabel('Time (ms)')
plt.ylabel('Membrane Potential (mV)')
plt.title('NEURON: Hodgkin-Huxley Action Potential Response')
plt.legend()
plt.tight_layout()
plt.show()
