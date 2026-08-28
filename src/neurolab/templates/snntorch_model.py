#!/usr/bin/env python3
"""snnTorch Spiking Neural Network (SNN) Classification Model Template."""

import torch
import torch.nn as nn
import snntorch as snn
from snntorch import surrogate

# Device configuration (CUDA GPU / CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- Define SNN Architecture ---
class SpikingNet(nn.Module):
    def __init__(self, num_inputs=10, num_hidden=64, num_outputs=2, beta=0.95):
        super().__init__()
        self.beta = beta
        spike_grad = surrogate.fast_sigmoid(slope=25)

        # Layer 1: Linear -> Leaky Integrate-and-Fire
        self.fc1 = nn.Linear(num_inputs, num_hidden)
        self.lif1 = snn.Leaky(beta=self.beta, spike_grad=spike_grad)

        # Layer 2: Linear -> Leaky Integrate-and-Fire
        self.fc2 = nn.Linear(num_hidden, num_outputs)
        self.lif2 = snn.Leaky(beta=self.beta, spike_grad=spike_grad)

    def forward(self, x, num_steps=25):
        # Initialize membrane potentials
        mem1 = self.lif1.init_leaky()
        mem2 = self.lif2.init_leaky()

        spk2_rec = []
        mem2_rec = []

        # Loop over simulation timesteps (BPTT)
        for step in range(num_steps):
            cur1 = self.fc1(x)
            spk1, mem1 = self.lif1(cur1, mem1)

            cur2 = self.fc2(spk1)
            spk2, mem2 = self.lif2(cur2, mem2)

            spk2_rec.append(spk2)
            mem2_rec.append(mem2)

        return torch.stack(spk2_rec, dim=0), torch.stack(mem2_rec, dim=0)

if __name__ == "__main__":
    print(f"snnTorch model running on: {device}")
    model = SpikingNet().to(device)

    # Test forward pass with dummy batch
    batch_size = 4
    dummy_input = torch.randn(batch_size, 10).to(device)

    spikes, membrane = model(dummy_input, num_steps=30)
    print(f"Output Spikes shape [steps, batch, classes]: {spikes.shape}")
    print(f"Output Membrane shape [steps, batch, classes]: {membrane.shape}")
    print("snnTorch template initialized successfully.")
