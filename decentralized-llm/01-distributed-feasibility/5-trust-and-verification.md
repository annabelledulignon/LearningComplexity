# 5 · Trust and verification

**Verdict:** a data center trusts its machines because one entity owns them. A swarm has to
assume some fraction of peers lie, free-ride, or attack. The tools exist (robust aggregation,
redundancy, refereed delegation, attestation, zero-knowledge proofs), but each costs compute,
hardware trust, or bitwise reproducibility. Today the cheap ones are probabilistic and the
rigorous ones are slow.

## 5.1 Who might misbehave, and how

| Adversary | Attack | Hurts |
|---|---|---|
| **Free-rider** | Claims credit for work not done (returns random or stale gradients) | Training efficiency, fairness of rewards |
| **Poisoner** | Crafts gradients that plant a backdoor or bias | Model integrity, silently and permanently |
| **Sybil** | Runs many identities to dominate aggregation, votes or routing | Everything that counts heads |
| **Steering server** | Returns subtly altered activations during inference | Individual answers (ads, propaganda, targeted lies) |
| **Eclipse attacker** | Surrounds a victim in the DHT so all its lookups hit attacker nodes | Discovery, so routes go only through hostile servers |
| **Snoop** | Logs the hidden states it computes on | Privacy (see [02 / privacy](../02-ethical-llm/4-privacy-architecture.md)) |

## 5.2 Robust aggregation (training)

Instead of averaging updates, use an aggregator that tolerates a fraction of bad ones:
**Krum** (Blanchard et al., 2017), coordinate-wise **median / trimmed mean** (Yin et al., 2018),
**centred clipping** (Karimireddy et al., 2021). **BTARD** (Gorbunov et al., 2022, "Secure
Distributed Training at Scale") adapts this to decentralised all-reduce, with peers re-computing
random slices of each other's work.

The limits are real. Robust aggregators throw away information from honest-but-unusual peers
(the people with unusual *data*, such as minority languages, are exactly the ones who look like
outliers). Carefully crafted poison can also hide within the natural variance of honest updates
("A Little Is Enough", Baruch et al., 2019). Robust aggregation raises the cost of attack; it
does not prevent it.

## 5.3 Proving the work was done

| Technique | How | Cost | Trust assumption | Maturity |
|---|---|---|---|---|
| **Redundancy** | Two or three peers do the same work; compare | 2–3× compute | Not all copies colluding | Easy; needs determinism (§5.4) |
| **Random audits** | Re-execute a random fraction of submitted work | Audit rate (e.g. 5%) | Cheaters can't predict audits | Easy; probabilistic deterrent with stake |
| **Refereed delegation** | On dispute, bisect the computation to the first diverging operation and re-run only that (Canetti, Riva & Rothblum, 2011; Gensyn's *Verde*, 2025) | ~Free unless disputed | At least one honest party | Promising; requires bitwise-reproducible ops |
| **Optimistic + fraud proofs** | Accept results; anyone can challenge within a window | Latency of the window | One watcher is honest and awake | Borrowed from blockchain rollups |
| **Trusted execution (TEE)** | Hardware attests to the code and weights running; GPU confidential computing on H100 and later | ~Few % | The chip vendor; no side channels | Shipping, but centralises trust in vendors |
| **zkML proofs** | Succinct proof that output = model(input) | zkLLM: 13B inference proof in < 15 min, < 200 kB | Maths only | Audits yes; per-token chat or training no |
| **Proof-of-learning** | Publish the training trajectory; verifiers replay segments (Jia et al., 2021) | Moderate | — | Shown to be spoofable (Fang et al., 2023) |

## 5.4 Determinism is a prerequisite

Redundancy, audits and refereed delegation all compare two executions. If two honest GPUs give
bitwise-different answers ([`4-storage-and-coherence.md`](4-storage-and-coherence.md) §4.6),
then either comparisons must be approximate (and an attacker hides inside the tolerance), or
everyone must run **deterministic, hardware-independent kernels** (Gensyn's RepOps,
batch-invariant kernels). Accept a speed penalty on the verification path in exchange for being
able to say "this is wrong" with certainty.

## 5.5 Sybil resistance: what counts as one participant?

| Mechanism | Weight goes to | Problem |
|---|---|---|
| Proof-of-work | Energy spent | Wasteful, unless the work *is* the useful training, which is hard to verify (§5.3) |
| Stake | Capital | Plutocracy |
| Reputation | History of good work | Slow to earn, can be farmed, hostile to newcomers |
| **Proof of personhood** | Unique humans | Hard to do privately; the same problem as the constitution's voter roll ([02](../02-ethical-llm/2-free-speech-and-democratic-constitution.md)) |

For the DHT itself, **S/Kademlia** (Baumgart & Mies, 2007) makes node IDs costly to choose
(crypto puzzles) and uses disjoint lookup paths, which blunts Sybil and eclipse attacks.

## 5.6 Why would anyone contribute?

| Motive | Precedent | Fit with the ethical project |
|---|---|---|
| Altruism / shared mission | Folding@home passed an exaFLOP in 2020; BOINC; Wikipedia | Excellent, but volatile |
| Reciprocity | Petals: host blocks and get priority; BitTorrent tit-for-tat | Good; non-financial |
| Institutional | Universities, public research clouds, co-ops (as with Debian mirrors) | Good; the "fat node" core |
| Tokens | Bittensor (TAO subnets), Nous Psyche (Solana), Gensyn | Uneasy: speculation, incentive gaming, and a drift towards GPU farms |

**Recentralisation is the default outcome of financial incentives.** Economies of scale push
work towards professional GPU farms, as happened with Bitcoin mining pools. Measure it rather
than assume it away: the *Nakamoto coefficient* (the minimum number of entities that together
control a third or half of compute or votes) belongs on the project dashboard.

A non-transferable **compute-credit** system (contribute GPU-hours, spend them on inference
priority) captures reciprocity without creating a speculative asset. That fits the GNU ethos much
better than a token.

## 5.7 A pragmatic stack

1. **Reputation + light stake** for routing and reward eligibility.
2. **Random audits** by deterministic re-execution, at a rate set so expected penalty exceeds
   expected gain from cheating.
3. **Refereed delegation** to settle disputes cheaply and exactly.
4. **Robust aggregation** (trimmed mean / centred clipping) at the outer DiLoCo step.
5. **TEEs optional**: nodes that offer them get a "confidential" badge and private traffic.
6. **zk proofs for releases**: for each canonical version, a published proof that the registered
   weights produce the published evaluation transcript.
