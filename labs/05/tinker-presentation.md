---
marp: true
theme: default
paginate: true
math: katex
---

# Fine-Tuning Large Language Models
## Introduction to Tinker

Scientific Programming 2025

---

# Part 0: Fundamentals

Understanding the basics before we dive in

---

# What are Large Language Models?

- **Pre-trained** neural networks trained on massive text corpora
- Learn language patterns, knowledge, and reasoning capabilities
- Examples: GPT-5, Claude, Llama, Qwen
- Trained on billions/trillions of tokens
- General-purpose but not specialized

---

# Pre-Training vs Fine-Tuning

**Pre-Training:**
- Train from scratch on massive datasets
- Extremely expensive (millions of dollars)
- Results in a "base model" with general capabilities

**Fine-Tuning:**
- Start with a pre-trained model
- Train on smaller, task-specific dataset
- Much cheaper and faster
- Customizes model behavior for your use case

---

# Why Fine-Tune?

**Common Use Cases:**
- Adapt to specific domains (medical, legal, code)
- Follow specific output formats or styles
- Improve performance on narrow tasks
- Align with human preferences
- Reduce hallucinations in specific contexts
- Learn from specialized datasets too small for pre-training

---

# Types of Fine-Tuning

**Full Fine-Tuning:**
- Update all model parameters
- Expensive: requires storing full model copy
- Best performance on large datasets

**Parameter-Efficient Fine-Tuning (PEFT):**
- Update only a small subset of parameters
- Much more memory efficient
- Often equivalent performance
- **LoRA** is the most popular PEFT method

---

# What is LoRA?

**Low-Rank Adaptation:**
- Instead of updating all weights, add small "adapter" matrices
- Adapters have much fewer parameters (typically 0.1-1% of model)
- Original model weights stay frozen
- Only train the adapter weights

**Key Insight:**
- Most fine-tuning updates are "low rank"
- Can approximate updates with smaller matrices

---

# LoRA: Visual Intuition

```
Original Model:        W (frozen, e.g. 4096×4096 = 16M params)
LoRA Adapters:         A×B (trainable, e.g. 4096×32 × 32×4096 = 262K params)

Forward Pass:          output = W·x + A·B·x
```

**Benefits:**
- 16M params → 262K trainable params (98% reduction)
- Faster training, less memory
- Can swap adapters for different tasks
- Preserves base model knowledge better

---

# LoRA Advantages

- Equivalent to full fine-tuning for RL
- Equivalent for small supervised datasets
- Better preservation of base model capabilities
- Much more cost-effective

---

# LoRA Disadvantages

- Worse performance on large supervised datasets
- Must use much higher learning rates (20-100x)
- Cannot update vocabulary or architecture

---

# Supervised Learning Recap

**Supervised Learning (SL):**
- Learn from labeled examples: (input, expected output)
- Loss function: cross-entropy (predict next token)
- Example: "Translate to French: Hello" → "Bonjour"

---

# Gradients and Optimization

**What is a gradient?**
- Direction and magnitude to adjust each parameter to reduce loss
- Think of it like a compass pointing downhill
- If loss is a mountain, gradient points toward the valley

**How training works:**
1. Compute gradient of loss w.r.t. every weight
2. Update each weight by taking a small step to reduce loss
3. Step size controlled by **learning rate**
4. Backward pass (gradients) + forward pass (loss) = training loop core

---

# SL for LLMs

**For LLMs:**
- Input: prompt tokens
- Output: completion tokens
- Loss: how well model predicts the completion

---

# What is Reinforcement Learning?

**RL Fundamentals:**
- Agent interacts with environment
- Takes actions, receives rewards
- Goal: maximize cumulative reward

**For LLMs:**
- **Policy**: the language model (generates text)
- **Action**: choosing next token
- **Reward**: feedback on quality of generated text
- **Environment**: the task/problem being solved

---

# RL Terminology

**Policy (π):**
- The model that generates text
- Maps states → probability distribution over actions

**Reward (R):**
- Feedback signal (e.g., +1 for correct answer, 0 for wrong)
- Can be programmatic (verifiable) or learned (from humans)

**Environment:**
- Provides observations and rewards
- Examples: math problems, coding challenges, dialogue

---

# What is RLHF?

**Reinforcement Learning from Human Feedback:**
- Train model using human preferences instead of labels
- Humans compare multiple outputs: "A is better than B"
- More natural than writing explicit labels
- How ChatGPT and Claude are aligned

