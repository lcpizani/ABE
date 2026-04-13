# Model Development

ABE is not a single model — it is a multi-component AI system. This page documents each component, how it was built, and the tools used.

---

## System architecture overview

ABE combines three types of AI:

| Component | Type | What it does |
|---|---|---|
| OpenClaw + Claude | Agentic LLM | Understands the farmer's question, routes to the right skill, interprets outputs, composes responses |
| gno (BM25 + vector) | Retrieval-augmented generation (RAG) | Searches ~41 documents and synthesizes sourced answers |
| CornCNN2 (PyTorch) | Computer vision | Classifies corn leaf disease from a photo |

These three components work together: Claude drives the conversation and decides which tool to use; gno retrieves document content when needed; CornCNN2 handles image analysis when a photo is sent.

---

## Component 1 — Conversational agent (OpenClaw + Claude)

### Model type

Multi-modal agentic AI. The core LLM is **Claude Sonnet** (Anthropic). The agent runtime is **[OpenClaw](https://openclaw.bot)**, which manages the Telegram interface, tool invocation, cron scheduling, and memory file access.

### Key features

| Feature | Description |
|---|---|
| Skill routing | Claude reads `AGENTS.md` to determine which skill to invoke for each question type |
| Memory | Farmer profiles stored as Markdown files; read at conversation start and updated in real time |
| Tool use | Claude calls Python scripts via shell and parses JSON output |
| Grounding | Every financial output is constrained to named sources — Claude is instructed never to generate a figure not backed by the database or an API |
| Proactive behavior | Five cron-driven heartbeat tasks run autonomously and message farmers without being asked |
| Persona | Defined in `SOUL.md` and `AGENTS.md` — warm, direct, source-citing, never estimating |

### Development process

ABE's behavior was developed through iterative prompt engineering across three files:

- **`SOUL.md`** — defines who ABE is: voice, hard limits, what it will never say or do
- **`AGENTS.md`** — operational rules: skill routing logic, memory protocol, response structure, banned phrases, conversation constraints
- **`HEARTBEAT.md`** — autonomous task definitions: what each cron job does, what thresholds trigger a message, what the message says

Each file was refined through test conversations, the 50-question benchmark, and the 5 full profile runs documented in [How We Evaluated ABE](evaluation.md).

### Tools used

| Tool | Purpose |
|---|---|
| [Anthropic Claude Sonnet](https://anthropic.com) | Core LLM |
| [OpenClaw](https://openclaw.bot) | Agent runtime, Telegram integration, cron scheduling |
| Python 3 | Skill scripts, data processing, API clients |
| SQLite | Structured benchmark data storage |

---

## Component 2 — Knowledge base (gno RAG)

### Model type

Retrieval-augmented generation using hybrid search: **BM25** (keyword matching) combined with **vector embeddings** (semantic similarity), re-ranked and returned as context to Claude.

### Key features

| Feature | Description |
|---|---|
| Hybrid retrieval | BM25 handles exact keyword matches; vector search handles semantic intent. Both are combined for better coverage than either alone |
| Local operation | gno runs entirely on the local machine — no external embedding API required |
| Auto-indexing | The gno daemon watches `knowledge/` and re-indexes automatically when files are added or updated |
| Citation support | Each retrieved chunk carries its source document name, which ABE cites inline |
| Synthesis mode | `gno ask` synthesizes a grounded answer from multiple chunks, not just a ranked list |

### Development process

1. Identified the authoritative sources for each topic ABE covers (ISU Extension, USDA, Iowa IADD, university extension programs)
2. Downloaded official PDFs and converted web pages to plain text
3. Organized documents in `knowledge/` with consistent naming
4. Started the gno daemon; it indexed all documents automatically
5. Tested retrieval quality with representative queries for each topic area
6. Iteratively refined query phrasing in `SKILL.md` files based on retrieval results

### Tools used

| Tool | Purpose |
|---|---|
| [gno](https://github.com/gmickel/gno) v0.30.0 | Document indexing, BM25 + vector search, answer synthesis |
| Qwen3-Embedding-0.6B (quantized) | Embedding model used by gno |
| ~41 PDF and TXT documents | Source corpus |

---

## Component 3 — Corn disease detector (CornCNN2)

### Origins and attribution

The CornCNN2 model was not built from scratch by SAU Hive Mind. It was developed in the previous academic year by a team of St. Ambrose University students as part of a separate research project. They trained a convolutional neural network to identify corn leaf diseases from photographs and generously shared their trained model with our team.

We integrated their work into ABE as the corn disease detection skill, wrapped it with a confidence threshold and a plain-language output layer, and connected it to the knowledge base so that after any diagnosis, ABE automatically retrieves management and treatment guidance for the identified disease.

All credit for the model architecture, training methodology, and trained weights belongs to the original SAU team.

### Model type

Computer vision — convolutional neural network (CNN) built in PyTorch, trained on visual image data of corn leaves from the [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset).

### Training data

The model was trained on photographs of corn leaves, each labeled with the disease present or marked as healthy. The images were sourced from the PlantVillage Dataset — a peer-reviewed, publicly available collection of labeled plant disease images developed by Penn State and published under open license.

Each image is a close-up photograph of a single corn leaf under controlled lighting conditions. The dataset captures the visual patterns characteristic of each disease: the cigar-shaped lesions of northern blight, the pustule clusters of common rust, the rectangular grey lesions of grey leaf spot, and so on.

Images were preprocessed using standard torchvision transforms: resized to a consistent input dimension, normalized, and augmented with flips and rotations to improve generalization.

### Supported classes

| Class | Pathogen | Visual characteristic |
|---|---|---|
| Northern Corn Leaf Blight | *Exserohilum turcicum* (fungal) | Long, cigar-shaped tan lesions with wavy margins |
| Southern Corn Leaf Blight | *Cochliobolus heterostrophus* (fungal) | Smaller tan to brown lesions with distinct borders |
| Common Rust | *Puccinia sorghi* (fungal) | Small, round to oval pustules — brick red to brown |
| Grey Leaf Spot | *Cercospora zeae-maydis* (fungal) | Rectangular grey-tan lesions parallel to leaf veins |
| Lethal Necrosis | Viral complex | Widespread necrosis from leaf tip inward; brown coloring |
| Streak Virus | *Maize streak virus* | Pale yellow streaks running the length of the leaf |
| Healthy | — | No visible lesions or discoloration |

### Key features

| Feature | Description |
|---|---|
| Multi-class classification | Identifies 6 disease classes and healthy (7 classes total) |
| Confidence threshold | Returns a diagnosis only if model confidence ≥ 60%; otherwise requests a clearer photo |
| Iowa-relevant scope | All six diseases are present or threatening in Iowa corn production |
| Integrated follow-up | After any diagnosis, ABE automatically queries the knowledge base for management and treatment guidance |

### Integration into ABE

The model is loaded and run via `skills/corn-disease-detector/scripts/corn_disease.py`. The entry point accepts an image path, runs inference using `predict.py`, evaluates the confidence score against the 60% threshold, and returns a plain-language diagnosis string to ABE.

If confidence is below threshold, ABE asks the farmer for a clearer photo rather than reporting an uncertain result.

After a confirmed diagnosis, ABE:
1. Runs 14-day weather history for the farmer's county
2. Connects the weather conditions (humidity, temperature) to disease favorability
3. Searches the knowledge base for management guidance specific to the identified disease

### Tools used

| Tool | Purpose |
|---|---|
| [PyTorch](https://pytorch.org) | Model architecture and inference |
| [torchvision](https://pytorch.org/vision/) | Image preprocessing and transforms |
| [Pillow (PIL)](https://python-pillow.org) | Image loading |
| PlantVillage Dataset | Training and validation data |

### Evaluation metrics

The CornCNN2 model was evaluated by the original SAU team using:

- **Overall accuracy** — percentage of test images classified correctly
- **Per-class precision** — of images predicted as class X, how many actually were X
- **Per-class recall** — of images that are class X, how many did the model identify
- **Confusion matrix** — to identify which disease pairs are most likely to be confused

For ABE-level evaluation (skill invocation and output quality), see [How We Evaluated ABE](evaluation.md).

---

## Scalability and adaptability

| Dimension | Current state | Path to scale |
|---|---|---|
| Additional crops | Corn and soybeans | Add training data and knowledge documents for other crops |
| Additional diseases | 6 corn disease classes | Retrain or fine-tune with soybean disease images |
| Additional states | Iowa only | Replace ISU/Iowa datasets with equivalent state extension data |
| More farmers | Single-machine deployment | Move to VPS; OpenClaw supports multi-tenant deployment |
| Additional programs | Current FSA/Iowa set | Drop new PDFs into `knowledge/`; gno re-indexes automatically |
