# Hi, I'm Rick Zhang 👋

**Building auditable memory systems for agents that act in the physical world.**

I care about one question: *when an agent does something, can you show me exactly why?* Not a confidence score, not a summary — the actual observations, the evidence, and the reasoning that led there.

Currently building **[Moqi · 默契](https://github.com/shlihy/moqi-home)** — an auditable memory and learning framework for smart-home agents.

---

## 🔬 What I'm working on

**Moqi** is a framework where a home agent learns from what it can actually observe, and keeps the evidence behind every conclusion inspectable.

The interesting part isn't the learning — it's the *accountability*:

- **Observations are evidence, not truth.** A sensor event doesn't prove a human pressed a button. The framework tracks attribution and keeps unknowns labeled as unknown.
- **Learning ≠ permission.** Four verified occurrences can seed a candidate habit; they never authorize execution. The safety boundary is enforced by deterministic code, never by model confidence.
- **Understanding is editable.** A resident can correct a habit, restrict an action, or roll back to an earlier understanding — without erasing what actually happened.
- **Shadow mode by default.** The integrated runtime observes and proposes, but Home Assistant owns device selection and the final dispatch boundary.

The design stance throughout: *when in doubt, say so*. Every layer that can't prove something reports it as unverified rather than guessing.

**Stack:** Python 3.11+ · SQLite (WAL) · Home Assistant custom integration · Pyodide for browser-based playground · TypeScript/Node tooling

---

## 🧭 Areas I'm exploring

- **Agent memory architecture** — episodic vs. semantic memory, evidence-weighted confidence, exposure-based forgetting, dormancy cycles
- **Typed language models** — routing natural language to a narrow local model (EdgeJev) while keeping numeric, temporal, and safety decisions in deterministic code
- **Home automation as a safety problem** — occupancy inference, nighttime silence budgets, state reconciliation, reserved command IDs
- **Privacy-preserving inference** — local-first models, background summarization with token/cache accounting, deidentified exports
- **Auditable systems** — Git-backed memory history, explicit rollback, reproducible acceptance ledgers

---

## 🛠️ Things I like working with

| | |
|---|---|
| **Languages** | Python, TypeScript, SQL, Bash |
| **Systems** | SQLite internals, Home Assistant, Docker, Git, Linux |
| **Practices** | Test-driven development, reproducible acceptance criteria, writing docs that stay honest |

---

## 💭 Currently learning

- **SQLite concurrency internals** — WAL mode, shared-memory file locking, and why the same code can pass on one filesystem and fail on another
- **Local model deployment** — quantizing small language models for on-device inference with acceptable latency
- **Rust** — currently working through ownership and the borrow checker

---

## 🤝 Open to

- **Collaborating** on auditable agent memory, home automation safety, or local-first inference
- **Discussing** design trade-offs in agent systems — especially where determinism and model capability conflict
- **Contributing** — issues and pull requests are welcome on the projects below

---

## 📦 Projects

| Project | Description |
|---|---|
| **[moqi-home](https://github.com/shlihy/moqi-home)** | Auditable memory and learning framework for smart-home agents · MIT |
| **[Rick-Zhang](https://github.com/shlihy/Rick-Zhang)** | This profile |

---

## 📫 Reach me

- **GitHub:** [@shlihy](https://github.com/shlihy)
- **Email:** [shlihy@gmail.com](mailto:shlihy@gmail.com)

---

<div align="center">
  <sub>Built with care. Every claim here is scoped to what was actually verified.</sub>
</div>