**Two-Stage Process:**
1. Train a reward model on human preferences
2. Use RL to optimize the language model against that reward

---

# Preference Learning Basics

**Instead of:** "The correct answer is X"
**We have:** "Response A is better than Response B"

**Advantages:**
- Easier for humans to provide
- Captures subjective quality (helpfulness, safety)
- Works when there's no single "right answer"

**Challenge:**
- Need to convert preferences into a training signal
- DPO and RLHF are two approaches

---

# Training Data Requirements

**Supervised Learning:**
- Prompt/completion pairs (1K-100K examples)
- Quality over quantity
- Format: conversational or raw text

**Reinforcement Learning:**
- Prompts only (model generates completions)
- Reward function or preference data (10K-1M prompts)
- Multiple completions per prompt

---

# Hyperparameters: Learning Rate

**Learning Rate:**
- How much to update weights each step
- Most important hyperparameter
- Too high: unstable training
- Too low: slow learning or no improvement

---

# Hyperparameters: Batch & Rank

**Batch Size:**
- Number of examples per update
- Larger: more stable, slower
- Smaller: faster, noisier

**LoRA Rank:**
- Size of adapter matrices
- Default: 32, can go up to 128+

---

# Common Fine-Tuning Pitfalls

1. **Wrong learning rate** (especially with LoRA)
2. **Overfitting** on small datasets
3. **Forgetting** base model capabilities
4. **Poor data quality** or formatting
5. **Not enough training steps**
6. **Ignoring evaluation metrics**
7. **Off-policy RL** without importance sampling

---

# Key Takeaways So Far

- Fine-tuning adapts pre-trained models to your tasks
- LoRA is efficient but requires higher learning rates
- Supervised learning uses labeled examples
- RL optimizes for rewards/preferences
- RLHF aligns models with human values
- Data quality and hyperparameters are critical

---

# Part 1: Introduction to Tinker

What is Tinker and why should you care?

---

# The Fundamental Problem

**When you fine-tune modern LLMs (like Llama-3 or Qwen), you typically need:**
- Multiple GPUs (8B models barely fit on one GPU)
- Distributed training setup (FSDP, DeepSpeed, etc.)
- Infrastructure management (networking, checkpointing, fault tolerance)

**This is expensive, complex, and time-consuming!**

---

# What is Tinker?

**Tinker is a hosted API that handles all of that**

You don't run GPUs locally—you send training requests to Tinker's service, and it handles the distributed compute.

**Philosophy:**
- You write simple CPU code
- Tinker runs it on distributed GPUs
- Full control over training loop
- No infrastructure headaches

---

# The Key Split

```
Your CPU machine (local)          Tinker's GPU cluster (remote)
━━━━━━━━━━━━━━━━━━━━━━            ━━━━━━━━━━━━━━━━━━━━━━━━━━
• Training loop logic             • Forward passes
• Data loading/batching            • Backward passes
• Reward computation               • Gradient updates
• Sampling rollouts                • LoRA parameter storage
• Metrics tracking                 • Model serving for sampling
```

**Your job:** Write the training orchestration
**Tinker's job:** Execute the heavy GPU work

---

# Division of Responsibilities

**You write:**
- Training loop logic
- Data preparation
- Loss computation
- Sampling/evaluation

**Tinker handles:**
- Distributed GPU orchestration
- Model parallelism and sharding
- Hardware failure recovery
- Efficient batching and scheduling
- Checkpoint management

---

# Current Features

**Supported:**
- LoRA fine-tuning (not full fine-tuning yet)
- Qwen and Llama model series
- Models from 1B to 405B parameters
- Mixture-of-Experts (MoE) models
- Supervised learning and RL
- Async/non-blocking API

**Not Yet Supported:**
- Full fine-tuning
- Other model architectures (coming soon)
- Multi-modal models

---

# Core API Overview

**Main Operations:**

```python
# Training step
forward_backward(data, loss_fn)  # Compute gradients
optim_step()                      # Update weights

# Sampling
sample(prompts, params)           # Generate text

# Checkpointing
save_weights_for_sampler()        # Save for inference
save_state() / load_state()       # Full training state
```

---

# Model Lineup

**Available Model Series:**
- **Llama**: 1B, 3B, 8B, 70B, 405B
- **Qwen**: 1.5B, 7B, 14B, 32B, 72B, 235B (MoE)

