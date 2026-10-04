# 3 · Distributed training

**Verdict:** pretraining over the internet is *real* but runs about three orders of magnitude
behind the frontier. It works when each participant is a "fat node" (a multi-GPU server)
and the optimizer synchronises rarely. Training on a crowd of single consumer GPUs is blocked
less by compute than by **memory** and by the **bandwidth that model parallelism needs**.
Fine-tuning and RL post-training decentralise much more easily than pretraining.

## 3.1 The compute bill

Training a dense transformer costs ≈ **6 · N · D** FLOPs (N parameters, D tokens). From
`estimate.py training`:

| Model | Tokens | FLOPs | On RTX 4090s (25% eff.) | On H100s (40% eff.) |
|---|---|---|---|---|
| 8B | 15T | 7.2 × 10²³ | 4.9M GPU-h, 2.2 GWh | 0.5M GPU-h, 0.4 GWh |
| 70B | 15T | 6.4 × 10²⁴ | 42.8M GPU-h, 19.3 GWh | 4.5M GPU-h, 3.1 GWh |
| 405B | 15.6T | 3.8 × 10²⁵ | 255M GPU-h, 115 GWh | 26.6M GPU-h, 18.6 GWh |

(Sanity check: Meta reported ~6.4M H100-hours for Llama 3 70B, the same order as the 4.5M here.)

*If communication were free*, a 70B run needs ~4.9 years on 1,000 volunteer 4090s, ~178 days on
10,000, or ~18 days on 100,000. That is large but not absurd: BOINC-style volunteer projects
have mobilised hundreds of thousands of machines.

The more interesting near-term target is a **licence-clean model at Comma scale**. The Common Pile
team trained Comma v0.1 (7B, 2T tokens of openly licensed text, see
[02 / licensing](../02-ethical-llm/1-licensing-and-data-tiers.md)). That is 8.4 × 10²² FLOPs:
**~24 days on 1,000 consumer GPUs**, if the next two walls can be handled.

**Energy honesty:** the same FLOPs cost ~6× more electricity on consumer cards at volunteer-grade
efficiency than on data-center hardware. A decentralised model is not automatically a greener one.

## 3.2 Wall #1: memory

Mixed-precision Adam keeps ~**16 bytes per parameter**: bf16 weights and gradients plus fp32
master weights and two fp32 moments.

| Model | Training state | 24 GB cards just to *hold* it |
|---|---|---|
| 8B | 128 GB | 6 |
| 70B | 1.1 TB | 48 |
| 405B | 6.5 TB | 270 |

So no consumer GPU can hold a full replica, and plain data parallelism (every node holds the
whole model, nodes exchange gradients) is impossible for these sizes on consumer cards. The
datacenter answer is sharding (ZeRO-3 / FSDP), but that re-gathers the parameters over the
network in every forward and backward pass, which over the internet is hopeless.

Options:

- **Fat nodes.** Each participant is an 8×H100 or 8×4090 box, so the replica lives in local
  memory and only the replicas talk over the internet. This is what every successful
  decentralised pretraining run so far has done.
- **Leaner optimizers.** 8-bit Adam, Adafactor, Muon (one momentum buffer), and low-rank
  gradient projection (GaLore) cut state to ~6–10 bytes/param. That helps, but not by enough.
- **Model parallelism over the internet** (§3.5). Each volunteer holds a slice and activations
  flow between them.

## 3.3 Wall #2: gradient synchronisation

Naive synchronous data parallelism sends the full gradient every step. For 70B in bf16 that is
141 GB, and a ring all-reduce pushes ~282 GB through each node. At a 16M-token batch, 15T tokens is
~940k steps:

| Link | One sync | Sync every step | Every 500 steps, int8 | Every 500 steps, ~8× compressed |
|---|---|---|---|---|
| 1 Gb/s | 38 min | **67 years** | 24.5 days | 6.1 days |
| 100 Mb/s | 6.3 h | 672 years | 245 days | 61 days |

The last two columns are why the field moved. **Syncing rarely and compressing hard** turns an
impossible run into one where communication is a modest fraction of a months-long job, and
streaming variants hide even that behind compute.

## 3.4 The low-communication optimizer family

| Method | Idea | Reported reduction |
|---|---|---|
| **Local SGD / FedAvg** (McMahan et al., 2017) | Train locally, average weights periodically | The ancestor of all below |
| **DiLoCo** (Douillard et al., 2023) | Inner AdamW for H≈500 local steps; outer Nesterov step on the *pseudo-gradient* (start weights − end weights) | ~500× less communication at matched loss |
| **Streaming DiLoCo** (Douillard et al., 2025) | Sync parameter fragments on a staggered schedule, overlap with compute, quantise | Up to ~400× less bandwidth; comms hidden behind compute |
| **OpenDiLoCo → INTELLECT-1** (Prime Intellect, 2024) | Open DiLoCo with 100 inner steps; int8 pseudo-gradients; nodes join and leave mid-run | ~400× (100 steps × 4× quantisation). 10B params, 1T tokens, up to 14 concurrent nodes on 3 continents, 30 contributors |
| **DisTrO / DeMo** (Peng, Kingma et al., Nous Research, 2024) | Decouple momentum; DCT + top-k so only the fast-moving components are sent | Up to ~85× less data per GPU (paper, 300M–1B models); powers the **Psyche** network and the **Consilience 40B** run (2025) |
| **PowerSGD, top-k + error feedback, 1-bit Adam** | Low-rank, sparse or quantised gradients | 10–100×, composable with the above |
| **Moshpit SGD** (Ryabinin et al., 2021) | Average in small rotating groups instead of a global all-reduce | Tolerates churn and failures |

