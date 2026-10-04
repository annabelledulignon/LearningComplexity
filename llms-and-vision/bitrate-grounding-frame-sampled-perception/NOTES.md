# Vision in LLMs: Bitrate, Grounding, and the Limits of Frame-Sampled Perception

*Oct 3, 2026 · @annana*

Working notes for an arXiv-style article draft on the limitations of current multimodal LLM vision architectures, comparing frame-sampled retrofit approaches against natively trained video-native models, and situating both against the embodiment/grounding critique associated with Yann LeCun and JEPA-style world models.

## Instructions for the drafting model

This document is a brief for a more capable model to turn into a serious, long-form, citation-heavy article suitable for arXiv submission, using LaTeX formatting, formal mathematical notation where relevant, and grounding in recent (2024–2026) papers directly engaged with this subject rather than general-audience summaries.

The drafting model should not simply elaborate on the notes below politely. It should render an honest verdict: is this line of argument genuinely novel and thought-provoking relative to the existing literature (LeCun's JEPA program, embodied AI critiques, video-LLM scaling papers), or is it a well-trodden restatement of positions already made more rigorously elsewhere? If the latter, say so plainly rather than padding the piece to look original.

If the verdict is that the core idea is derivative or already well-covered, the drafting model should instead identify where the most technically serious and influential people engaged in this exact debate (AI researchers, lab leads, academics publishing on embodiment, world models, and multimodal grounding) read and discuss this kind of work — for example specific venues, blogs, preprint servers, or forums where a sharp critique could actually reach and move people making real training and investment decisions about embodied and visual learning versus token-prediction scaling — so the author can route the idea there instead of or in addition to arXiv.

## Framing: why this matters now

The current wave of multimodal AI (Gemini Live, Claude-based video plugins, startups like Overshoot promising sub-200 ms stream-to-model latency) is being marketed as a qualitative leap toward real-time visual understanding. An open question worth interrogating rigorously: is the distinction between frame-sampled, post-hoc vision bolted onto a text model, and a model trained natively on interleaved video-audio tokens, a difference of kind or merely of degree and engineering polish? And separately: does either approach constitute grounded understanding of the visual world, or only richer pattern association over labeled visual data?

## Engineering approaches compared

Two architecturally distinct paths currently exist for giving a language model access to visual stimuli over time, and the drafting model should treat their differences precisely rather than rhetorically.

### Path A: frame-sampled retrofit onto a text-native model

Projects such as `claude-video-vision` and `claude-real-video` extract frames from a video file via ffmpeg, apply scene-change detection to deduplicate near-identical frames, run audio through a separate transcription backend, and hand the resulting set of timestamped images plus transcript text to the model as a single batched multimodal prompt.

Overshoot (YC W2026) claims to connect arbitrary video streams to arbitrary vision-language models in under 200 milliseconds per frame, which addresses latency but not the underlying architectural fact that each frame is encoded independently of the others, with no learned temporal or motion representation between frames. The model infers continuity after the fact from a sequence of discrete, independently encoded stills.

### Path B: natively trained video-interleaved tokens

Gemini's documented approach samples video at a default of 1 frame per second (up to 10 fps in Live/real-time mode), converts each frame to roughly 258 visual tokens, and processes audio in parallel at approximately 32 tokens per second, for a combined cost on the order of 300 tokens per second of video.

Critically, these visual and audio tokens are interleaved and attended over jointly within a single transformer that was trained from the start on this interleaved multimodal stream, rather than having video bolted onto a model trained primarily on text. Some technical commentary (e.g. discussions of a "space-time tokenizer") describes tokens that span small spatial regions across several consecutive frames, which would in principle encode motion directly into the token rather than requiring the model to infer motion purely from attention across separately encoded stills.

### The central technical question

The drafting model should establish, with citations to primary technical documentation and any available architecture papers, whether Path B's joint training constitutes a qualitatively different representational capacity (e.g., tokens that natively encode motion/change) or whether it is best characterized as Path A's same frame-sampling strategy, merely integrated earlier in the pipeline and benefiting from joint training rather than post-hoc adapter fusion. This is the central technical question of the piece and should be argued rigorously rather than asserted.

## The grounding problem

Independent of the frame-sampling-versus-native-training question above, there is a deeper critique worth engaging seriously: that neither approach constitutes grounded understanding of the visual world, in the sense argued by Yann LeCun and the broader embodied-cognition and world-model literature.

The core of this critique: both paths train a system to associate visual input with labels, captions, or next-token predictions derived from human-annotated or human-generated data. Neither path requires the system to predict the physical consequences of a visual state and be corrected by the actual outcome, the way a human (or animal) builds a sensorimotor world model through continuous action, prediction, and physical error correction from infancy onward. A vision-language model can correctly describe a cup tipping over because it has seen many labeled examples of cups tipping over in training data, not because it predicted the tip, generated an expectation about momentum and liquid dispersion, and had that expectation falsified or confirmed by consequence.

LeCun's JEPA (Joint Embedding Predictive Architecture) program is the most prominent concrete attempt to close this gap: rather than predicting pixels or tokens, JEPA trains a model to predict the future latent representation of a scene from a partial or current observation, explicitly as a world model rather than a generative or token-prediction objective. The drafting model should locate and cite the current state of JEPA and related world-model literature (V-JEPA, V-JEPA 2, and any more recent iterations as of the drafting date), and assess directly whether this architecture class plausibly addresses the grounding gap, or whether it too remains a pattern-association system trained on passively collected video rather than self-generated embodied interaction.

### The "blind describer" analogy

The analogy worth preserving from the author's own framing, to be rendered precisely rather than decoratively: a vision-language model may function like *"a blind person who can describe everything perfectly"* — fluent and often correct in its visual descriptions and inferences, while lacking the embodied predictive loop that a sighted, physically active agent uses to verify and refine those descriptions against real consequence.

The piece should treat this as a falsifiable empirical claim where possible (e.g., failure modes in physical reasoning, robotics manipulation benchmarks, or physical commonsense evaluations where frontier vision-language models underperform relative to their descriptive fluency), not merely a rhetorical flourish.

## Open questions the article should answer

1. Is the frame-sampled-retrofit versus native-interleaved-training distinction one of architectural kind, or only of engineering integration and training-data joint-optimization? What evidence (ablations, published benchmarks, architecture disclosures) bears directly on this?
2. Does any current production system (Gemini included) demonstrably encode motion or temporal causality within its visual tokens themselves, versus inferring temporal continuity purely through cross-attention over independently encoded frames?
3. Does JEPA-style latent prediction meaningfully close the grounding gap, or does it remain a passive-data pattern-association system at a different level of abstraction?
4. What testable, falsifiable predictions distinguish a genuinely grounded embodied world model from a fluent but ungrounded vision-language model? Where do current frontier models already fail in ways that support the embodiment critique, and where (if anywhere) do they succeed in ways that complicate it?
5. **Final verdict required from the drafting model:** is this article's central thesis a genuinely novel contribution to the embodiment/grounding debate, or a restatement of positions already made more rigorously by LeCun, the JEPA papers, or other embodied-AI researchers? State this plainly near the top of the piece.

## If the verdict is that the idea is not novel: where to route it instead

If the drafting model concludes the core argument is already well-established in the literature, it should identify, by name, the specific venues where the most serious and influential people in this exact debate actually read and engage — for example:

- the Alignment Forum and LessWrong-adjacent technical AI discourse;
- Twitter/X accounts of specific named embodied-AI and world-model researchers;
- workshop venues at NeurIPS/ICML/ICLR focused on embodied AI or world models;
- LeCun's own public commentary channels;
- Interconnects or similar technical AI-research Substacks;
- specific labs or academic groups (e.g. those publishing JEPA follow-ups) whose public-facing blogs or preprint commentary would be the realistic path for a non-affiliated author's critique to reach and influence people making real training-investment decisions.

Name specific, current (2025–2026) venues and people rather than generic categories.