**Model Types:**
- 🐙 Base models (raw pre-trained)
- ⚡ Instruction-tuned models
- 🔀 Mixture-of-Experts (cost-effective for large models)

**Recommendation:** Start with Llama-3.1-8B or Qwen2.5-7B for experiments

---

# Tinker's Value Proposition

**For Researchers:**
- Experiment with novel training algorithms
- Full transparency and control
- Fast iteration on ideas
- No infrastructure management

**For Developers:**
- Production-quality training infrastructure
- Reliable and fault-tolerant
- Scales from 8B to 405B models
- Cost-effective (especially MoE models)

---

# Part 2: Getting Started

Let's write some code

---

# Installation

```bash
# Install Tinker SDK
pip install tinker

# Install Tinker Cookbook (examples)
git clone https://github.com/tinker-ai/tinker-cookbook
cd tinker-cookbook
pip install -e .

# Set API key
export TINKER_API_KEY=your_key_here
```

**Optional:**
```bash
pip install -e ".[envs]"  # For RL environment dependencies
```

---

# API Clients

**Two main clients:**

```python
from tinker import ServiceClient, TrainingClient

# Service client: manage training sessions
service = ServiceClient()

# Training client: actual training operations
training = TrainingClient(
    model_name="meta-llama/Llama-3.1-8B",
    lora_config={"rank": 32}
)
```

**ServiceClient:** Create sessions, list models
**TrainingClient:** Train and sample

---

# Data Format: Datum

```python
from tinker.types import Datum

datum = Datum(
    tokens=[1234, 5678, 9012],      # Token IDs
    targets=[5678, 9012, 3456],     # Next token (shifted)
    weights=[0.0, 0.0, 1.0]         # Loss weight per position
)
```

**Key Insight:**
- `weights=0.0`: Don't train on this token (prompt)
- `weights=1.0`: Train on this token (completion)
- Allows training only on outputs, not inputs

---

# Basic Workflow

```python
# 1. Create clients
training = TrainingClient(model_name="meta-llama/Llama-3.1-8B")

# 2. Prepare data
data = [datum1, datum2, ...]

# 3. Training step
training.forward_backward(data, loss_fn="cross_entropy")
training.optim_step()

# 4. Sample
response = training.sample(prompts=["Hello"], params={...})
```

---

# The Data Pipeline

**How chat becomes training data**

When fine-tuning on conversations, you need to answer:
1. Which tokens should the model learn to predict?
2. Which tokens should be ignored during training?

**Example:**
- ✅ Learn to predict: "The answer is 4."
- ❌ NOT learn to predict: "User: What's 2+2?"

---

# How Renderers Work

The renderer converts a conversation into two tensors:

**1. tokens:** The full sequence
```
[BOS, "User:", "What's", "2", "+", "2", "?",
 "Assistant:", "The", "answer", "is", "4", "."]
```

**2. weights:** Per-token loss weights
```
[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
```

Where:
- `weight=1` → "train on this token"
- `weight=0` → "ignore this token"

---

# The TrainOnWhat Enum

**Controls which tokens to train on:**

```python
class TrainOnWhat(StrEnum):
    # Only final response
    LAST_ASSISTANT_MESSAGE = "last_assistant_message"

    # All assistant turns (most common)
    ALL_ASSISTANT_MESSAGES = "all_assistant_messages"

    # Everything (including user)
    ALL_MESSAGES = "all_messages"

    # No masking
    ALL_TOKENS = "all_tokens"
```

**Most common:** `ALL_ASSISTANT_MESSAGES` - train the model to predict what the assistant says, not what the user says.

---

# The Complete Data Flow

```
Raw conversation                    Renderer                 Training datum
━━━━━━━━━━━━━━━━                   ━━━━━━━━               ━━━━━━━━━━━━━━
[                                                          tinker.Datum(
  {"role": "user",        ─────→   tokens:                  model_input=[...],
   "content": "Hi"},                [15, 23, 42, ...]
                                                            loss_fn_inputs={
  {"role": "assistant",             weights:                 "target_tokens": [...],
   "content": "Hello!"}  ─────→    [0, 0, 1, 1, ...]        "weights": [0,0,1,1,...]
]                                                           }
                                                          )
```

---

# Why Different Models Need Different Renderers

Different models use different chat templates:

**Llama-3:**
```
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
Hello<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

**Qwen:**
```
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
```

**The cookbook automatically picks the right renderer for your model!**

```python
renderer_name = model_info.get_recommended_renderer_name(config.model_name)
renderer = renderers.get_renderer(renderer_name, tokenizer)
```

---

# Futures Pattern

**All operations are non-blocking:**

```python
# Submit request, get future
future = await training.sample_async(prompts, params)

