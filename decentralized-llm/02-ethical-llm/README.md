# 02 · The ethical LLM ideal

**Question.** If we designed a language model from first principles around freedom, consent,
democracy and privacy, rather than around a company's business model, what would it look like,
and what would it take?

## The ideal in five commitments

| # | Commitment | In one line | Detail |
|---|---|---|---|
| 1 | **Free software** | Weights, code and everything needed to rebuild the model under GNU licences: AGPLv3 code, GPLv3 weights | [Licensing](1-licensing-and-data-tiers.md) §1.1–1.3 |
| 2 | **Free data** | Trained only on data whose authors chose free licences, in three tiers from strict (Stallman) to pragmatic | [Licensing](1-licensing-and-data-tiers.md) §1.5 |
| 3 | **Free speech** | Uncensored by default; no hidden refusals; every limit written down and cited | [Constitution design](2-free-speech-and-democratic-constitution.md) §2.1 |
| 4 | **Democratic alignment** | Behaviour set by a constitution its community amends: deliberation, secret receipt-free votes, an entrenched core, forkability as the backstop | [Constitution design](2-free-speech-and-democratic-constitution.md) · [Draft v0](3-draft-constitution-v0.md) |
| 5 | **Unlinkable privacy** | No one but the user can link them to their prompts, answers, conversations or the weights that served them, with Monero-style primitives rebuilt on post-quantum cryptography | [Privacy architecture](4-privacy-architecture.md) |

How they reinforce each other:

- **Free data enables attribution.** Because the corpus is public, any output can be traced to
  its sources, which satisfies CC BY automatically. Closed-data models can't do this.
- **Copyleft enables exit.** Anyone outvoted on the constitution can fork everything, which is
  what makes majority rule safe for minorities.
- **Privacy enables honest democracy.** Secret, receipt-free ballots stop vote buying and coercion.
- **Free alignment data enables audit.** The exact data that turned the constitution into weights
  is public, so "behaviour ≠ text" can be checked.

## Reading order

1. [`1-licensing-and-data-tiers.md`](1-licensing-and-data-tiers.md): which GNU licence, what
   counts as a model's "source", the CC BY-SA ↔ AGPL trap, the legal landscape, the three data
   tiers and taint rules.
2. [`2-free-speech-and-democratic-constitution.md`](2-free-speech-and-democratic-constitution.md):
   what "uncensored" means precisely, layered alignment, who votes, proof of personhood,
   deliberation, the amendment cycle, turning text into weights.
3. [`3-draft-constitution-v0.md`](3-draft-constitution-v0.md): a strawman constitution with the
   open choices in [brackets].
4. [`4-privacy-architecture.md`](4-privacy-architecture.md): the linkage graph, Monero's
   primitives and why they aren't quantum-safe, the post-quantum toolbox, what belongs on a
   ledger (and what never does), the activation-privacy problem.
5. [`5-tensions-and-open-questions.md`](5-tensions-and-open-questions.md): eighteen tensions,
   how each is currently resolved, and how confident I am.

## Decisions waiting on you

These are choices about the vision, not technical details. The notes take a default and flag it:

1. **Licence structure.** Default: *GPLv3 weights + AGPLv3 code* (keeps Wikipedia/Stack Exchange
   in tier A; closes the SaaS loophole via GPLv3 §13, pending legal review). Alternative:
   AGPLv3 for everything, dropping CC BY-SA data from tier A.
2. **Blockchain scope.** Default: *no conversation data on any ledger, even encrypted*. Use a chain
   only for votes and payments, and transparency logs for the registry. The brief imagined the
   linkage itself on a chain; [§4.6](4-privacy-architecture.md) explains why permanence works
   against that goal.
3. **Article 5.** Default: *left open*, with candidate narrow limits listed alongside a "no limits"
   option. This is the heart of the free-speech question and belongs to you, and eventually to the
   founding assembly.

## Relation to sub-project 01

The feasibility study sets what's buildable: pretraining a tier-A model at ~7B scale (the size of
Comma v0.1) is within reach of a modest fat-node federation; swarm inference works but is
latency-bound; and **content privacy against compute nodes is the deepest technical gap**. That
gap is shared by both halves of the project, and local-first inference is the best answer
available today.