An observation worth keeping: DiLoCo replicas are **short-lived experiments that get merged**.
That shape matches volunteers who come and go far better than lockstep synchronous training does.

## 3.5 Model parallelism over the internet: SWARM and the square-cube law

If no node can hold the model, split it by layers (pipeline parallelism) and stream activations
between volunteers. **SWARM parallelism** (Ryabinin et al., 2023) makes this fault-tolerant with
randomised, rebalancing pipelines, and makes a key observation, the **square-cube law**: a
layer's compute grows with d² per token, while the activation it hands onward grows only with d.
Wider models do more work per byte sent (`estimate.py pipeline`):

| Model | Params / layer | FLOPs per byte sent | Stage on 24 GB cards | Needed each way | vs 20 Mb/s upload |
|---|---|---|---|---|---|
| 8B | 218M | 79,872 | 4 layers / 1 GPU | 1.0 Gb/s | 52× short |
| 70B | 856M | 156,781 | 1 layer / 1 GPU | 2.1 Gb/s | 105× short |
| 405B | 3,181M | 291,223 | 1 layer / 4 GPUs | 4.5 Gb/s | 227× short |

The law holds (FLOPs per byte roughly doubles with each step up in width), but a consumer card
is memory-capped at about 1B trainable parameters, so **per-GPU traffic stays at 1–2 Gb/s whatever
the model**. The square-cube benefit only pays off for nodes fat enough to hold whole wide layers.
The remaining 50–200× gap is the target for **activation compression**. Pluralis Research's
"Protocol Models" work (2025) reports compressing pipeline activations and their gradients by
roughly two orders of magnitude, exploiting low-rank structure. If that holds at scale,
consumer-GPU model parallelism over home fibre becomes plausible.

A caution for the ethical project: Pluralis's stated goal ("Protocol Learning") is a model that
**no participant can ever extract in full**, which suits monetisation. Decentralisation and
openness are different properties; a swarm can be decentralised and still closed.

## 3.6 Design for the network: modular training

Following the biology aside in [`1-physics-of-information.md`](1-physics-of-information.md), the
alternative to fighting the network is to train models that **need little communication by
construction**:

- **Branch-Train-Merge** (Li et al., 2022) / **Branch-Train-MiX** (Sukhbaatar et al., 2024):
  copies of a seed model are trained *independently* on different data domains, then merged
  or combined as a mixture-of-experts. Communication during training is near zero.
- **DiPaCo** (Douillard et al., 2024): a modular network where each worker trains one *path*
  through shared modules, and modules sync rarely.
- **Model soups and merging** (Wortsman et al., 2022 and successors): average fine-tuned
  weights.

This fits the governance picture in [02](../02-ethical-llm/README.md) well. Different communities
(a university, a language community, a free-software foundation) could each train an expert on
their own licence-clean data, with the canonical model as a merge ratified by vote.

## 3.7 Fine-tuning and RL: the easy part

- **LoRA / adapters** train ~0.1–1% of parameters. They are small to sync and small to share, and
  they ride on a Petals-style inference swarm (Petals supports this).
- **RL post-training** splits into embarrassingly parallel *rollouts* (pure inference, done by
  anyone) and a learner that updates weights. **INTELLECT-2** (Prime Intellect, 2025) trained a 32B
  reasoning model with globally distributed RL rollouts; Gensyn's RL Swarm explores the same shape.
  This is likely the phase where a broad volunteer swarm adds the most.

## 3.8 Where the state of the art sits

- The largest decentralised pretraining runs so far (INTELLECT-1 at 10B, Nous Consilience at 40B,
  Pluralis's 8B Protocol Model) used roughly **1,000× less compute than contemporary frontier
  models**, per Epoch AI's 2025 analysis.
- The gap is closing faster on the *method* side (communication cost per step) than on the
  *participation* side (number and reliability of contributors).
- Unsolved at scale: Byzantine-robust aggregation that doesn't waste most of the compute,
  verification of contributed work, and incentives that don't recentralise into a few big GPU
  farms. See [`5-trust-and-verification.md`](5-trust-and-verification.md).

## 3.9 A realistic path

1. **Pretrain** a 7–30B licence-clean base with DiLoCo-family optimizers on a few dozen fat nodes
   run by co-ops, universities and hackerspaces.
2. **Specialise** with branch-train-merge: communities train domain and language experts on their
   own data.
3. **Post-train** (RL, constitution alignment) on a broad volunteer swarm, where rollouts are
   inference and anyone can help.
4. **Serve** through regional Petals-style swarms, with local inference for anything that fits on
   the user's device.

Frontier-scale pretraining on a pure crowd of consumer GPUs stays out of reach until activation
compression and verification both mature.