# Later: wait for result
result = await future

# Or combine: double await
result = await (await training.sample_async(prompts, params))
```

**Why?** Overlap requests to maximize GPU utilization

---

# Part 3: Supervised Learning

Training on labeled examples

---

# Anatomy of a Training Script

Let's walk through the simplest possible example: `sl_loop.py` (156 lines)

This shows you exactly what happens in a training loop, step by step.

---

# Step 1: Configuration

```python
@chz.chz
class Config:
    model_name: str = "meta-llama/Llama-3.1-8B"
    batch_size: int = 128
    learning_rate: float = 1e-4
    lora_rank: int = 32
    train_on_what: renderers.TrainOnWhat = ALL_ASSISTANT_MESSAGES
```

The `@chz.chz` decorator makes this a CLI-configurable dataclass.

**Override from command line:**
```bash
python sl_loop.py model_name=Qwen/Qwen3-8B learning_rate=5e-5
```

---

# Step 2: Setup

```python
# Get tokenizer and renderer
tokenizer = get_tokenizer(config.model_name)
renderer = renderers.get_renderer(renderer_name, tokenizer)

# Load dataset
dataset = datasets.load_dataset("HuggingFaceH4/no_robots")
train_dataset = dataset["train"]
```

**Key concept:** The renderer converts chat conversations into token sequences with per-token loss weights.

---

# Step 3: Create Training Client

```python
service_client = tinker.ServiceClient(base_url=config.base_url)

training_client = service_client.create_lora_training_client(
    base_model=config.model_name,
    rank=config.lora_rank
)
```

This connects to Tinker's API and:
- Allocates GPU resources
- Loads the base model
- Initializes LoRA adapters (low-rank matrices)

---

# Step 4: The Training Loop

```python
for batch_idx in range(start_batch, n_train_batches):
    # 1. Prepare batch
    batch_rows = train_dataset.select(range(batch_start, batch_end))
    batch = [
        conversation_to_datum(
            row["messages"],      # Raw chat messages
            renderer,             # Converts to tokens + weights
            config.max_length,
            config.train_on_what,
        )
        for row in batch_rows
    ]

    # 2. Forward + backward pass
    fwd_bwd_future = training_client.forward_backward(
        batch, loss_fn="cross_entropy"
    )

    # 3. Optimizer step
    optim_step_future = training_client.optim_step(adam_params)

    # 4. Wait for results
    fwd_bwd_result = fwd_bwd_future.result()
    _optim_result = optim_step_future.result()
```

---

# The Async Pattern

**Notice:** Submit both `forward_backward` and `optim_step` immediately, THEN wait for results.

```python
# Submit both operations (non-blocking)
fwd_bwd_future = training_client.forward_backward(batch, loss_fn="cross_entropy")
optim_step_future = training_client.optim_step(adam_params)

# Then wait (blocking)
fwd_bwd_result = fwd_bwd_future.result()
optim_result = optim_step_future.result()
```

**Why?** This keeps the GPU busy—no idle time between operations!

---

# SL Workflow in Tinker

1. **Prepare dataset** of (prompt, completion) pairs
2. **Render** to token format with appropriate weights
3. **Training loop:**
   - Batch your data
   - Call `forward_backward` with cross-entropy loss
   - Call `optim_step` to update weights
4. **Evaluate** periodically on validation set
5. **Save checkpoint** when done

---

# Loss Functions: Cross-Entropy

**Cross-entropy** is standard for supervised learning:

```python
training.forward_backward(
    data=batch,
    loss_fn="cross_entropy"
)
```

**What it does:**
- Compares model's predicted token probabilities to targets
- Higher loss when model is uncertain or wrong
- Lower loss when model confidently predicts correct token

---

# Example: Pig Latin Translation

**Task:** Train model to translate English to Pig Latin

**Dataset:**
- "hello" → "ellohay"
- "world" → "orldway"

**Process:**
1. Convert to messages format
2. Render with weights (0 for prompt, 1 for completion)
3. Train with cross-entropy loss
4. Sample to test: "translate: goodbye" → "oodbyegay"

---

# Example: NoRobots Dataset

**NoRobots:** 10K high-quality instruction-following examples

```python
from datasets import load_dataset

dataset = load_dataset("HuggingFaceH4/no_robots")

