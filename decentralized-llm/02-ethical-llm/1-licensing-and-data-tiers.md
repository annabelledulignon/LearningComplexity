# 1 · Licensing and data tiers

**Principle:** the model, everything needed to rebuild it, and everything it learned from are
free as in freedom, and nobody may take that freedom away from downstream users. Where the law
is unclear about whether training even needs permission, the project **honours authors' licence
choices anyway**. Consent expressed through a licence is the ethical baseline, whatever courts
decide.

## 1.1 Why a GNU licence, and which one

Permissive licences (MIT, Apache) let anyone make a proprietary derivative. Copyleft (the GNU
GPL family) requires derivatives to stay free. For a commons that many people pour data, compute
and votes into, copyleft is the guarantee that nobody can enclose it.

The catch for AI is that **models are mostly used over a network**. Under GPLv3, a company can
modify the model, serve it as an API, never "distribute" it, and owe nobody the source. The
**GNU Affero GPL v3 (AGPLv3)** closes that loophole: users interacting over a network get the
right to the corresponding source.

## 1.2 What is the "source code" of a model?

The GPL defines source as *"the preferred form of the work for making modifications to it."* For
a model that is contested:

| View | "Source" means | Who holds it |
|---|---|---|
| Weights-only | The weights (most people modify by fine-tuning) | Many "open-weight" releases |
| Data information | Weights + code + a detailed *description* of the data | OSI Open Source AI Definition 1.0 (Oct 2024) |
| Full freedom | Weights + code + **the training data itself**, all under free licences | FSF (criteria for free ML applications, presented at FOSDEM 2025) |

This project takes the FSF position. **Model Corresponding Source** means all of:

1. Weights in a standard, documented format.
2. All training, data-processing, evaluation and inference code (AGPLv3).
3. **The training data**, or exact retrievable copies served from the project's own swarm
   (GPLv3 §6(d) allows corresponding source to be offered from a network server, which the
   storage design in [01 / storage](../01-distributed-feasibility/4-storage-and-coherence.md)
   provides).
4. A **data manifest**: per document, its hash, source, licence, author attribution and tier.
5. The tokenizer and the data it was trained on.
6. Configs, seeds, hyperparameters, training logs and intermediate checkpoints.
7. **All alignment data**: preference pairs, constitution versions, RLAIF prompts and critiques.
   Alignment data is training data too, and it is where a model's values hide, so it must be just
   as free.

Honest caveat: training is not bitwise reproducible
([01 / §4.6](../01-distributed-feasibility/4-storage-and-coherence.md)). The source rebuilds a
model that is *statistically* equivalent, not identical. That is still far more than any
weights-only release offers.

## 1.3 The licence structure, and a subtle trap

The natural idea is "AGPLv3 everything". But much of the best free text is under **CC BY-SA 4.0**
(Wikipedia, Stack Exchange), and CC BY-SA 4.0 is *one-way compatible with GPLv3* only. Adaptations
may be relicensed under GPLv3, and the AGPL is not on Creative Commons' list. *If* model weights
are legally an adaptation of their training data (unsettled, see §1.4), AGPLv3 weights could not
lawfully absorb Wikipedia.

GPLv3 §13 offers a way out. It allows a GPLv3 work to be combined with an AGPLv3 work, and says
the AGPL's network clause *"will apply to the combination as such."*

| | **Option A (proposed)** | Option B |
|---|---|---|
| Weights | **GPLv3-or-later** | AGPLv3-or-later |
| Code (training, inference server) | **AGPLv3-or-later** | AGPLv3-or-later |
| SaaS loophole | Closed if serving weights through the AGPL server makes a "combination" under §13 (untested) | Closed directly |
| CC BY-SA 4.0 data (Wikipedia, Stack Exchange) | ✅ Compatible | ❌ Only if training is not adaptation |
| GPLv2-*only* code (e.g. the Linux kernel) | ❌ Incompatible with GPLv3 | ❌ |

