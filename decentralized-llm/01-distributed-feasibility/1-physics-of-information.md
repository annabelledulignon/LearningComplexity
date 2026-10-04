# 1 · The physics of information

Before asking how clever a protocol can be, ask what the universe allows. Three quantities
decide almost everything:

| Quantity | What it limits | Can money fix it? |
|---|---|---|
| **Latency** (round-trip time, RTT) | Anything *sequential*: generating the next token, a synchronous all-reduce | No. Bounded below by the speed of light in fibre. |
| **Bandwidth** | Anything *bulky*: gradients, checkpoints, long-prompt activations | Yes, up to a point. Home links are the bottleneck. |
| **Memory bandwidth** (on the GPU) | Decode speed: every weight is read once per token | Yes. Buy HBM. |

## 1.1 Speed-of-light floor

Light in silica fibre travels at about 0.68 *c*, roughly 204,000 km/s or **4.9 µs per km**
(`estimate.py light`):

| Route | Distance | One-way floor | RTT floor |
|---|---|---|---|
| Same metro area | 50 km | 0.25 ms | 0.5 ms |
| Paris – Berlin | 880 km | 4.3 ms | 8.6 ms |
| New York – Los Angeles | 3,940 km | 19.3 ms | 38.6 ms |
| New York – London | 5,570 km | 27.3 ms | 54.6 ms |
| London – Sydney | 16,990 km | 83.3 ms | 166.6 ms |
| Antipodes | 20,000 km | 98.1 ms | 196.1 ms |

Real paths follow cables, not great circles, and add routing and queuing delay, so observed RTTs
run 1.3–2× these floors (NY–London is typically ~70 ms). No protocol, blockchain or optimizer
gets under the floor. Hollow-core fibre (~0.99 *c*) and low-orbit satellite links (vacuum, but
longer paths) shave a constant factor at best.

Compare the inside of a GPU server: NVLink hops are on the order of **microseconds**. Moving a
computation from one rack to another continent multiplies its communication latency by
**10,000–100,000×**.

## 1.2 The bandwidth cliff

(`estimate.py bandwidth`)

| Link | Bandwidth | NVLink is … × faster |
|---|---|---|
| HBM3 (on-GPU memory) | 3.35 TB/s | 0.27× (HBM is faster still) |
| NVLink 4 (GPU↔GPU, same server) | 900 GB/s | 1× |
| InfiniBand NDR 400 Gb/s (data-center fabric) | 50 GB/s | 18× |
| 10 GbE | 1.25 GB/s | 720× |
| 1 Gb/s home fibre | 125 MB/s | 7,200× |
| 100 Mb/s home broadband | 12.5 MB/s | 72,000× |
| 20 Mb/s home *upload* | 2.5 MB/s | **360,000×** |

Two things stand out:

- **Upload is the binding direction.** A node that *serves* (sends activations onward, shares
  gradients, seeds weights) is limited by its upload, which on cable and DSL is often a tenth of
  its download.
- **Datacenter parallelism strategies assume the top three rows.** Tensor parallelism, fully
  sharded data parallelism (FSDP/ZeRO-3) and synchronous all-reduce every step were designed
  for links three to five orders of magnitude faster than the internet. Porting them unchanged
  fails, and section 5 of `estimate.py` shows by how much.

## 1.3 Which constraint hits which workload

| Workload | Bytes per network hop | Bound by |
|---|---|---|
| Decode one token (70B, batch 1) | one hidden state: 8,192 × 2 B = **16 KB** | **Latency.** 16 KB is nothing. |
| Prefill a 4,096-token prompt (70B) | 4,096 × 16 KB = **67 MB** per hop | **Bandwidth.** 0.5 s at 1 Gb/s, ~27 s at 20 Mb/s upload. |
| One data-parallel gradient sync (70B, bf16) | ~141 GB × 2 (ring all-reduce) | **Bandwidth.** 38 min at 1 Gb/s. |
| Pipeline training, one stage (70B) | ~32 KB per token, ~8,000 tokens/s | **Bandwidth.** ~2 Gb/s needed each way. |

## 1.4 The critical path cannot be parallelised away

Autoregressive generation is a chain of strict dependencies:

```
token t ──► layer 1 ──► layer 2 ──► … ──► layer L ──► token t+1 ──► layer 1 ──► …
```

Each arrow is sequential. If consecutive layers live on different continents, network latency
sits *inside* that chain, and Amdahl's law says no amount of extra hardware removes it. There are
only three escapes:

1. **Fewer hops on the critical path.** Give each node a larger contiguous block of layers, and
   route latency-aware (prefer nearby peers).
2. **More tokens per traversal.** Speculative decoding (a local draft model proposes, the swarm
   verifies several tokens at once) and multi-token-prediction heads.
3. **Give up on per-user latency and sell throughput.** A swarm can serve *many* users at once
   at high aggregate throughput (Little's law), even while each user waits.

## 1.5 An aside from biology

The brain is a *slow* network. Myelinated axons conduct at up to ~100 m/s, about two
million times slower than light in fibre. Yet it works, because its architecture is built for
that medium: overwhelmingly local computation, sparse long-range communication, and massive
parallelism with no global clock.

Dense transformers have the opposite shape: every layer depends on every previous layer, and
data-center training synchronises everything every step. The lesson for decentralization may be
**don't port the data center; design for the network**. That points towards architectures with
locality built in: mixture-of-experts, modular or "branch-train-merge" models, and
asynchronous updates. [`3-training.md`](3-training.md) follows that thread.