# Each example has:
# - messages: list of {"role": ..., "content": ...}
# - category: task type
```

**Common workflow:**
- Filter/sample subset
- Render to Datum format
- Train for ~100-500 steps
- Evaluate on held-out set

---

# Hyperparameter Formulas

**Learning rate formula:**

$$LR = lr_{base} \cdot M_{LoRA} \cdot \left(\frac{2000}{H}\right)^P$$

- $lr_{base} = 5 \times 10^{-5}$
- $M_{LoRA} = 10$ (for LoRA, 1 for full FT)
- $H$ = hidden dimension of model
- $P$ = 0.0775 (Qwen) or 0.781 (Llama)

**Utility:**
```python
from tinker_cookbook.utils import get_lr
lr = get_lr("meta-llama/Llama-3.1-8B")
```

---

# Why LoRA Needs Higher Learning Rates

**Key insight:** LoRA adapters are smaller matrices

- Must make larger relative updates to have same effect
- Typical multiplier: 20-100x higher than full fine-tuning
- Formula accounts for this with $M_{LoRA} = 10$

**Don't guess!** Use provided utilities or formula

---

# Batch Size Considerations

**Smaller batches often better:**
- Less data required to see improvement
- More gradient updates for same data
- Recommended: 128 examples per batch

**Trade-off:**
- Larger batches: more stable, but slower feedback
- Smaller batches: noisier, but faster iteration

**Rule of thumb:** Aim for 100+ training steps

---

# Prompt Distillation

**Goal:** Train student model to match teacher with long prompt

**Process:**
1. Teacher uses long prompt: "You are an expert classifier..."
2. Collect teacher outputs on queries
3. Train student on (query, teacher_output) without prompt
4. Student "internalizes" the prompt instructions

**Use case:** Reduce latency and cost by removing prompt

---

# Evaluation Strategies

**During Training:**
- Track loss on validation set
- Sample outputs to check quality
- Compute task-specific metrics

**After Training:**
- Benchmark on held-out test set
- A/B test against base model
- Check for forgetting (eval on general tasks)

**Tinker supports:** Inline evaluators during training

---

# Part 4: Reinforcement Learning

Training with rewards instead of labels

---

# RL Overview

**Two main flavors:**

**RLVR:** Reinforcement Learning with Verifiable Rewards
- Programmatic reward functions
- Example: math problem correctness, code execution

**RLHF:** Reinforcement Learning from Human Feedback
- Learned reward models
- Example: helpfulness, safety preferences

---

# RL Use Cases

1. **Specialist models:** Excel at narrow tasks (math, coding)
2. **Post-training research:** Alignment, safety, reasoning
3. **RL algorithms research:** Novel training methods

**When to use RL:**
- Hard to provide labeled examples
- Easy to verify correctness
- Want to optimize for subjective quality

---

# RL Environments

**Environment interface:**

```python
class Env:
    def initial_observation(self) -> list[int]:
        """Return initial prompt tokens"""

    def step(self, action: int) -> tuple[list[int], float, bool]:
        """
        Args: action (token ID)
        Returns: (observation, reward, done)
        """
```

**Token-level interface** (not strings)

---

# Reward Functions

**GSM8K math example:**

```python
def compute_reward(answer: str) -> float:
    predicted = extract_number(answer)
    reward = 1.0 if predicted == correct else 0.0
    if has_boxed_answer(answer):
        reward += 0.1
    return reward
```

**Key idea:** +1 for correct, +0.1 bonus for proper formatting

---

# Example: GSM8K

**GSM8K:** Grade school math word problems

**RL Approach:**
1. Sample completions for each question
2. Extract answer from completion
3. Check correctness: +1 if right, 0 if wrong
4. Use RL to increase probability of correct completions

**Better than SL when:**
- Multiple valid solution paths
- Want to reward reasoning process, not just final answer

---

# Training Loop Components

1. **Dataset:** Batch of prompts/environments
2. **Rollout:** Sample completions from current policy
3. **Reward:** Compute rewards for completions
4. **Advantages:** Compute advantage estimates
5. **Training:** Update policy with importance sampling loss
6. **Repeat**

---

# Rollout Collection

**Generate multiple completions per prompt:**

```python
# Sample completions
responses = training.sample(prompts, {"temperature": 1.0})