Option A keeps the richest free corpora and still reaches network users, provided the
combination argument holds. Whether weights loaded by an inference engine form a single combined
work (or are mere data, like a game's assets) has never been tested. **This needs review by
free-software lawyers** (the FSF licensing team, Software Freedom Conservancy, SFLC) before
anything ships. One irony to note: under the strict "weights are derivative" reading, the most
famous GPL program of all, the Linux kernel, is GPLv2-only and cannot be in a GPLv3 model.

**Output exception.** The model's own licence should explicitly *not* extend to what it
generates, with an additional permission like GCC's Runtime Library Exception. Users own their
outputs. One caveat cannot be waived by the project: if the model regurgitates a third-party
document verbatim, that document's licence still applies. Mitigations are deduplication,
memorisation testing, and the **attribution index** below.

**Attribution index.** Because every training document is public and licensed, any output can be
searched against the corpus (infini-gram / OLMoTrace-style) to show where a passage came from.
That satisfies CC BY attribution automatically. A closed-data model can never offer this; for a
free-data model it is a signature feature.

**Are weights even copyrightable?** It is unclear in most jurisdictions, since weights are
machine-produced numbers. Where they are not, copyleft on weights is unenforceable and becomes a
community norm. The code and data licences still bind.

## 1.4 Does training even need permission? (late 2026)

| Jurisdiction | State of play |
|---|---|
| **US** | Fair use, decided case by case. *Bartz v. Anthropic* (N.D. Cal., June 2025): training on lawfully acquired books was fair use, but building a library from pirated copies was not (followed by a reported $1.5B settlement). *Kadrey v. Meta* (June 2025): judgment for Meta on the record presented, with a warning that market-dilution arguments could win elsewhere. *Thomson Reuters v. Ross* (D. Del., Feb 2025): not fair use for a competing, non-generative tool. |
| **EU** | DSM Directive Art. 4: text-and-data-mining exception unless rights holders opt out in machine-readable form. The AI Act (GPAI obligations from Aug 2025) requires *all* GPAI providers, open-source included, to keep a copyright policy that honours opt-outs and to publish a training-content summary. In Germany, *GEMA v. OpenAI* (LG München I, Nov 2025) treated song lyrics memorised in a model as reproduction. |
| **Elsewhere** | Japan's Art. 30-4 is broad; the UK had not settled its position at last check. Public-domain status itself varies by country (life + 50, 70 or 100 years). |

Takeaway: the law is unsettled and differs by jurisdiction, and it may end up *more* permissive
than this project. The tier system below is an ethical commitment that is meant to stay right
whichever way the courts go.

## 1.5 The tiers

Three tiers of data strictness. **Every tier ships under the same licences (§1.3) with full
Corresponding Source.** What changes is how much of the training data's freedom is guaranteed.

### Tier A · *Libre*: the Stallman tier

> Every byte the model learned from was released by its author under a licence that is free
> **and** compatible with GPLv3.

- **Allowed:** public domain (with its jurisdiction recorded), CC0, CC BY 4.0, CC BY-SA 4.0,
  MIT/Expat, BSD-2/3-Clause, ISC, Apache-2.0, MPL-2.0 (unless marked incompatible with secondary
  licences), LGPL/GPL v3 (and v2-or-later), AGPLv3 (via §13).
- **Excluded:** GPLv2-only, GFDL-only, CC BY-NC / BY-ND (non-free), older CC versions unless
  checked individually, "all rights reserved", unknown or undetectable licences.
- **Synthetic data:** only if generated by a tier-A model. Text written by a non-free model may
  carry what it learned from non-free data. That would be licence laundering, and it is excluded.
- **Alignment data:** written by contributors under CC BY-SA 4.0 or CC0, with a
  Developer-Certificate-of-Origin-style sign-off.
- **Candidate sources:** the Common Pile v0.1 (filtered to compatible licences), Wikimedia
  projects, Project Gutenberg and other public-domain books (e.g. Harvard's Institutional Books),
  US federal government works, the CC BY / CC0 subsets of arXiv and PubMed Central, Stack
  Exchange, permissively and GPL-licensed code from Software Heritage, free-software
  documentation.
- **Expected capability:** Comma v0.1 (7B, 2T tokens of openly licensed text) matched Llama 1/2 7B
  at equal compute, so roughly two years behind the frontier at that size. It is weaker on
  informal language, personal narrative and non-English text, which are exactly the genres free
  licensing under-represents.

### Tier B · *Free*: every author chose a free licence

> Every byte the model learned from was released under *some* free licence, even if that
> licence is not GPLv3-compatible.

- **Adds:** GPLv2-only (the Linux kernel), GFDL-only, EPL, CDDL, OFL, CC BY / BY-SA 3.0 and
  earlier, Artistic 1.0, and similar.
- **Relies on:** the position that a trained model is not an adaptation of each document, so
  licence *compatibility* does not bind. Attribution and notices are preserved in the manifest.
- **Spirit:** still 100% free data. No author's explicit choice is overridden.

### Tier C · *Open-consent*: pragmatic

> Adds publicly accessible material whose authors expressed no licence but also **did not opt
> out**.

- **Adds:** web crawl filtered to honour robots.txt, ai.txt / TDM-reservation signals and EU
  Art. 4 opt-outs; plus PII scrubbing and deduplication.
- **Never, in any tier:** pirated material (shadow libraries), NC/ND-licensed works (an explicit
  author choice *against* this use), content behind access controls, or private data.
- **Corresponding Source caveat:** a crawl often cannot legally be redistributed, so tier C
  publishes URLs, hashes and processing code ("data information", as in the OSI definition). Put
  roughly: **tier C ≈ OSI-open, tier A ≈ FSF-free.**
- **Expected capability:** close to the best open-data models of the same size.

### Taint rules

| Operation | Resulting tier |
|---|---|
| Train on mixed-tier data | The lowest tier present |
| Merge or distil models of different tiers | The lowest tier involved |
| Synthetic data generated by a tier-X model | Tier X data |
| Fine-tune a tier-A model on tier-A data | Tier A |

Tier is part of the version manifest, and the data-coherence ledger
([01 / §4.5g](../01-distributed-feasibility/4-storage-and-coherence.md)) is how anyone verifies
that a "tier A" model saw only tier-A shards.

## 1.6 Pipeline

1. **Ingest** with licence metadata from the source (repository licence files, Wikimedia dumps,
   CC metadata). Code goes through ScanCode-style detection.
2. **Classify** to a tier; anything ambiguous falls to the lower tier or is dropped.
3. **Audit** random samples by hand, publish the error rates, and set a target (e.g. < 0.1%
   misclassified in tier A).
4. **Correct**: when a document turns out to be mislabelled, remove it from the next version, log
   the correction publicly, and (for tier A) consider retraining or unlearning. The GPL cannot
   revoke past releases, so the commitment is forward-looking.
5. **Publish** the manifest and data alongside every release, as Corresponding Source.

## 1.7 Open questions

- Is Option A's §13 combination argument sound? Get the FSF's view in writing.
- Should tier A also exclude **CC BY-SA 4.0** to make AGPLv3 weights possible? That trades away
  Wikipedia to remove legal doubt.
- How do we credit **CC BY** authors at scale? Is the attribution index plus the manifest enough
  "reasonable manner" attribution?
- Can community-written corpora (oral histories, minority-language texts, informal writing
  donated under CC BY-SA) close tier A's genre gap? This would make a great participatory
  sub-project.
- How should a contributor's later wish to withdraw their own text be handled? Copyleft says no;
  kindness says maybe for future versions.
