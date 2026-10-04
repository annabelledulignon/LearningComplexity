# Prior art: annotated bibliography

Grouped by topic. arXiv IDs are given where checked; otherwise search the title.

## Surveys and overviews

- **Beyond a Single AI Cluster: A Survey of Decentralized LLM Training**, 2025. arXiv:2503.11023.
  The best single map of the field.
- **Distributed and Decentralised Training: Technical Governance Challenges in a Shifting AI
  Landscape**, 2025. arXiv:2507.07765. What decentralised training means for compute-based
  regulation.
- **Epoch AI, "How far can decentralized training over the internet scale?"**, 2025. Places the
  largest decentralised runs ~1,000× below frontier compute and projects the trend.

## Swarm inference

- **Petals** (Borzunov et al., ACL 2023 demo; NeurIPS 2023). arXiv:2209.01188.
  [github.com/bigscience-workshop/petals](https://github.com/bigscience-workshop/petals).
  BitTorrent-style inference and fine-tuning of 70B–176B models over a DHT; the reference design
  for [`2-inference.md`](2-inference.md).
- **exo**, **distributed-llama**, **llama.cpp RPC backend**. Split a model across a few machines
  on a home LAN. The "fat local cluster" end of the spectrum.

## Decentralised and low-communication training

- **hivemind** ([github.com/learning-at-home/hivemind](https://github.com/learning-at-home/hivemind)).
  The library under Petals: Kademlia DHT, decentralised averaging, DMoE.
- **Towards Crowdsourced Training of Large Neural Networks using Decentralized
  Mixture-of-Experts** (Ryabinin & Gusev, NeurIPS 2020). Experts found through a DHT.
- **Distributed Deep Learning in Open Collaborations / DeDLOC** (Diskin et al., NeurIPS 2021).
  Volunteers trained a Bengali language model (sahajBERT).
- **Moshpit SGD** (Ryabinin et al., NeurIPS 2021). Averaging in rotating small groups,
  churn-tolerant.
- **SWARM Parallelism** (Ryabinin et al., ICML 2023). arXiv:2301.11913. Fault-tolerant pipeline
  training over unreliable peers; the *square-cube law*.
- **DiLoCo** (Douillard et al., 2023). arXiv:2311.08105. Inner/outer optimisation, ~500× less
  communication.
- **Streaming DiLoCo** (Douillard et al., 2025). arXiv:2501.18512. Staggered fragment syncs,
  overlap, quantisation; up to ~400× less bandwidth.
- **DiPaCo: Distributed Path Composition** (Douillard et al., 2024). Modular paths through
  shared modules.
- **OpenDiLoCo** (Jaghouar et al., Prime Intellect, 2024) and **INTELLECT-1 Technical Report**
  (2024, arXiv:2412.01152). 10B, 1T tokens, 3 continents, 30 contributors. **INTELLECT-2**
  (2025): 32B, globally distributed RL.
- **DeMo: Decoupled Momentum Optimization** (Peng, Chen, Su, Quesnelle, Kingma, Liu; ICLR 2026).
  arXiv:2411.19870. Basis of Nous Research's DisTrO and the Psyche network (Consilience 40B, 2025).
- **Pluralis Research, Protocol Models / Protocol Learning** (2025). Compressed model-parallel
  training in which no participant holds the full model.
- **Branch-Train-Merge** (Li et al., 2022) and **Branch-Train-MiX** (Sukhbaatar et al., 2024).
  Embarrassingly parallel expert training, merged afterwards.
- **Communication-Efficient Learning of Deep Networks from Decentralized Data / FedAvg**
  (McMahan et al., AISTATS 2017). Federated learning.
- **PowerSGD** (Vogels et al., NeurIPS 2019). Low-rank gradient compression.
- **PipeDream** (Narayanan et al., SOSP 2019). Asynchronous pipeline training and weight stashing.

## Storage and discovery

- **Kademlia** (Maymounkov & Mazières, IPTPS 2002). XOR-metric DHT.
- **S/Kademlia** (Baumgart & Mies, 2007). Sybil- and eclipse-resistant Kademlia.
- **Design and Evaluation of IPFS** (Trautwein et al., SIGCOMM 2022). Real-world DHT behaviour.
- **BitTorrent BEP 52 (v2)**. Per-file SHA-256 Merkle trees.
- **Storj v3 whitepaper** (2018). Reed–Solomon 29-of-80 erasure coding with repair.
- **Filecoin**. Proof-of-replication and proof-of-spacetime.

## Trust, verification, determinism

- **Secure Distributed Training at Scale / BTARD** (Gorbunov et al., ICML 2022).
- **Machine Learning with Adversaries / Krum** (Blanchard et al., NeurIPS 2017); **Byzantine-Robust
  Distributed Learning** (Yin et al., ICML 2018); **A Little Is Enough** (Baruch et al., NeurIPS 2019).
- **Practical Delegation of Computation Using Multiple Servers** (Canetti, Riva & Rothblum, CCS 2011).
  Refereed delegation; applied to ML in Gensyn's **Verde** (2025) with RepOps.
- **zkLLM** (Sun, Li & Zhang, CCS 2024). arXiv:2404.16109. 13B inference proofs in under 15 minutes.
- **Proof-of-Learning** (Jia et al., IEEE S&P 2021) and **Proof-of-Learning is Currently More
  Broken Than You Think** (Fang et al., EuroS&P 2023).
- **Defeating Nondeterminism in LLM Inference** (Thinking Machines Lab, 2025). Batch-invariant
  kernels.

## Privacy of activations

- **Text Embeddings Reveal (Almost) As Much As Text / vec2text** (Morris et al., EMNLP 2023).
  arXiv:2310.06816.
- **PUMA: Secure Inference of LLaMA-7B in Five Minutes** (Dong et al., 2023). MPC inference cost.