# Score and create training data
rewards = [compute_reward(r) for r in responses]
data = create_rl_data(responses, rewards, advantages)
```

---

# Importance Sampling Loss

**Problem:** Sampler policy ≠ learner policy (off-policy)

**Solution:** Importance sampling with ratio clipping

```python
training.forward_backward(
    data=batch,
    loss_fn="importance_sampling"
)
```

**What it does:**
- Corrects for distribution mismatch
- Prevents large policy updates
- More stable than vanilla policy gradient

---

# RL Hyperparameters

**Learning rate:** Same formula as SL

**Batch and group sizes:**
- `batch_size`: Number of prompts
- `group_size`: Completions per prompt
- Total rollouts: `batch_size × group_size`

**Scale LR with batch size:**
$$LR \propto \sqrt{\text{batch\_size}}$$

---

# KL Divergence Monitoring

**KL divergence:** Measure of policy change

```
KL(sampler || learner) < 0.01  # Good
KL(sampler || learner) > 0.1   # Too much drift
```

**Why it matters:**
- Large KL = learner very different from sampler
- Off-policy corrections break down
- Need to update sampler policy more frequently

**Best practice:** Track KL, resample if too high

---

# Group-Based Training

**Key insight:** Multiple completions per prompt

**Advantages:**
- Better advantage estimates (compare within group)
- Filter out constant-reward groups (no signal)
- More sample-efficient

---

# Group Training Example

**Setup:**
- 128 prompts × 4 completions = 512 rollouts
- Compare rewards within each group of 4
- Update policy to favor higher-reward completions

---

# Multi-Step Environments

**Beyond single response:**

```python
class TwentyQuestionsEnv(Env):
    def step(self, action):
        if is_question(action):
            obs = self.answer_question()
            return obs, 0.0, False  # No reward yet
        else:
            reward = 1.0 if correct_guess() else -1.0
            return [], reward, True  # Episode ends
```

**Use cases:** Dialogue, games, interactive tasks

---

# Math RL Environment

**Real `MathEnv` from cookbook:**

```python
class MathEnv(ProblemEnv):
    def get_question(self) -> str:
        return self.problem + " Write in \\boxed{}."

    def check_format(self, sample: str) -> bool:
        return has_boxed(sample)

    def check_answer(self, sample: str) -> bool:
        return safe_grade(extract_boxed(sample), self.answer)
```

---

# The Math RL Flow

**1. Environment gives problem**
```
"What's 15 * 23? Write your answer in \boxed{} format."
```

**2. Model generates response**
```
"Let me calculate: 15 * 23 = 345. Therefore \boxed{345}"
```

**3. Environment grades it**
```python
check_format() → True (has \boxed{})
check_answer() → True (345 is correct)
reward = +1.0
```

**4. Training uses reward to update model**
```
Model learns: "Correct answers in proper format = high reward"
```

---

# SL vs RL: Key Differences

| Aspect          | Supervised Learning               | Reinforcement Learning                 |
|-----------------|-----------------------------------|----------------------------------------|
| Data source     | Human-written examples            | Model generates its own data           |
| Learning signal | Cross-entropy loss on gold labels | Reward signal from environment         |
| Exploration     | None (follows human examples)     | Generates diverse attempts             |
| Optimization    | Match human responses             | Maximize expected reward               |
| Use case        | Imitate human behavior            | Solve tasks with clear success metrics |

---

# Group-Based Training (GRPO)

**One clever trick:** Group Reward Preference Optimization

```python
# Generate multiple attempts for same problem
Problem: "What's 15 * 23?"

Group of 16 attempts:
- Attempt 1: "\boxed{345}" → reward = +1.0
- Attempt 2: "\boxed{345}" → reward = +1.0
- Attempt 3: "\boxed{340}" → reward = -1.0
- ... (13 more attempts)

# Center rewards within the group
# This helps the model learn relative quality
advantages = rewards - mean(rewards)

