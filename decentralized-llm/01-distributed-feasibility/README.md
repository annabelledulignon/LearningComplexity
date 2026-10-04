# 01 · Feasibility of distributed (DHT-style) training and inference

**Question.** Could you train or run a large language model on a swarm of independently owned
machines, coordinated peer-to-peer (Kademlia-style DHT, gossip, a blockchain, or a mix) instead of
inside one data center? If you can't, which wall stops you first: compute, the speed of
information, storage coherence, or trust?

## Short answer (as of late 2026)

| Workload | Over the open internet today? | The binding constraint |
|---|---|---|
| **Inference, model fits one machine** (≤ ~30B at 4-bit on a 24 GB card) | ✅ Trivially. Just run it locally. | None. No network in the loop. |
| **Inference, 70B–400B pipelined across a swarm** (Petals-style) | ✅ Works, but slow: roughly 1–10 tokens/s per user | **Latency:** hops × round-trip time, *not* bandwidth |
| **Tensor-parallel inference across the internet** | ❌ No | 2 round trips per layer per token → seconds per token |
| **Fine-tuning (LoRA / adapters) on a swarm** | ✅ Yes | Few trainable parameters, so little to sync |
| **Pretraining on well-connected "fat" nodes** (each node an 8-GPU server) with DiLoCo-family optimizers | ✅ Demonstrated at 10B–40B scale (INTELLECT-1, Nous Consilience) | Sync bandwidth, hidden by syncing rarely |
| **Pretraining frontier-scale models on volunteer consumer GPUs** | ❌ Not yet | Memory (training state is ~16 bytes/param), model-parallel bandwidth, churn, verification, energy |
| **Storing and distributing weights & data** | ✅ Solved in principle (BitTorrent, IPFS, erasure codes) | *Which* version is canonical is a consensus problem, not a storage one |
| **Verifying strangers' compute** | 🟡 Partly | Redundancy and refereed delegation work; zero-knowledge proofs are still far too slow for training |
| **Keeping prompts private from the nodes that compute on them** | 🟡 Only locally or inside TEEs | MPC and FHE are orders of magnitude too slow (see [02 / privacy](../02-ethical-llm/4-privacy-architecture.md)) |

The core lesson in one sentence: **the DHT is the control plane, never the data plane.** A DHT
is excellent at answering *"who holds layers 40–59 of model `sha256:ab12…`?"* or *"who has chunk
C?"*. It is hopeless as the path a token's activations travel on, because every lookup costs
several sequential round trips.

## Reading order

1. [`1-physics-of-information.md`](1-physics-of-information.md): speed of light, the bandwidth
   cliff between NVLink and home internet, latency vs throughput. The floor everything else sits on.
2. [`2-inference.md`](2-inference.md): pipeline inference over a swarm, KV-cache state,
   speculative decoding, mixture-of-experts, why nodes can read your prompt.
3. [`3-training.md`](3-training.md): the compute bill, the gradient-sync wall, DiLoCo and
   friends, pipeline/SWARM parallelism and the square-cube law, the state of the art.
4. [`4-storage-and-coherence.md`](4-storage-and-coherence.md): chunk recoherence. Content
   addressing, Merkle manifests, erasure coding under churn, canonical versions, version skew, and
   floating-point non-determinism.
5. [`5-trust-and-verification.md`](5-trust-and-verification.md): Byzantine peers, Sybils,
   proving work was done, incentives.
6. [`prior-art.md`](prior-art.md): annotated bibliography.

## The calculator

[`estimate.py`](estimate.py) produces every number in these notes (standard library only):

```sh
python3 estimate.py              # full report
python3 estimate.py inference    # sections: light bandwidth memory inference tensor training pipeline storage
```

The hardware, network and model assumptions are constants at the top of the file. Change them
and re-run; don't trust a number in the prose that you can't regenerate.

## Open questions

- **Where is the crossover?** At what model width and node size does pipeline training over home
  connections become compute-bound instead of bandwidth-bound, given realistic activation
  compression (~10–100×)?
- **Can churn be made a feature?** Volunteer nodes come and go. Could DiLoCo-style replicas be
  short-lived by design, the way BitTorrent peers are?
- **What is the minimum trusted component?** Can verification be done with *no* trusted party,
  or is a small elected committee (see [02 / constitution](../02-ethical-llm/2-free-speech-and-democratic-constitution.md))
  unavoidable?
- **Energy honesty.** A consumer-GPU swarm burns several times the energy of a data center for the
  same FLOPs (`estimate.py training`). Does reusing hardware that already exists offset that?
- **Geography as topology.** Latency-aware routing clusters swarms by region. Does a global
  decentralized model naturally fragment into continental ones?
