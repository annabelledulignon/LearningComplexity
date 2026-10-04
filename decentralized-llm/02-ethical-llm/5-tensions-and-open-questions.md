# 5 · Tensions and open questions

The ideal combines commitments that pull against each other. Writing the tensions down is how
the design stays honest. Each row gives the current best resolution and how confident I am in
it. New ideas that sharpen or dissolve a tension go to [`../IDEAS.md`](../IDEAS.md) first.

## 5.1 The tension map

| # | Tension | Why it's real | Current resolution | Confidence |
|---|---|---|---|---|
| 1 | **Uncensored ↔ democratically amendable** | A majority could vote in censorship | Entrenched speech article; sunsets on every restriction; Layer-0 base always released; forkability | Medium-high |
| 2 | **Uncensored ↔ the law** | Node operators are liable where they live | Operator disclosure + routing around (Art. 8); the constitution governs the model, not operators' legal duties | Medium |
| 3 | **Free speech ↔ third parties** | Some outputs harm people who never consented (doxxing, non-consensual imagery) | Draft Art. 5: narrow, operational-only, sunsetting, or none at all, decided by the founding assembly | Open |
| 4 | **Privacy ↔ accountability** | Unlinkable users can't be held responsible; an unlinkable model can't be audited | Signed receipts the user may disclose voluntarily; public per-article test suite | Medium-high |
| 5 | **Anonymity ↔ one person, one vote** | Sybil resistance wants identity; privacy forbids it | Plural personhood mechanisms with zero-knowledge nullifiers | Low: an open research problem |
| 6 | **Licence purity ↔ capability** | Free-licensed text is smaller and narrower (little informal, personal or non-English writing) | Three data tiers with taint rules; community-donated corpora to close the gap | Medium |
| 7 | **AGPL ↔ CC BY-SA** | CC BY-SA 4.0 is compatible with GPLv3 only, not the AGPL | GPLv3 weights + AGPLv3 engine via GPLv3 §13; needs legal review | Low-medium |
| 8 | **Copyleft ↔ adoption** | Many companies avoid (A)GPL, so fewer contributors and less funding | Accepted by design: the point is that nobody can enclose it | High (as a value choice) |
| 9 | **Decentralisation ↔ efficiency** | Consumer swarms burn ~6× the energy of a data center for the same FLOPs | Fat-node core (co-ops, universities); swarm for RL rollouts and inference; local-first | Medium |
| 10 | **Decentralisation ↔ openness** | A swarm can be decentralised yet closed (Pluralis-style unextractable models) | Corresponding Source is constitutional (Art. 3); every manifest is public | High |
| 11 | **Incentives ↔ decentralisation** | Financial rewards drift towards GPU farms | Non-transferable compute credits; track the Nakamoto coefficient | Medium |
| 12 | **Blockchain ↔ privacy** | Ledgers are permanent and public; crypto breaks are retroactive | No conversation data on any ledger; the chain only for votes and payments | High |
| 13 | **Post-quantum ↔ practicality** | PQ signatures and proofs are 50–1000× larger | Hybrid classical + PQ; keep PQ artefacts off-chain where possible | Medium |
| 14 | **Democracy ↔ expertise** | Alignment and cryptography need expertise that most voters lack | Bicameral chambers; sortition assemblies with expert hearings; impact statements | Medium |
| 15 | **Global demos ↔ local norms** | Cultures disagree deeply on speech | A thin global constitution; a thick user-preference layer; forks | Medium |
| 16 | **Open data ↔ privacy of people *in* the data** | Freely licensed archives (mailing lists, forums) contain personal data | PII scrubbing in every tier; erasure requests honoured for future versions | Medium |
| 17 | **Open weights ↔ dual use** | Anyone can strip the alignment layer | Accepted: the constitution governs the commons' defaults, not forks | High (as a value choice) |
| 18 | **Content privacy ↔ distributed compute** | Nodes see activations | Tiered privacy levels with disclosure; push local inference | Medium (honest about limits) |

## 5.2 Questions for later

**Governance**
- Who sits on the founding assembly, and how is it chosen before personhood proofs exist?
- Should the model have *any* opinions of its own (Art. 6.2 option)?
- How should people affected by outputs, but not voting, be represented?

**Licensing and data**
- Will the FSF's final criteria for free ML applications match the tier-A rules? Engage early.
- Could a "data co-op" pay or credit people who donate writing under CC BY-SA?

**Technical**
- What is the smallest model that is "good enough" for local-first privacy, and when does it run
  on a phone?
- Can speculative decoding with a local draft model cut swarm traffic enough to make
  mixnet-routed inference pleasant?
- Can the constitutional test suite be made adversarially robust (hard to game by a model that
  learns the tests)?

**Economics**
- Who pays for the fat-node core? Grants, co-op membership fees, public research clouds,
  donations?
- Can compute credits be fair across hardware generations (an H100-hour vs a 4090-hour)?