# Update model: increase probability of high-advantage attempts
```

**More sample-efficient than standard RL!**

---

# Part 5: Preferences & RLHF

Learning from human feedback

---

# Direct Preference Optimization (DPO)

**Alternative to RLHF:** Train directly on preferences

**Approach:**
- Given pairs: (prompt, chosen_response, rejected_response)
- Maximize probability of chosen over rejected
- No separate reward model needed

**Simpler than RLHF but can be less powerful**

---

# DPO Loss Function

```python
training.forward_backward(
    data=preference_pairs,
    loss_fn="dpo",
    dpo_beta=0.1  # Temperature parameter
)
```

**Key parameter:** `dpo_beta`
- Higher: more conservative (stay close to base model)
- Lower: more aggressive (fit preferences more)
- Typical: 0.1 - 0.5

---

# Preference Datasets

**Common datasets:**
- Anthropic HHH (Helpful, Honest, Harmless)
- HelpSteer3
- UltraFeedback

**Format:**
```python
{
    "prompt": "How do I bake a cake?",
    "chosen": "Here's a simple recipe...",
    "rejected": "I don't know."
}
```

---

# RLHF: Two-Stage Process

**Stage 1: Train Reward Model**
- Use preference pairs
- Train model to predict which response is better
- Output: scalar reward for any completion

**Stage 2: RL with Reward Model**
- Sample completions
- Score with reward model
- Use RL to maximize reward

---

# Training Preference Models

```python
# Compare two completions
reward_a = model(prompt + completion_a)
reward_b = model(prompt + completion_b)

# Loss: Bradley-Terry model
prob_a_better = sigmoid(reward_a - reward_b)
loss = -log(prob_a_better)  # If A was preferred
```

**Result:** Model that scores completion quality

---

# RL with Learned Rewards

**Combine RL + reward model:**

1. Sample completions from policy
2. Score each with reward model
3. Use scores as rewards in RL
4. Update policy to maximize reward

**Challenge:** Reward model can be exploited
**Solution:** Add KL penalty to stay near base model

---

# Part 6: The Tinker Cookbook

Understanding the recipe structure

---

# What is the Tinker Cookbook?

**Pre-built examples for 7 major use cases:**

The cookbook is organized into recipe families, each demonstrating a different training approach.

**Think of it as:**
- Example code you can run immediately
- Templates to customize for your tasks
- Best practices for different scenarios

---

# Recipe Categories

**1. Chat SFT** - Supervised fine-tuning on chat datasets (Tulu3, NoRobots)

**2. Math RL** - Mathematical reasoning with verifiable rewards (GSM8K, MATH)

**3. Preference Learning** - RLHF and DPO from human preferences

---

# More Recipe Categories

**4. Tool Use** (`tool_use/`)
- Teaching models to use retrieval tools (RAG)
- Reward: Correctness with retrieved context

**5. Prompt Distillation** (`prompt_distillation/`)
- Internalize prompts into model parameters

---

# Additional Recipe Types

**6. Multi-Agent** (`multiplayer_rl/`)
- Multi-turn games between agents
- Games: Guess-the-number, twenty-questions, tic-tac-toe

**7. Distillation** (`distillation/`)
- Transfer knowledge from teacher to student
- Methods: On-policy and off-policy

---

# "Basic" vs "Loop" Scripts

**`sl_basic.py` / `rl_basic.py` (Production)**
- Full-featured: checkpointing, metrics, W&B
- Start here for real projects

**`sl_loop.py` / `rl_loop.py` (Educational)**
- Minimal ~150 line training loops
- Direct API usage to understand internals

---

# Standard Recipe Structure

Every recipe follows this pattern:

```
recipes/some_recipe/
├── README.md              # What it does, how to run it
├── train.py              # Main training script
├── {recipe}_env.py       # Environment definition (for RL)
├── {recipe}_dataset.py   # Dataset builder
└── config.py             # Configuration dataclasses (optional)
```

**Consistent structure** makes it easy to navigate and customize.

---

# Running Any Recipe

The general pattern:

```bash
python -m tinker_cookbook.recipes.RECIPE.train \
    model_name=MODEL \
    learning_rate=LR \
    batch_size=BS \
    log_path=/tmp/my-run \
    wandb_project=my-project  # optional
```

**Override any config field from CLI thanks to `chz`:**

```bash
# Override learning rate
python -m tinker_cookbook.recipes.math_rl.train learning_rate=1e-4

# Override multiple fields
python -m tinker_cookbook.recipes.chat_sl.train \
    model_name=Qwen/Qwen3-8B \
    batch_size=256 \
    lora_rank=128
```

---

# Key Features All Recipes Share

**Built-in production features:**

1. **Automatic checkpointing** (every N steps)
2. **Resume from interruptions** (just rerun with same `log_path`)
3. **Metrics logging** (`metrics.jsonl` + optional W&B)
4. **Evaluation during training** (configurable with `eval_every`)
5. **HTML transcripts** for qualitative review

**You get all of this for free!**

---

# Example: Running Math RL

```bash
# Basic run
python -m tinker_cookbook.recipes.math_rl.train \
    env=gsm8k \
    model_name="meta-llama/Llama-3.1-8B-Instruct" \
    group_size=64

