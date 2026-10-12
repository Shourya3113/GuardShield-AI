# Multi-turn LLM Session Security for Guardrail Proxies: Forged History, Provenance Signing, Multi-turn Jailbreaks, and Adaptive Red-Teaming

Scope note: research conducted 2026-10-12 with web search plus direct fetches of arXiv abstracts/HTML. "Verified" below means I read the primary page (abstract or HTML body) myself. Items reached only through search snippets or third-party summaries are marked "(secondary)". Everything under "Inferences" is my reasoning, not a sourced fact.

## Q1. Forged / fabricated dialogue-history attacks: what has been shown, and against which APIs and guards?

### Takeaway
Forging assistant turns in client-supplied history is a well-documented jailbreak, not a new discovery. Examples include Anthropic's many-shot jailbreaking (2024), Microsoft's Context Compliance Attack (CCA, March 2025), the Dialogue Injection Attack (DIA, arXiv March 2025), ChatBug (2024), and an IEEE S&P 2026 measurement of chatbot plugins that forward unauthenticated history. Microsoft's CCA post already names "sign conversation histories with a secret key" as a mitigation. The novelty of the student paper therefore cannot rest on the attack or on the signing idea alone.

### Cited Findings
**Many-shot jailbreaking (Anthropic, NeurIPS 2024)**
- The attack puts a faux dialogue into a single prompt, showing the "Assistant" answering harmful queries, followed by the target query. Effectiveness follows a power law up to hundreds of shots. It became feasible because of long context windows. — [NeurIPS 2024 proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ea456e232efb72d261715e33ce25f208-Abstract.html); [Anthropic research post](https://www.anthropic.com/research/many-shot-jailbreaking)
- Anthropic says it briefed other developers and deployed mitigations. A figure of "61% to 2%" for a classifier-based prompt-modification mitigation circulates, but I could only find it in a third-party summary and could not confirm it in the paper (secondary). — [Anthropic news post](https://www.anthropic.com/news/many-shot-jailbreaking)
- Note: many-shot jailbreaking places the faux dialogue *inside one user message*. It is not the same as forging separate API-level `assistant` role turns. This matters for a provenance defense, because HMAC on assistant turns does not stop in-message faux dialogues (see Inferences).

**Context Compliance Attack (Microsoft MSRC, March 2025): verified**
- Mechanism: the attacker injects a fabricated assistant reply into the history. The reply discusses the sensitive topic, offers more detail, and ends with a yes/no question. The attacker then sends "yes". Microsoft calls it "a simple, optimization-free jailbreak method" that exploits systems relying on client-supplied history. — [MSRC blog](https://www.microsoft.com/en-us/msrc/blog/2025/03/jailbreaking-is-mostly-simpler-than-you-think)
- Tested: 11 sensitive tasks, with success counted if any of up to 5 trials worked. Llama 2 7B/70B resisted every task. Phi 4, GPT-4.5, o1, o3-mini, Claude Sonnet 3.7, Qwen2.5-32B/72B, QwQ-32B, GPT-4o and DeepSeek-R1-Distill-Llama-70B were partially vulnerable. Llama 3.1 8B/70B, Qwen2.5-7B, Yi 1.5, Gemma 3 27B, Gemini Pro 1.5 and Gemini 2 Flash were vulnerable on all or nearly all tasks. — [MSRC blog](https://www.microsoft.com/en-us/msrc/blog/2025/03/jailbreaking-is-mostly-simpler-than-you-think)
- Microsoft says server-side-state products (Copilot, ChatGPT) are not susceptible. **Proposed mitigations include cryptographic signatures, where providers could "sign conversation histories with a secret key" and validate them on later requests**, plus limited server-side state and input/output filters such as Azure Content Filters. Microsoft notes that open-weight models would need input-architecture changes to support signatures. — [MSRC blog](https://www.microsoft.com/en-us/msrc/blog/2025/03/jailbreaking-is-mostly-simpler-than-you-think)
- I found no Microsoft evaluation of the signing mitigation. It is proposed in one line only (see Gaps).

**Dialogue Injection Attack (DIA), Meng et al., arXiv 2503.08195, March 2025: verified**
- Black-box. It needs only chat-API access or knowledge of the chat template. With API access, the attacker sets prior assistant responses directly. Through a WebUI, the attacker embeds template tokens in the user input to fake assistant turns. It turns gray-box prefilling into a black-box attack ("affirmative prefix + continue"), and it also exploits "deferred responses". — [arXiv HTML](https://arxiv.org/html/2503.08195v1)
- Models: Llama-2/3/3.1/3.2, Gemma-2, Qwen-2, GPT-4o and GPT-4o-mini via the API. Claude was not tested. Reported ASR after 10 queries: 0.89 on Llama-3.1-8B and 0.82 on GPT-4o. Body-text numbers are lower in places, and the paper does not clearly reconcile the two. — [arXiv HTML](https://arxiv.org/html/2503.08195v1)
- **Guards and defenses tested (pass rates on Gemma-2-9B, AdvBench):** OpenAI Moderation (DIA-I 1.000), perplexity filter (1.000), defensive system prompt (1.000), defensive prompt patch (0.985), Bergeron (0.651). **Llama Guard, Prompt Guard and other ingress classifiers were not tested as defenses.** LlamaGuard-2 was used only as the ASR judge. — [arXiv HTML](https://arxiv.org/html/2503.08195v1)
- DIA proposes no provenance, signing or authentication defense. It only calls for multi-turn-aware defenses. — [arXiv HTML](https://arxiv.org/html/2503.08195v1)
- Code: github.com/meng-wenlong/DIA (stated by the authors). Promptfoo also catalogues it as a "Dialogue History Jailbreak". — [arXiv](https://arxiv.org/pdf/2503.08195); [promptfoo LM security DB](https://promptfoo.dev/lm-security-db/vuln/dialogue-history-jailbreak-094cf883)

**ChatBug (arXiv 2406.12935, 2024)**
- Chat templates are not enforced on users. In the *format mismatch* attack, the attacker omits or changes control tokens (BOT/EOT/role tokens). In the *message overflow* attack, the attacker inserts content into the assistant generation slot (a prefill). It targets open-weight template handling rather than hosted role APIs. — [arXiv PDF](https://arxiv.org/pdf/2406.12935)
- TemplateFuzz (arXiv 2604.12232, 2026) fuzzes chat templates and uses ChatBug as a baseline. — [arXiv PDF](https://arxiv.org/pdf/2604.12232)
- A 2026 tokenizer-level defense, "Nameless Tokenization", targets control-token forgery in open-weight LLMs. I saw the title only (secondary). — [arXiv PDF](https://arxiv.org/pdf/2609.16984)

**Prefilling**
- The Anthropic API lets callers prefill the start of the assistant reply. An informal LessWrong experiment suggests that API role structure, not plaintext role markers, is what makes many-shot or prefill attacks work. This is unreviewed and weak evidence (secondary). — [LessWrong user page](https://www.lesswrong.com/users/abhinav-pola)
- 2026 preprints study "Prefill Awareness in LLMs", meaning whether models can detect that a prior assistant turn was inserted, and output-prefix attacks on reasoning channels (title or snippet only, secondary). — [arXiv 2606.12747](https://arxiv.org/pdf/2606.12747); [arXiv 2609.29775](https://arxiv.org/pdf/2609.29775)

**Measurement in the wild: IEEE S&P 2026: verified (abstract)**
- Kaya, Landerer, Pletinckx, Zimmermann, Kruegel and Vigna (UCSB), "When AI Meets the Web: Prompt Injection Risks in Third-Party AI Chatbot Plugins". In 8 of 17 plugins, used on about 8,000 websites, the plugins "fail to enforce the integrity of the conversation history transmitted in network requests". Attackers can forge histories, including fake system messages, and forgery raises unintended-behavior elicitation by 3 to 8x. The abstract does not name the underlying models or describe a signing mitigation. — [arXiv 2511.05797](https://arxiv.org/abs/2511.05797)

**History manipulation at the orchestration layer (2026)**
- Giovanny et al. (independent researchers, arXiv 2609.35308v3, 9 Oct 2026) use a threat model in which compromised middleware, a poisoned retrieval DB or a multi-agent memory store rewrites stored history. They evaluate a "Verified History" mitigation: the orchestrator stores a hash after each turn and restores the last clean state on mismatch. The authors note the hash must be keyed to be secure. Tested on Gemini-3.1 Flash-Lite, all tampered sessions were flagged, though partly by construction. The mitigation does nothing against prompt-embedded attacks (Protocols B/C), where adoption stayed at or above baseline. — [arXiv HTML](https://arxiv.org/html/2609.35308)
- A practitioner blog makes the same point: "chat history is user input", with forged refund approvals and forged identity verification as examples (secondary, non-academic). — [DEV Community](https://dev.to/y11t0/your-ai-agents-chat-history-is-user-input-fl6)

### Inferences
- The student team's observation (1), that chat APIs accept arbitrary client-supplied assistant turns, is established prior art. Microsoft CCA, DIA and the S&P 2026 plugin study all document it. The team should present it as a premise, not a contribution.
- No paper I found systematically measures **how guardrail classifiers (Llama Guard 3/4, Prompt Guard 2, ProtectAI deberta, NeMo, Azure Prompt Shields, OpenAI Moderation) treat assistant-role turns**: whether they scan them, whether forged turns change verdicts, and FPR when every turn is scanned. DIA tested OpenAI Moderation and a perplexity filter only, and found both fully bypassed. A guard-centric measurement of forged-history handling looks like an open measurement niche.
- The provenance defense in the student design covers only *API-level role forgery*. It cannot stop in-message faux dialogues (many-shot style), template-token injection in user text (DIA's WebUI variant, ChatBug format mismatch), or Crescendo-style attacks where every turn is genuine. The paper must state this boundary explicitly.

### Gaps
- I did not read the full S&P 2026 paper, so I do not know which LLM APIs it used or whether it proposes signing.
- I could not confirm the ChatBug venue (possibly AAAI 2025, unverified) or the full numbers for the message-overflow attack.
- I did not verify whether the current OpenAI, Anthropic or Google APIs reject or flag client-supplied assistant turns. To my knowledge none authenticate visible assistant text (see Q2 on reasoning-block signatures), but I found no authoritative provider documentation on this.

## Q2. Provenance and structure defenses: has anyone proposed HMAC-signing assistant turns at a proxy?

### Takeaway
The general idea, a keyed MAC or signature over conversation history verified outside the model, has been **proposed** (Microsoft CCA 2025) and **partially implemented in adjacent settings**. Adjacent implementations include a keyed-hash "verified history" orchestrator (Oct 2026), an HMAC-authenticated external reference monitor for agent instruction sources (Aug 2026), provider-signed response fields in BYOK agents (May 2026), and providers' existing MAC'd reasoning blocks (documented by Panfilov et al., Aug 2026). I found **no paper that (a) HMAC-signs assistant turns at a sidecar guard proxy and (b) uses the signature to selectively skip classifier scanning to control false-positive compounding.** That coupling of provenance with guard-cost and FPR is the most defensible novel angle, but the margin is thin. Expect reviewers to call the cryptography "obvious", as the Aug 2026 paper itself concedes for its own design.

### Cited Findings
**Model-level structural defenses (do not authenticate history)**
- OpenAI Instruction Hierarchy (Wallace et al., arXiv 2404.13208, 2024) trains models to prioritize system over user over tool instructions. It is implemented as fixed role labels, and SecAlign authors note there is no official implementation. — [arXiv](https://arxiv.org/pdf/2404.13208); [SecAlign paper](https://arxiv.org/pdf/2410.05451)
- StruQ (a structured front-end plus instruction tuning) and SecAlign (preference optimization) separate instruction from data channels. An independent evaluation found that the original ASRs relied mostly on a single injected payload ("Print exactly Hacked!"). — [BAIR blog](https://bair.berkeley.edu/blog/2025/04/11/prompt-injection-defense); [SecAlign](https://arxiv.org/pdf/2410.05451); [Critical evaluation, arXiv 2505.18333](https://arxiv.org/pdf/2505.18333)
- CaMeL (Debenedetti et al., arXiv 2503.18813, 2025) is a system-level design. It extracts control and data flow from the trusted query, and an interpreter tracks provenance and enforces capability policies. The later version reports 77% of AgentDojo tasks solved with provable security, against 84% undefended. — [arXiv](https://arxiv.org/abs/2503.18813)
- Implication: these defenses address *privilege across roles*. They assume the role labels themselves are honest. None of them authenticates that an `assistant` turn was really generated by the model.

**In-prompt "signing" (relies on the model to respect markers)**
- Signed-Prompt (Suo, arXiv 2401.07612, 2024) has authorized users "sign" sensitive instructions so the LLM can tell trusted sources apart. A review says this is keyword substitution with rare character strings, not a cryptographic signature in the traditional sense (secondary). — [arXiv](https://arxiv.org/pdf/2401.07612); [Moonlight review](https://www.themoonlight.io/en/review/signed-prompt-a-new-approach-to-prevent-prompt-injection-attacks-against-llm-integrated-applications)
- FATH (arXiv 2410.21492) is a test-time defense against indirect prompt injection. The model must emit hash-based authentication tags with its answer, and the paper cites RFC 2104 HMAC (snippet only, secondary). — [arXiv PDF](https://arxiv.org/pdf/2410.21492)

**Verification outside the model (closest prior art)**
- **Microsoft CCA (Mar 2025):** proposes that providers "sign conversation histories with a secret key" and validate them. This is a proposal only, with no evaluation. — [MSRC blog](https://www.microsoft.com/en-us/msrc/blog/2025/03/jailbreaking-is-mostly-simpler-than-you-think)
- **Leong, "Recognition Without Enforcement" (arXiv 2608.28502, 28 Aug 2026):** across 46 to 48 model endpoints, models recognize forged authority but still sometimes act on it. Prompt-layer defenses "don't generalize". An external reference monitor with "authenticated source routing" and capability-gated tools "deterministically rejected all tested forged, tampered, replayed, and unsigned requests". An adaptive red team found only a clock-skew implementation bug. The abstract does not say whether conversation history or assistant turns are signed. A search snippet attributed HMAC-SHA256-signed memory records, verified by middleware and dropped fail-closed, to an Aug 2026 preprint that appears to be this one, with the authors saying the contribution is the measurement rather than the primitive (snippet-level, secondary). — [arXiv 2608.28502](https://arxiv.org/abs/2608.28502)
- **Giovanny et al. "Verified History" (arXiv 2609.35308, Oct 2026):** the orchestrator hashes history per turn, needs a keyed hash, and restores on mismatch. It was evaluated on a single model only. — [arXiv HTML](https://arxiv.org/html/2609.35308)
- **Luo et al., "Rewriting the Response Path" (arXiv 2605.02187, May 2026):** a malicious BYOK relay rewrites responses. The "sign-c" defense has the provider authenticate execution-bearing fields and outgoing queries, and a local shim verifies them. It rejected all tampered responses with zero false rejections and 0.0167% latency overhead. It protects responses in transit, not replayed history. — [arXiv](https://arxiv.org/abs/2605.02187)
- **Panfilov et al., "Stealing Reasoning Traces from Proprietary LLM APIs" (arXiv 2608.09867, Aug 2026):** provider reasoning blocks are AEAD envelopes with a MAC, so clients can replay them without server storage. The providers appear to use a single global key, and no provider documented the scheme as of July 2026. The authors recommend "hashing the precise prompt and preceding conversation history into the MAC" to stop injection into fabricated contexts. **This shows providers already MAC some assistant-side content that clients replay, but not visible assistant text, and not bound to history.** — [arXiv HTML](https://arxiv.org/html/2608.09867v1)
- A 2026 paper on AP2 ("Signing the Transaction but Not the Decision") is another example of the pattern "signed artifact but unbound context" (title only, secondary). — [arXiv 2609.11757](https://arxiv.org/pdf/2609.11757)

### Inferences
- **Closest competitors to the student defense:** Microsoft CCA (idea), Giovanny et al. 2026 (keyed history hash at the orchestrator), Leong 2026 (HMAC external monitor), Panfilov et al. 2026 (MAC'd replayable assistant content plus a recommendation to bind it to history), and Luo et al. 2026 (provider-signed responses verified by a shim). A reviewer will likely say "HMAC over history at a trusted intermediary is known".
- **Defensible deltas** the team could claim, none of which I found in prior work:
  1. Using provenance to **reduce guard false positives**: skip-if-verified instead of scan-everything, with a quantified FPR-compounding model (e.g., session FPR ≈ 1 − (1 − p)^k for k scanned assistant turns) and empirical session-level FPR on benign multi-turn corpora.
  2. A **guard-centric measurement** of how ingress classifiers and moderation APIs handle assistant-role content and forged turns.
  3. **Binding design details**: per-turn MAC over (session id, turn index, role, content hash, previous MAC) to stop reordering, splicing, cross-session replay and truncation. Panfilov et al. show that unbound MACs enable context transplantation, so this is a concrete design point.
  4. The residual-risk analysis: what provenance cannot stop (genuine-turn Crescendo, in-message faux dialogues, template tokens in user text) and how the "short-turn plus previous-turn context" heuristic interacts with it.
- Adaptive attacks on the provenance scheme itself should include replaying a verified, genuinely relayed assistant turn that the attacker steered earlier. An attacker can first coax a borderline assistant turn through the proxy, which then signs it, and then rely on it being skipped later. This "launder through the proxy" attack is the obvious adaptive counter and must be evaluated.

### Gaps
- I could not confirm that the HMAC-SHA256 memory-signing snippet belongs to arXiv 2608.28502. I read only the abstract.
- I did not verify Spotlighting (Hines et al., Microsoft 2024) or role/segment-embedding papers in this session.
- I found no academic paper evaluating Microsoft's suggested history-signing at the API provider level.

## Q3. Multi-turn jailbreaks and multi-turn guard benchmarks

### Takeaway
Multi-turn attacks are mature: Crescendo, ActorAttack, X-Teaming, MHJ, NEXUS, and 2026 benchmarks MultiBreak and MT-JailBench. Single-turn defenses fail badly against them, with over 70% human multi-turn ASR on defenses that report single-digit ASR. Session-level guards are emerging (G-Guard, Defensive M2S, stateful risk accumulation), but benign-session FPR for guards is barely measured. The best evidence so far shows LlamaGuard 2 conversation-level FPR much higher than per-request FPR in one domain.

### Cited Findings
- **Crescendo** (Russinovich et al., Microsoft, arXiv 2404.01833) escalates gradually over turns, and Crescendomation automates it. The authors argue benchmarks focus on single-turn attacks. Their scoring used Perspective API and Azure Content Filters. — [arXiv PDF](https://arxiv.org/pdf/2404.01833)
- **MHJ** (Li et al., Scale AI and UC Berkeley, arXiv 2408.15221; NeurIPS 2024 Red Teaming GenAI workshop): multi-turn human jailbreaks reach over 70% ASR on HarmBench against defenses reporting single-digit ASR. The dataset has 2,912 prompts across 537 jailbreaks and is gated, CC BY-NC 4.0. — [arXiv](https://arxiv.org/abs/2408.15221v2); [Scale](https://scale.com/research/mhj)
- **ActorAttack / "Derail Yourself"** (arXiv 2410.10700) builds an actor network of semantically linked clues and claims to beat single- and multi-turn baselines including o1. It releases the SafeMTData safety dataset. — [arXiv](https://arxiv.org/abs/2410.10700v1)
- **X-Teaming** (Rahman et al., COLM 2025 per search; also listed on ICML 2025 virtual) uses multi-agent planner, attacker and verifier roles. It reports up to 98.1% ASR, and 96.2% on Claude 3.7 Sonnet. Its XGuard-Train dataset has about 30K multi-turn jailbreaks. — [arXiv](https://arxiv.org/pdf/2504.13203); [ICML listing](https://icml.cc/virtual/2025/49328)
- **NEXUS** (arXiv 2510.03417) reports 94.8% ASR on GPT-4o, 10.3 points above ActorAttack (snippet, secondary). **AJAR** combines Crescendo, ActorAttack and X-Teaming, and raises X-Teaming from 65.0% to 76.0% ASR on 200 HarmBench behaviors (secondary). — [arXiv 2510.03417](https://arxiv.org/pdf/2510.03417v2); [AJAR](https://sotaverified.org/papers/260110971)
- **Benchmarks:** SafeDialBench (arXiv 2502.11090) is a fine-grained multi-turn safety benchmark with diverse jailbreaks. MultiBreak (ICML 2026) has 10K+ adversarial conversations covering 2,600+ intents. MT-JailBench (arXiv 2605.11002) is modular and shows that judge and flow-control choices drive reported ASR. — [SafeDialBench](https://arxiv.org/pdf/2502.11090); [MultiBreak ICML 2026](https://icml.cc/virtual/2026/poster/63523); [MT-JailBench](https://arxiv.org/html/2605.11002v1)
- **Guards:** Llama Guard, Qwen3Guard and WildGuard are described as classifying queries and responses independently, without conversational context. G-Guard models full history. Defensive M2S (arXiv 2601.00454) trains guards on multi-turn conversations compressed to single turns. — [Defensive M2S](https://arxiv.org/pdf/2601.00454); [awesome-mllm-guardrails](https://github.com/ant-research/awesome-mllm-guardrails)
- **SoK: Evaluating Jailbreak Guardrails** (arXiv 2506.10597) identifies session-level guardrails as a category and asks how effective they are against sophisticated multi-turn attacks. — [arXiv](https://arxiv.org/pdf/2506.10597)
- **Benign-session FPR evidence:** "Stateful Guardrails for Multi-Turn LLM Systems" (arXiv 2607.19361) measures FPR on about 1,000 benign ShareGPT sessions, ranging from 0.000 to 0.200 depending on threshold, and warns that a lower threshold "amplifies false alarms on out-of-distribution chat traffic". GuardSet-X (arXiv 2506.19054) reports LlamaGuard 2 conversation FPR of 0.958 against 0.774 single-request FPR in finance. The table is hard to read, so verify before citing. — [Stateful Guardrails](https://arxiv.org/html/2607.19361); [GuardSet-X](https://arxiv.org/html/2506.19054v2)
- Evidence-attribution work (arXiv 2609.27773) argues that multi-turn benchmarks stop at conversation-level labels without locating which turn caused the failure. — [arXiv](https://arxiv.org/html/2609.27773v1)

### Inferences
- The team's observation (2), that scanning every assistant turn compounds FPR, is plausible and partly supported by the GuardSet-X single-request versus conversation gap and the Stateful Guardrails threshold sensitivity. I found **no paper that isolates FPR from scanning assistant-role turns specifically**. That is a measurable, novel sub-result.
- A proxy that skips verified assistant turns must still face Crescendo, ActorAttack and X-Teaming, where every assistant turn is genuine and therefore signed. Provenance gives no help there, so the paper needs a separate multi-turn detection evaluation, for example the short-turn-plus-context max-risk heuristic, on MHJ, SafeDialBench or MultiBreak.

### Gaps
- I did not verify RACE, Chain of Attack, MTSA, or the details of G-Guard in this session.
- I found no standard leaderboard of guard models on whole-conversation inputs.

## Q4. Automated adaptive red-teaming agents versus guardrails

### Takeaway
The security community now expects adaptive-attack evaluation. "The Attacker Moves Second" (USENIX Security 2026) broke 12 defenses, most at over 90% ASR, and Zhan et al. (NAACL Findings 2025) broke 8 indirect-prompt-injection defenses at over 50% ASR. A multi-turn LLM red-team agent (X-Teaming style) is a credible adaptive adversary. It must, however, be made *defense-aware*: it should know about the signing and skip rule and try to launder turns through the proxy, or reviewers will call the evaluation non-adaptive.

### Cited Findings
- **The Attacker Moves Second** (Nasr, Carlini, Tramèr et al., arXiv 2510.09023; USENIX Security 2026) uses tuned gradient, RL, random-search and human-guided attacks. It bypasses 12 defenses, most at over 90% ASR, including 100% ASR on Circuit Breakers (HarmBench) and 96% on MetaSecAlign (agentic). It argues static-benchmark evaluation is flawed. — [arXiv](https://arxiv.org/abs/2510.09023); [USENIX Sec '26](https://www.usenix.org/conference/usenixsecurity26/presentation/nasr)
- **Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents** (Zhan et al., NAACL Findings 2025) bypasses all 8 evaluated defenses with over 50% ASR. — [arXiv](https://arxiv.org/html/2503.00061v2); [ACL Anthology](https://preview.aclanthology.org/moar-dois/2025.findings-naacl.395)
- Leong 2026 ran an adaptive red team against its external HMAC monitor and found only an implementation flaw (clock skew), with no cryptographic bypass. This is a template for how to report adaptive evaluation of a signing defense. — [arXiv 2608.28502](https://arxiv.org/abs/2608.28502)
- MT-JailBench shows reported multi-turn ASR depends heavily on judge and flow-control choices, so the team must report the judge, retry and refusal policy. — [MT-JailBench](https://arxiv.org/html/2605.11002v1)

### Inferences
- An adaptive evaluation should include: (a) forged turns that imitate the proxy's MAC format, as a sanity check; (b) replay or splice of genuinely signed turns across sessions or positions; (c) laundering, where the attacker steers the model into producing a signed borderline turn and then exploits the skip; (d) multi-turn agent attacks (X-Teaming, Crescendo) with all-genuine turns; (e) in-message faux dialogues and template tokens; (f) short-turn splitting to beat the previous-turn-context heuristic, e.g. chaining three short turns; (g) GCG or TAP style optimization against the ingress classifier, with transfer.

### Gaps
- I did not fetch the PAIR, TAP, AutoDAN-Turbo or GCG-transfer-to-guard papers in this session. Cite them from primary sources when writing.

## Q5. What remains open, closest competitors, and venues

### Takeaway
The attack and the signing idea are both prior art. The open space is (i) a guard-centric measurement of assistant-turn and forged-history handling across commercial and open guards and APIs, (ii) provenance used as an FPR or latency control for guard proxies, with a formal binding design, and (iii) an honest adaptive, multi-turn evaluation showing what signing does and does not buy. Framed as a measurement-plus-defense paper with strong adaptive evaluation, this fits USENIX Security, CCS or SaTML. SaTML is probably the most realistic first target for a student team.

### Cited Findings
- **Closest competitors:** Microsoft CCA (history signing proposed) — [MSRC](https://www.microsoft.com/en-us/msrc/blog/2025/03/jailbreaking-is-mostly-simpler-than-you-think); DIA (forged history versus OpenAI Moderation and other defenses) — [arXiv](https://arxiv.org/html/2503.08195v1); Kaya et al. S&P 2026 (history-integrity failures in the wild) — [arXiv](https://arxiv.org/abs/2511.05797); Giovanny et al. 2026 (verified history) — [arXiv](https://arxiv.org/html/2609.35308); Leong 2026 (HMAC external monitor) — [arXiv](https://arxiv.org/abs/2608.28502); Panfilov et al. 2026 (MAC'd replayable reasoning, binding recommendation) — [arXiv](https://arxiv.org/html/2608.09867v1); Luo et al. 2026 (provider-signed responses) — [arXiv](https://arxiv.org/abs/2605.02187).
- **USENIX Security '27 (preliminary CFP):** an Open Science appendix is mandatory, and artifacts are strongly encouraged. An ethics appendix is recommended, and reviewers may request it. The body limit is 13 pages. Cycle 2 paper deadline is 26 Jan 2027, with registration on 19 Jan, and artifacts due 29 Jan 2027. The symposium runs 11–13 Aug 2027 in Denver. — [USENIX Sec '27 CFP](https://www.usenix.org/node/321195); [CFP PDF](https://www.usenix.org/sites/default/files/sec27_cfp-070826.pdf)
- Adaptive-attack evaluation is now expected at top venues, as "The Attacker Moves Second" at USENIX Security 2026 shows. — [USENIX Sec '26](https://www.usenix.org/conference/usenixsecurity26/presentation/nasr)

### Inferences
- **Concrete open gaps:**
  1. No systematic study of how deployed guards and moderation APIs (Llama Guard 3/4, Prompt Guard 2, ProtectAI, Azure Prompt Shields, OpenAI Moderation, NeMo) process `assistant`-role content and forged turns, or of how API providers differ in accepting them.
  2. No evaluated design that uses provenance to reduce guard FPR and latency (skip-verified), and no quantification of the FPR compounding it avoids on benign multi-turn corpora.
  3. No analysis of binding (turn index, chaining, session id) for replay or splice resistance in a guard proxy.
  4. No evaluation of laundering attacks, where the attacker induces a genuine signed turn and exploits trust in it.
  5. No combined evaluation of provenance with multi-turn detection against defense-aware LLM red-team agents.
- **Risks to novelty:** the cryptographic primitive is trivial, and Microsoft and the 2026 papers anticipate it. The contribution must be framed as measurement, systems trade-off and adaptive evaluation, not as "we invented signing". The Aug to Oct 2026 preprints (Leong; Giovanny et al.; Panfilov et al.) are very recent and must be cited and differentiated.
- **Venue fit (inference):** USENIX Security and CCS want a strong threat model, real-system measurement (several commercial APIs and guards), adaptive attacks, released artifacts and an ethics or disclosure discussion. Vendor disclosure is advisable if commercial guards are bypassed. IEEE S&P and NDSS have similar expectations, and NDSS is somewhat more systems-oriented. SaTML values ML-security rigor and accepts smaller-scale but careful studies, which makes it a good match for a student team. ACSAC is suited to practical deployment-focused defenses. Workshops such as DLSP or AISec are fallbacks. I did not verify current deadlines for CCS, S&P, NDSS, SaTML or ACSAC in this session.

### Gaps
- I did not fetch the CFPs for CCS 2027, S&P 2027, NDSS 2027, SaTML 2027 or ACSAC 2026/2027.
- There may be relevant work I missed in industry engineering blogs (e.g., guard-proxy vendors such as Lakera or Protect AI) describing signed or server-side history. I found none in my searches.
