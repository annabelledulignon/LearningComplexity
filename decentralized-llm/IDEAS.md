# Ideas inbox

New ideas land here first, a few lines each. When one grows big enough, it moves into
`01-distributed-feasibility/`, `02-ethical-llm/`, or a new `03-…/` folder, and its line here
becomes a link.

Template:

```
### <short name>  (YYYY-MM-DD)
What: one or two sentences.
Why it matters: …
Touches: 01 / 02 / new
```

---

### Founding brief  (2026-10-04)
What: The two sub-projects as first described. (1) Feasibility of DHT-style training and
inference: compute limits, speed of information, chunk recoherence on distributed storage.
(2) The ethical LLM: fully open source under a GNU licence; data GNU-compatible, with a couple of
less strict tiers; uncensored, with a democratically amendable alignment constitution; the
prompter → answer → conversation → weights linkage protected by Monero-grade, quantum-resistant
cryptography.
Touches: 01, 02 → now [`01-distributed-feasibility/`](01-distributed-feasibility/) and [`02-ethical-llm/`](02-ethical-llm/)

### Open data as an attribution engine  (2026-10-04)
What: Because every training document is public and licensed, any output can be searched against
the corpus (an infini-gram / OLMoTrace-style index) to show *where a passage came from*, which
satisfies CC BY attribution automatically. A closed-data model can never offer this.
Touches: 02 (licensing), 01 (the index itself is a distributed storage problem)

### Forkability as the constitution's backstop  (2026-10-04)
What: Under the GPL, a minority that loses a constitutional vote can always fork the model and its
constitution. Exit backs up voice (Hirschman). Worth formalising: how do forks share data and
compute without splitting the swarm?
Touches: 02 (constitution), 01 (shared infrastructure)

### Speculative decoding as the swarm's latency fix  (2026-10-04)
What: A small local model drafts tokens and the big distributed model only verifies them. That
turns the swarm's worst property (round-trip latency) into a batch-verification problem. See the
numbers in `estimate.py inference`.
Touches: 01 (inference)