# With custom hyperparameters
python -m tinker_cookbook.recipes.math_rl.train \
    env=gsm8k \
    model_name="meta-llama/Llama-3.1-8B-Instruct" \
    group_size=32 \
    learning_rate=5e-4 \
    batch_size=64 \
    log_path=/tmp/my-math-experiment \
    wandb_project=my-rl-experiments
```

**The recipe handles everything else!**

---

# How to Choose a Recipe

**Based on your use case:**

| Goal | Recipe |
|------|--------|
| Fine-tune chat model | `chat_sl` |
| Improve math reasoning | `math_rl` |
| Learn from preferences | `preference` |
| Build custom RL task | Study `math_rl`, create your own env |
| Reduce prompt length | `prompt_distillation` |
| Multi-agent interactions | `multiplayer_rl` |
| Distill large → small model | `distillation` |

**Pro tip:** Start with the closest recipe and customize.

---

# Part 7: Practical Considerations

Tips for successful fine-tuning

---

# Saving Checkpoints

**Two checkpoint types:**

```python
# For inference only (lightweight)
uri = training.save_weights_for_sampler()

# Full state (for resuming training)
uri = training.save_state()

# Later: load
training.load_state(uri)
```

**Persistent URIs:** `tinker://...` format

---

# Best Practices

1. **Start small:** Test on small model/dataset first
2. **Use default hyperparameters** from utilities
3. **Monitor metrics:** Loss, accuracy, KL, entropy
4. **Evaluate frequently:** Don't just look at loss
5. **Save checkpoints:** Things can go wrong
6. **Check data quality:** Garbage in, garbage out
7. **Compare to baseline:** Is fine-tuning helping?

---

# Common Mistakes (1/2)

1. **Wrong learning rate** (too low or forgot LoRA multiplier)
2. **Training too long** (overfitting)
3. **Ignoring KL divergence** in RL

---

# Common Mistakes (2/2)

4. **Poor data formatting** (wrong weights, missing tokens)
5. **Not evaluating** on diverse examples
6. **Forgetting to update sampler** in off-policy RL

---

# Summary (1/2)

**What we learned:**

**Part 0: Fundamentals**
- LLMs, pre-training vs fine-tuning, LoRA, SL vs RL basics

**Part 1: Tinker Architecture**
- The fundamental problem: distributed training is hard
- Tinker's solution: CPU orchestration + GPU service
- Clean API with full control over training loops

---

# Summary (2/2)

**Part 2-3: Supervised Learning**
- Anatomy of a training script (`sl_loop.py`)
- The critical role of renderers (tokens + weights)
- Async patterns for GPU efficiency

---

# Summary (3/3)

**Part 4: Reinforcement Learning**
- RL environments, rewards, and GRPO

**Part 5: Preferences & RLHF**
- DPO and RLHF with reward models

**Part 6: The Cookbook**
- 7 recipe families with production and educational scripts

---

# Key Takeaways

1. **Tinker makes distributed training simple** - focus on algorithms, not infrastructure
2. **Renderers are critical** - they control what the model learns
3. **Start with recipes** - pre-built examples for common scenarios
4. **LoRA is powerful** - but needs higher learning rates (use the formulas!)
5. **RL opens new possibilities** - optimize for rewards, not just labels
6. **The cookbook has you covered** - chat, math, preferences, tools, distillation, multi-agent

**Bottom line:** You can fine-tune 8B-405B models without managing GPUs!

---

# Next Steps

**Getting Started:**
1. **Install Tinker** and clone the cookbook
2. **Run `sl_loop.py`** to understand the basics
3. **Pick a recipe** that matches your use case
4. **Start with small models** (8B) for fast iteration
5. **Monitor metrics** and evaluate frequently

**Resources:**
- Tinker Cookbook: `github.com/tinker-ai/tinker-cookbook`
- Documentation: `docs.tinker.ai`
- API Reference: `tinker.ai/docs`

**Pro tip:** Read `sl_loop.py` and `rl_loop.py` first - they're only ~150 lines each!

---

# Questions?

Thank you for your attention!

**Remember:**
- Fine-tuning is powerful but requires careful hyperparameter tuning
- Start simple, iterate based on metrics
- Tinker makes infrastructure easy so you can focus on your task
- The cookbook provides working examples for every major use case

**Let's make some fine-tuned models!**
