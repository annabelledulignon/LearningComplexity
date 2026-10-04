#!/usr/bin/env python3
"""Back-of-envelope numbers for decentralized LLM training and inference.

Every figure quoted in this folder's notes comes from this script, so the
assumptions live in one place. Edit the constants below and re-run:

    python3 estimate.py            # full report
    python3 estimate.py inference  # one section only

Sections: light, bandwidth, memory, inference, tensor, training, pipeline,
storage. Standard library only. These are order-of-magnitude estimates, not
benchmarks: real systems lose more to stragglers, retries and software
overhead than any formula here admits.
"""

import math
import sys

# --------------------------------------------------------------------------
# Physical constants and hardware assumptions (edit freely)
# --------------------------------------------------------------------------

C_VACUUM_KM_S = 299_792
FIBER_INDEX = 1.47  # refractive index of silica fibre -> light at ~0.68 c
C_FIBER_KM_S = C_VACUUM_KM_S / FIBER_INDEX

GPUS = {
    # name: (dense bf16 TFLOPS, memory GB, memory bandwidth GB/s, watts)
    "RTX 4090 (consumer)": (165, 24, 1008, 450),
    "H100 SXM (datacenter)": (989, 80, 3350, 700),
}

# Fraction of peak FLOPs actually achieved over a whole run, including
# stragglers, restarts and churn. Datacenter runs report ~40%; volunteer
# swarms are assumed much worse.
MFU = {"RTX 4090 (consumer)": 0.25, "H100 SXM (datacenter)": 0.40}

LINKS = {
    # name: bytes per second
    "HBM3 (on-GPU memory)": 3.35e12,
    "NVLink 4 (GPU-GPU, same box)": 900e9,
    "InfiniBand NDR 400 Gb/s": 50e9,
    "10 GbE": 1.25e9,
    "1 Gb/s home fibre": 125e6,
    "100 Mb/s home broadband": 12.5e6,
    "20 Mb/s home upload": 2.5e6,
}

# Dense Llama-3-family shapes (public model cards).
MODELS = {
    # name: params, d_model, layers, kv_heads, head_dim, vocab, train tokens
    "8B": dict(params=8.03e9, d=4096, layers=32, kv=8, hd=128, vocab=128256, tokens=15e12),
    "70B": dict(params=70.6e9, d=8192, layers=80, kv=8, hd=128, vocab=128256, tokens=15e12),
    "405B": dict(params=405e9, d=16384, layers=126, kv=8, hd=128, vocab=128256, tokens=15.6e12),
}

BYTES_PER_PARAM = {"bf16": 2.0, "int8": 1.06, "int4": 0.56}  # incl. scales
ADAM_MIXED_PRECISION_BYTES = 16  # bf16 w + bf16 g + fp32 master + 2 fp32 moments


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def human_bytes(n):
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(n) < 1000:
            return f"{n:,.1f} {unit}"
        n /= 1000
    return f"{n:,.1f} EB"


def human_time(s):
    if s < 1e-3:
        return f"{s * 1e6:,.1f} µs"
    if s < 1:
        return f"{s * 1e3:,.1f} ms"
    if s < 120:
        return f"{s:,.1f} s"
    if s < 3600:
        return f"{s / 60:,.1f} min"
    if s < 172800:
        return f"{s / 3600:,.1f} h"
    if s < 2 * 365 * 86400:
        return f"{s / 86400:,.1f} days"
    return f"{s / (365 * 86400):,.1f} years"


def table(headers, rows):
    widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)]
    line = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |"
    sep = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    out = [line, sep]
    for r in rows:
        out.append("| " + " | ".join(str(x).ljust(w) for x, w in zip(r, widths)) + " |")
    print("\n".join(out))
    print()


def params_per_layer(m):
    embeddings = 2 * m["vocab"] * m["d"]  # input embedding + untied LM head
    return (m["params"] - embeddings) / m["layers"]


def kv_bytes_per_token(m, bytes_per=2):
    return 2 * m["layers"] * m["kv"] * m["hd"] * bytes_per


def binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p)."""
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


# --------------------------------------------------------------------------
# Sections
# --------------------------------------------------------------------------

def light():
    print("## 1. Speed of light floor\n")
    print(f"Light in fibre travels at ~{C_FIBER_KM_S:,.0f} km/s "
          f"({1e6 / C_FIBER_KM_S:.1f} µs per km). Real routes are longer than the")
    print("great circle, so observed RTTs are typically 1.3-2x the floor.\n")
    routes = [
        ("Same metro area", 50),
        ("Paris - Berlin", 880),
        ("New York - Los Angeles", 3940),
        ("New York - London", 5570),
        ("London - Sydney", 16990),
        ("Antipodes (half the Earth)", 20000),
    ]
    rows = []
    for name, km in routes:
        one_way = km / C_FIBER_KM_S
        rows.append((name, f"{km:,}", human_time(one_way), human_time(2 * one_way)))
    table(["Route", "Distance (km)", "One-way floor", "RTT floor"], rows)


def bandwidth():
    print("## 2. The bandwidth cliff\n")
    ref = LINKS["NVLink 4 (GPU-GPU, same box)"]
    rows = []
    for name, bps in LINKS.items():
        ratio = ref / bps
        rows.append((name, f"{human_bytes(bps)}/s",
                     f"{ratio:,.0f}x" if ratio >= 1 else f"{ratio:.2f}x"))
    table(["Link", "Bandwidth", "NVLink / link"], rows)


def memory():
    print("## 3. Memory: what fits where\n")
    rows = []
    for name, m in MODELS.items():
        p = m["params"]
        row = [name]
        for prec in ("bf16", "int8", "int4"):
            b = p * BYTES_PER_PARAM[prec]
            row.append(f"{human_bytes(b)} ({math.ceil(b / 24e9)}x24GB)")
        row.append(human_bytes(p * ADAM_MIXED_PRECISION_BYTES))
        row.append(f"{kv_bytes_per_token(m) / 1e3:,.0f} KB")
        rows.append(row)
    table(["Model", "bf16 weights", "int8 weights", "int4 weights",
           "Training state (Adam)", "KV cache / token"], rows)
    m = MODELS["70B"]
    print(f"A single 8k-token conversation on 70B holds "
          f"{human_bytes(8192 * kv_bytes_per_token(m))} of KV cache, spread over")
    print("whichever servers host its layers. Lose a server, lose that slice.\n")


def inference():
    print("## 4. Pipeline inference over the internet (decode, batch 1)\n")
    m = MODELS["70B"]
    gpu_bw = GPUS["RTX 4090 (consumer)"][2] * 1e9
    weights = m["params"] * BYTES_PER_PARAM["int4"]
    compute = weights / gpu_bw  # decode is memory-bound: read every weight once
    act = m["d"] * 2
    print(f"70B int4 = {human_bytes(weights)}. Decode reads every weight once per token,")
    print(f"so pure compute across consumer GPUs is ~{human_time(compute)}/token. Each hop ships")
    print(f"one hidden state: {m['d']:,} x 2 bytes = {human_bytes(act)}. Bandwidth is irrelevant;")
    print("latency is everything. Client-mediated routing (as Petals does, for")
    print("fault tolerance) pays one full RTT per hop.\n")
    rtts = [("metro 5 ms", 0.005), ("continental 30 ms", 0.030),
            ("transatlantic 80 ms", 0.080), ("global 150 ms", 0.150)]
    rows = []
    for hops in (1, 2, 4, 8, 16):
        row = [hops]
        for _, rtt in rtts:
            row.append(f"{1 / (hops * rtt + compute):.1f}")
        rows.append(row)
    table(["Hops"] + [f"tok/s @ {n}" for n, _ in rtts], rows)

    print("Speculative decoding: a small local draft model proposes k tokens and")
    print("the swarm verifies them in one pass. Expected tokens per round trip:\n")
    rows = []
    for alpha in (0.5, 0.7, 0.85):
        row = [alpha]
        for k in (2, 4, 8):
            row.append(f"{(1 - alpha ** (k + 1)) / (1 - alpha):.2f}")
        rows.append(row)
    table(["Acceptance rate", "k=2", "k=4", "k=8"], rows)


def tensor():
    print("## 5. Why tensor parallelism over the internet is a non-starter\n")
    print("Megatron-style tensor parallelism needs 2 all-reduces per layer per")
    print("token. Each all-reduce costs at least one round trip. Lower bound:\n")
    rows = []
    for name, m in MODELS.items():
        row = [name, m["layers"]]
        for rtt in (0.000005, 0.005, 0.030, 0.080):
            row.append(human_time(2 * m["layers"] * rtt))
        rows.append(row)
    table(["Model", "Layers", "@ 5 µs (NVLink)", "@ 5 ms", "@ 30 ms", "@ 80 ms"], rows)


def training():
    print("## 6. Training: compute budget and the gradient-sync wall\n")
    rows = []
    for name, m in MODELS.items():
        flops = 6 * m["params"] * m["tokens"]
        row = [name, f"{m['tokens'] / 1e12:g}T", f"{flops:.2e}"]
        for gpu, (tflops, _, _, watts) in GPUS.items():
            eff = tflops * 1e12 * MFU[gpu]
            gpu_hours = flops / eff / 3600
            row.append(f"{gpu_hours / 1e6:,.1f}M GPU-h, {gpu_hours * watts / 1e9:,.1f} GWh")
        rows.append(row)
    table(["Model", "Tokens", "FLOPs (6ND)"] + list(GPUS), rows)

    m = MODELS["70B"]
    flops = 6 * m["params"] * m["tokens"]
    eff = GPUS["RTX 4090 (consumer)"][0] * 1e12 * MFU["RTX 4090 (consumer)"]
    for n in (1_000, 10_000, 100_000):
        print(f"- 70B on {n:>7,} volunteer RTX 4090s (if communication were free): "
              f"{human_time(flops / eff / n)}")
    # A licence-clean first target: Comma v0.1 was 7B params on 2T tokens.
    comma = 6 * 7e9 * 2e12
    print(f"- Comma-scale 7B on 2T tokens ({comma:.1e} FLOPs) on 1,000 RTX 4090s: "
          f"{human_time(comma / eff / 1000)}")
    print()

    grad = m["params"] * 2  # bf16
    per_sync = 2 * grad  # ring all-reduce sends ~2x the payload per node
    steps = m["tokens"] / 16e6  # 16M-token global batch
    print(f"Data-parallel sync for 70B: {human_bytes(grad)} of bf16 gradients; a ring")
    print(f"all-reduce pushes ~{human_bytes(per_sync)} through every node. At a 16M-token")
    print(f"batch, 15T tokens is ~{steps:,.0f} optimizer steps.\n")
    rows = []
    for link in ("1 Gb/s home fibre", "100 Mb/s home broadband"):
        bw = LINKS[link]
        t = per_sync / bw
        row = [link, human_time(t), human_time(steps * t)]
        for h, comp in ((500, 2), (500, 8)):  # DiLoCo-style: sync every h steps
            row.append(human_time(steps / h * t / comp))
        rows.append(row)
    table(["Link", "One sync", "Sync every step",
           "Every 500 steps, int8", "Every 500 steps, ~8x compressed"], rows)
    print("(Pure communication time. Modern methods overlap it with compute, and")
    print("the inner steps between syncs still need each replica to hold the model.)\n")


def pipeline():
    print("## 7. Pipeline training on consumer GPUs: the square-cube law\n")
    print("Split layers across volunteers. A layer's compute grows with d^2 per")
    print("token but the activation it hands on grows with d, so wider layers are")
    print("*easier* to pipeline (SWARM parallelism, Ryabinin et al. 2023).\n")
    tflops, mem_gb, _, _ = GPUS["RTX 4090 (consumer)"]
    eff = tflops * 1e12 * MFU["RTX 4090 (consumer)"]
    usable = mem_gb * 1e9 * 0.7  # leave room for activations
    rows = []
    for name, m in MODELS.items():
        ppl = params_per_layer(m)
        layer_state = ppl * ADAM_MIXED_PRECISION_BYTES
        if layer_state <= usable:
            layers, gpus = int(usable // layer_state), 1
            stage = f"{layers} layers / 1 GPU" if layers > 1 else "1 layer / 1 GPU"
        else:
            layers, gpus = 1, math.ceil(layer_state / usable)
            stage = f"1 layer / {gpus} GPUs"
        tok_s = gpus * eff / (6 * ppl * layers)
        sent_per_token = m["d"] * 2 * 2  # fwd activation out + bwd gradient back
        traffic = tok_s * sent_per_token
        rows.append((name, f"{ppl / 1e6:,.0f}M", f"{6 * ppl / sent_per_token:,.0f}",
                     stage, f"{tok_s:,.0f}", f"{traffic * 8 / 1e9:,.2f} Gb/s",
                     f"{traffic / LINKS['20 Mb/s home upload']:,.0f}x"))
    table(["Model", "Params/layer", "FLOPs per byte sent", "Stage",
           "Tokens/s per stage", "Needed each way", "vs 20 Mb/s upload"], rows)
    print("FLOPs per byte sent per layer roughly doubles with each step up in")
    print("width: that is the square-cube law. But a 24 GB card is capped at")
    print("~1B trainable parameters, so per-GPU traffic stays at 1-2 Gb/s whatever")
    print("the model: the law only pays off on nodes fat enough to hold whole wide")
    print("layers. The 50-200x gap to home upload is what activation compression")
    print("(and bigger nodes) must close.\n")


def storage():
    print("## 8. Chunk recoherence under churn\n")
    print("First, just moving the bytes. Time to fetch a full checkpoint from one peer:\n")
    rows = []
    for name, m in MODELS.items():
        row = [name]
        for prec in ("bf16", "int4"):
            b = m["params"] * BYTES_PER_PARAM[prec]
            for link in ("1 Gb/s home fibre", "100 Mb/s home broadband"):
                row.append(human_time(b / LINKS[link]))
        rows.append(row)
    table(["Model", "bf16 @ 1 Gb/s", "bf16 @ 100 Mb/s", "int4 @ 1 Gb/s", "int4 @ 100 Mb/s"],
          rows)
    print("A model is stored as N chunks on volunteer nodes that are each online")
    print("with probability p. Replication r: a chunk is lost if all r copies are")
    print("offline. Erasure coding RS(k, n): any k of n shards rebuild the chunk.\n")
    schemes = [("3x replication", 1, 3), ("5x replication", 1, 5),
               ("RS(10, 30) 3x", 10, 30), ("RS(10, 40) 4x", 10, 40),
               ("RS(29, 80) 2.8x", 29, 80)]
    chunks = 1400  # e.g. a 140 GB checkpoint in 100 MB chunks
    rows = []
    for name, k, n in schemes:
        row = [name]
        for p in (0.5, 0.8, 0.95):
            p_chunk_missing = binom_cdf(k - 1, n, p)
            p_model = (1 - p_chunk_missing) ** chunks
            row.append(f"{p_chunk_missing:.1e} / {p_model:.3f}")
        rows.append(row)
    table(["Scheme", "p=0.5", "p=0.8", "p=0.95"], rows)
    print(f"Each cell: P(one chunk unrecoverable) / P(all {chunks:,} chunks recoverable")
    print("right now). RS(29, 80) is the shape Storj uses. Volunteer-grade uptime")
    print("(p ~ 0.5) makes plain replication useless at model scale.\n")


SECTIONS = dict(light=light, bandwidth=bandwidth, memory=memory, inference=inference,
                tensor=tensor, training=training, pipeline=pipeline, storage=storage)

if __name__ == "__main__":
    chosen = sys.argv[1:] or list(SECTIONS)
    for s in chosen:
        if s not in SECTIONS:
            sys.exit(f"unknown section {s!r}; choose from {', '.join(SECTIONS)}")
        SECTIONS[s]()
