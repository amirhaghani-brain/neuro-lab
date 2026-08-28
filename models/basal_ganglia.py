#!/usr/bin/env python3
"""Nengo Cognitive Architecture & Neural Representation Template."""

import nengo
import numpy as np
import matplotlib.pyplot as plt

# Create the top-level Nengo Model
model = nengo.Network(label="2D Representation & Transformation")

with model:
    # 1. Input Stimulus: Sinusoidal wave input
    stimulus = nengo.Node(lambda t: [np.sin(t * 2 * np.pi * 0.5), np.cos(t * 2 * np.pi * 0.5)])

    # 2. Ensembles: Populations of spiking neurons representing 2D vectors
    ensemble_a = nengo.Ensemble(n_neurons=200, dimensions=2, radius=1.5, label="Ensemble_A")
    ensemble_b = nengo.Ensemble(n_neurons=200, dimensions=2, radius=1.5, label="Ensemble_B")

    # 3. Connections: Pass vector and apply non-linear transformation
    nengo.Connection(stimulus, ensemble_a)
    # Compute element-wise square: f(x, y) = [x^2, y^2]
    nengo.Connection(ensemble_a, ensemble_b, function=lambda x: [x[0]**2, x[1]**2])

    # 4. Probes: Record representations and spikes
    p_stim = nengo.Probe(stimulus)
    p_a = nengo.Probe(ensemble_a, synapse=0.01)
    p_b = nengo.Probe(ensemble_b, synapse=0.01)
    p_spikes = nengo.Probe(ensemble_a.neurons)

# Run with Nengo Simulator if executed directly in terminal
if __name__ == "__main__":
    with nengo.Simulator(model) as sim:
        sim.run(3.0)

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(sim.trange(), sim.data[p_stim], '--', label=['Input X', 'Input Y'])
    plt.plot(sim.trange(), sim.data[p_a], label=['Decoded A[0]', 'Decoded A[1]'])
    plt.title("Nengo: Input vs Decoded Ensemble Representation")
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(sim.trange(), sim.data[p_b], label=['Decoded B[0] ($X^2$)', 'Decoded B[1] ($Y^2$)'])
    plt.title("Non-linear Transformation: $f(x, y) = [x^2, y^2]$")
    plt.xlabel("Time (s)")
    plt.legend()

    plt.tight_layout()
    plt.show()
