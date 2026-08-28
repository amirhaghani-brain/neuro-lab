#!/usr/bin/env python3
"""Neo & Elephant Electrophysiology Data Analysis Template."""

import numpy as np
import quantities as pq
import neo
import elephant
import elephant.statistics as estats
import matplotlib.pyplot as plt

# 1. Generate Synthetic Spike Train (or load via neo.io)
# Example loading:
# reader = neo.io.AxonIO(filename="data/recording.abf")
# block = reader.read_block()

np.random.seed(42)
spike_times = np.sort(np.random.exponential(scale=20.0, size=150).cumsum())
spike_times = spike_times[spike_times < 1000.0]

# Construct Neo SpikeTrain object
spiketrain = neo.SpikeTrain(
    spike_times * pq.ms,
    t_start=0.0 * pq.ms,
    t_stop=1000.0 * pq.ms
)

# 2. Compute Electrophysiology Metrics with Elephant
mean_rate = estats.mean_firing_rate(spiketrain)
isis = estats.isi(spiketrain)
cv = estats.cv(isis)
fanofactor = estats.fanofactor([spiketrain])

print("--- Electrophysiology Analysis Summary ---")
print(f"Mean Firing Rate: {mean_rate:.2f}")
print(f"Coefficient of Variation (CV): {cv:.3f}")
print(f"Fano Factor: {fanofactor:.3f}")
print(f"Total Spikes: {len(spiketrain)}")

# 3. Visualization: Spike Raster & ISI Distribution
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6))

# Raster Plot
ax1.eventplot(spiketrain.times.rescale(pq.ms).magnitude, lineoffsets=1, linelengths=0.8, color='crimson')
ax1.set_xlim(0, 1000)
ax1.set_xlabel('Time (ms)')
ax1.set_yticks([])
ax1.set_title(f'Spike Train Raster (Rate: {mean_rate:.1f})')

# ISI Histogram
ax2.hist(isis.rescale(pq.ms).magnitude, bins=25, color='teal', edgecolor='black', alpha=0.7)
ax2.set_xlabel('Inter-Spike Interval (ms)')
ax2.set_ylabel('Count')
ax2.set_title(f'ISI Distribution (CV = {cv:.2f})')

plt.tight_layout()
plt.show()
