# Tinker Presentation Script

## Slide 1: Title Slide
"Welcome everyone! Today we're going to dive into fine-tuning large language models using a tool called Tinker. This is part of our Scientific Programming course for 2025. By the end of this presentation, you'll understand how to customize and improve LLMs for your specific use cases without needing to manage complex GPU infrastructure."

---

## Slide 2: Part 0 - Fundamentals
"Before we jump into Tinker itself, we need to make sure we're all on the same page about the fundamentals. We'll cover what LLMs actually are, the difference between pre-training and fine-tuning, and the basics of both supervised and reinforcement learning. Think of this as building our foundation."

---

## Slide 3: What are Large Language Models?
"So, what exactly are large language models? They're pre-trained neural networks that have been trained on massive amounts of text data - we're talking billions or even trillions of tokens. Through this training, they learn language patterns, world knowledge, and reasoning capabilities. You're probably familiar with examples like GPT-4, Claude, Llama, and Qwen. The key thing to understand is that these models are general-purpose - they know a lot about many things, but they're not specialized for any particular task."

---

## Slide 4: Pre-Training vs Fine-Tuning
"Let's clarify the difference between pre-training and fine-tuning, because this is fundamental to what we'll be doing. Pre-training is when you train a model from scratch on massive datasets. This is extremely expensive - we're talking millions of dollars in compute costs. The result is what we call a 'base model' with general capabilities.

Fine-tuning, on the other hand, starts with one of these pre-trained models and trains it further on a smaller, task-specific dataset. This is much cheaper and faster than pre-training. The goal is to customize the model's behavior for your specific use case, whether that's medical diagnosis, legal document analysis, or anything else you can imagine."

---

## Slide 5: Why Fine-Tune?
"You might be wondering - why bother with fine-tuning at all? Well, there are several compelling use cases. First, you can adapt models to specific domains like medical or legal text where specialized knowledge is crucial. You can also teach models to follow specific output formats or styles consistently. Fine-tuning can improve performance on narrow tasks, align models with human preferences, and even reduce hallucinations in specific contexts. It's especially useful when you have specialized datasets that are too small for pre-training but perfect for teaching a model new behaviors."

---

## Slide 6: Types of Fine-Tuning
"There are two main approaches to fine-tuning. Full fine-tuning updates all the model's parameters. This is expensive because you need to store a complete copy of the model, but it generally gives you the best performance when you have large datasets.

The alternative is Parameter-Efficient Fine-Tuning, or PEFT. With PEFT, you only update a small subset of parameters, which is much more memory efficient. Surprisingly, you often get equivalent performance to full fine-tuning! The most popular PEFT method is called LoRA, which we'll talk about next."

---

## Slide 7: What is LoRA?
"LoRA stands for Low-Rank Adaptation, and it's a clever technique. Instead of updating all the weights in your model, LoRA adds small 'adapter' matrices. These adapters have far fewer parameters - typically just 0.1 to 1 percent of the original model size. The original model weights stay frozen; you only train these adapter weights.

The key insight here is that most fine-tuning updates are 'low rank' - meaning they can be approximated well using smaller matrices. It's a bit like how you can compress an image without losing much quality."

---

## Slide 8: LoRA - Visual Intuition
"Let me give you some concrete numbers to make this intuitive. Imagine you have a weight matrix in your model that's 4096 by 4096 - that's 16 million parameters. With LoRA, instead of updating this entire matrix, you add two smaller matrices: one that's 4096 by 32, and another that's 32 by 4096. Together, these adapter matrices only have 262 thousand parameters - that's a 98% reduction!

During the forward pass, you compute the output as the original weights times your input, plus the product of these adapter matrices times your input. The benefits are huge: you need much less memory, training is faster, you can swap different adapters for different tasks, and you preserve the base model's knowledge better."

---

## Slide 9: LoRA Advantages
"Let's talk about when LoRA really shines. For reinforcement learning, LoRA is equivalent to full fine-tuning - you get the same results with far less compute. The same is true for small supervised datasets. LoRA also does a better job of preserving the base model's capabilities, which means you're less likely to experience 'catastrophic forgetting' where the model loses knowledge it had before. And of course, it's much more cost-effective overall."

---

## Slide 10: LoRA Disadvantages
"But LoRA isn't perfect. On large supervised datasets, it tends to perform worse than full fine-tuning. There's also a tricky aspect: you must use much higher learning rates - typically 20 to 100 times higher than you would for full fine-tuning. This can be counterintuitive and requires some care. Finally, LoRA can't update the model's vocabulary or architecture - you're working within the constraints of the original model."

---

## Slide 11: Supervised Learning Recap
"Let's do a quick recap of supervised learning, since that's one of the main ways we'll use Tinker. In supervised learning, you learn from labeled examples - pairs of inputs and expected outputs. For language models, the loss function is typically cross-entropy, which measures how well the model predicts the next token.

For example, you might have 'Translate to French: Hello' as input and 'Bonjour' as the expected output. The model learns to produce the correct completion given the prompt."

---

## Slide 12: Gradients and Optimization
"Now, how does the model actually learn from the loss? This is where gradients come in. A gradient tells you the direction and magnitude to adjust each model parameter to reduce the loss. Think of it like a compass pointing downhill - if the loss is a mountain, the gradient points toward the valley.

During training, we compute the gradient of the loss with respect to every weight in the model. Then we update each weight by taking a small step in the direction that reduces the loss. This process is called gradient descent. The size of that step is controlled by the learning rate, which we'll discuss later. This backward pass that computes gradients is paired with the forward pass that computes the loss - together they form the core of the training loop."

---

## Slide 13: SL for LLMs
"When we apply supervised learning to LLMs specifically, here's how it works: your input is the prompt tokens, your output is the completion tokens, and the loss measures how well the model predicts those completion tokens. It's conceptually simple, but powerful - this is how most instruction-following models are created."

---

## Slide 14: What is Reinforcement Learning?
"Now let's talk about reinforcement learning, which is a bit different. In RL, an agent interacts with an environment, takes actions, and receives rewards. The goal is to maximize the cumulative reward over time.

For language models, we can map these concepts: the policy is the language model itself, which generates text. Each action is choosing the next token. The reward is feedback on the quality of the generated text. And the environment is whatever task or problem you're trying to solve."

---

## Slide 15: RL Terminology
"Let me clarify some RL terminology. The policy - denoted by pi - is the model that generates text. It maps states to probability distributions over actions. The reward, denoted R, is the feedback signal. This could be a simple +1 for a correct answer and 0 for wrong, or something more complex. Rewards can be programmatic and verifiable, like checking if a math answer is correct, or learned from human preferences. The environment provides observations and rewards - examples include math problems, coding challenges, or dialogue scenarios."

---

## Slide 16: What is RLHF?
"RLHF - Reinforcement Learning from Human Feedback - is how modern conversational AI like ChatGPT and Claude are aligned with human values. Instead of providing explicit labels, humans compare multiple outputs and say 'A is better than B.' This is much more natural than writing explicit labels for subjective qualities like helpfulness or safety.

RLHF is a two-stage process: first, you train a reward model on human preferences. Then you use reinforcement learning to optimize the language model against that reward. We'll dive deeper into this later."

---

## Slide 17: Preference Learning Basics
"The core idea of preference learning is elegant. Instead of having to write 'The correct answer is X,' you just say 'Response A is better than Response B.' This has several advantages: it's easier for humans to provide, it captures subjective quality that's hard to define explicitly, and it works when there's no single 'right answer.'

The challenge, of course, is converting these preferences into a training signal. DPO and RLHF are two different approaches to solving this problem."

---

## Slide 18: Training Data Requirements
"The data requirements differ significantly between supervised learning and reinforcement learning. For supervised learning, you need prompt and completion pairs. Quality matters more than quantity here - typical datasets range from 1,000 to 100,000 examples. The format can be conversational messages or raw text.

For reinforcement learning, you just need prompts - the model generates its own completions. You also need a reward function or preference data. RL usually needs more data, typically 10,000 to 1 million prompts. The advantage is you can generate multiple completions per prompt to learn from."

---

## Slide 19: Hyperparameters - Learning Rate
"Let's talk about the most important hyperparameter: learning rate. This controls how much you update the weights at each training step. If it's too high, training becomes unstable and you might diverge. If it's too low, learning is painfully slow or might not improve at all. Getting this right is crucial for successful fine-tuning."

---

## Slide 20: Hyperparameters - Batch & Rank
"Batch size is the number of examples you process before updating the model. Larger batches are more stable but slower and require more data. Smaller batches give faster iterations but are noisier.

LoRA rank is the size of those adapter matrices we talked about earlier. The default is 32, but you can go up to 128 or higher if you need more capacity."

---

## Slide 21: Common Fine-Tuning Pitfalls
"Let me warn you about some common mistakes people make. First is using the wrong learning rate - this is especially tricky with LoRA. Second is overfitting on small datasets. Third is forgetting - where the model loses its base capabilities. Poor data quality or formatting will ruin your results. Not training for enough steps is also common. Many people ignore evaluation metrics and just watch the loss. And finally, in off-policy RL, you must handle importance sampling correctly or your training won't work."

---

## Slide 22: Key Takeaways So Far
"Let's pause and review what we've covered. Fine-tuning adapts pre-trained models to your specific tasks. LoRA is efficient but requires higher learning rates - don't forget this! Supervised learning uses labeled examples, while RL optimizes for rewards or preferences. RLHF aligns models with human values. And remember: data quality and hyperparameters are absolutely critical to success."

---

## Slide 23: Part 1 - Introduction to Tinker
"Now that we have our foundations, let's talk about Tinker. What is it, and why should you care?"

---

## Slide 24: The Fundamental Problem
"Here's the problem Tinker solves. When you fine-tune modern LLMs like Llama-3 or Qwen, even the 8 billion parameter versions barely fit on one GPU. You typically need multiple GPUs and a distributed training setup using frameworks like FSDP or DeepSpeed. You also need to manage infrastructure - networking, checkpointing, fault tolerance, all of it. This is expensive, complex, and time-consuming. Most researchers and developers shouldn't have to deal with this complexity."

---

## Slide 25: What is Tinker?
"Tinker is a hosted API that handles all of that distributed training infrastructure for you. You don't run GPUs locally - you send training requests to Tinker's service, and it handles the distributed compute. The philosophy is simple: you write simple CPU code to orchestrate your training loop, Tinker runs the heavy GPU work, you get full control over the training process, and you have no infrastructure headaches."

---

## Slide 26: The Key Split
"Let me break down how responsibilities are split between your machine and Tinker's cluster. On your local CPU machine, you handle the training loop logic, data loading and batching, reward computation, sampling rollouts, and metrics tracking.

Tinker's GPU cluster handles the forward passes, backward passes, gradient updates, LoRA parameter storage, and model serving for sampling. Your job is to write the training orchestration. Tinker's job is to execute the heavy GPU work. It's a clean separation of concerns."

---

## Slide 27: Division of Responsibilities
"To be more specific: you write the training loop logic, data preparation, loss computation, and sampling and evaluation code. Tinker handles distributed GPU orchestration, model parallelism and sharding, hardware failure recovery, efficient batching and scheduling, and checkpoint management. This lets you focus on the algorithm and the data rather than fighting with infrastructure."

---

## Slide 28: Current Features
"What does Tinker currently support? It supports LoRA fine-tuning - not full fine-tuning yet, but that's coming. It works with Qwen and Llama model series, ranging from 1 billion to 405 billion parameters. It supports Mixture-of-Experts models, which are very cost-effective. Both supervised learning and RL are supported, and the API is async and non-blocking for maximum efficiency.

What's not yet supported? Full fine-tuning, other model architectures like Mistral or GPT, and multi-modal models. But these are all on the roadmap."

---

## Slide 29: Core API Overview
"The core API is straightforward. For training, you call forward_backward with your data and a loss function - this computes gradients. Then you call optim_step to update the weights. For sampling, you call sample with your prompts and generation parameters. For checkpointing, you can save_weights_for_sampler for inference, or save_state and load_state for full training state. That's really the essence of it."

---

## Slide 30: Model Lineup
"Tinker offers an extensive lineup of models. For Llama, you have 1B, 3B, 8B, 70B, and 405B parameter versions. For Qwen, you have 1.5B, 7B, 14B, 32B, 72B, and a 235B parameter Mixture-of-Experts model. Each series has base models - the raw pre-trained versions - and instruction-tuned models that already follow instructions. The MoE models are particularly interesting because they're cost-effective for their size. My recommendation is to start with Llama-3.1-8B or Qwen2.5-7B for initial experiments."

---

## Slide 31: Tinker's Value Proposition
"Why use Tinker? For researchers, it lets you experiment with novel training algorithms without worrying about infrastructure. You get full transparency and control over the training process, fast iteration on ideas, and no infrastructure management. For developers, you get production-quality training infrastructure that's reliable and fault-tolerant. It scales from 8 billion to 405 billion parameter models seamlessly, and it's cost-effective, especially with those MoE models."

---

## Slide 32: Part 2 - Getting Started
"Alright, enough theory. Let's write some code!"

---

## Slide 33: Installation
"Installation is straightforward. First, install the Tinker SDK with pip install tinker. Then clone the Tinker Cookbook repository, which has tons of examples. Set your API key as an environment variable. Optionally, if you want to use the RL environment dependencies, install those with the envs extra. That's it - you're ready to go."

---

## Slide 34: API Clients
"Tinker has two main client types. The ServiceClient manages training sessions - creating them, listing available models, that sort of thing. The TrainingClient is what you use for actual training operations - forward passes, sampling, all the heavy lifting. You create a TrainingClient by specifying the model name and LoRA configuration. It's a clean API design."

---

## Slide 35: Data Format - Datum
"Let's talk about the Datum type, which is how you represent training data. A Datum has three fields: tokens, which are the token IDs; targets, which are the next tokens you want the model to predict; and weights, which control the loss at each position. Here's the key insight: when the weight is 0.0, you don't train on that token - this is typically your prompt. When the weight is 1.0, you do train on it - this is typically the completion. This allows you to train only on outputs, not inputs."

---

## Slide 36: Basic Workflow
"Here's a basic workflow. First, create your training client with a model name. Second, prepare your data as a list of Datum objects. Third, run a training step by calling forward_backward with your data and the loss function - typically cross-entropy - then call optim_step. Fourth, sample from the model to see what it's learned. It's that simple at its core."

---

## Slide 37: The Data Pipeline
"Now I want to talk about what I consider the most important concept in fine-tuning: how chat conversations become training data. When you fine-tune on conversations, you need to answer two critical questions: which tokens should the model learn to predict, and which tokens should be ignored during training? For example, you typically want the model to learn to predict the assistant's response, but not learn to predict what the user said."

---

## Slide 38: How Renderers Work
"This is where renderers come in. A renderer converts a conversation into two tensors. First is the tokens tensor - the full sequence including special tokens like the beginning of sequence, user prefix, the actual message, assistant prefix, and the response. Second is the weights tensor, which has a weight per token. Where the weight is 0, we ignore that token during training. Where it's 1, we train on it. This is how we control what the model learns."

---

## Slide 39: The TrainOnWhat Enum
"Tinker provides a TrainOnWhat enum that controls which tokens to train on. LAST_ASSISTANT_MESSAGE trains only on the final response. ALL_ASSISTANT_MESSAGES trains on all assistant turns - this is the most common setting. ALL_MESSAGES trains on everything, including what the user said. And ALL_TOKENS does no masking at all. Most of the time, you want ALL_ASSISTANT_MESSAGES - you want the model to learn what the assistant should say, not what the user says."

---

## Slide 40: The Complete Data Flow
"Let me show you the complete flow. You start with a raw conversation - messages with roles and content. The renderer converts this into tokens and weights. Finally, this becomes a Tinker Datum with model inputs and loss function inputs including target tokens and weights. This pipeline is crucial to understand because if you get it wrong, you'll be training on the wrong parts of your data."

---

## Slide 41: Why Different Models Need Different Renderers
"Different models use different chat templates. Llama-3 uses special tokens like begin_of_text, start_header_id, user, end_header_id, and so on. Qwen uses a different format with im_start and im_end tokens. The good news is the cookbook automatically picks the right renderer for your model based on the model name. You don't have to worry about these details."

---

## Slide 42: Futures Pattern
"An important pattern to understand is that all Tinker operations are non-blocking. When you call sample_async, you get back a future immediately. Later, you can await that future to get the result. Or you can do both at once with a double await. Why is this important? It lets you overlap requests to maximize GPU utilization. You can submit multiple operations and let them run in parallel."

---

## Slide 43: Part 3 - Supervised Learning
"Now let's dive into supervised learning - training on labeled examples."

---

## Slide 44: Anatomy of a Training Script
"I want to walk you through the simplest possible example: sl_loop.py, which is only 156 lines. This shows you exactly what happens in a training loop, step by step, with no abstraction hiding what's really going on."

---

## Slide 45: Step 1 - Configuration
"First, you define a configuration using the chz decorator, which makes it a CLI-configurable dataclass. You specify things like the model name, batch size, learning rate, LoRA rank, and what to train on. The beauty is you can override any of these from the command line when you run the script. For example, you could say model_name equals Qwen slash Qwen3-8B to use a different model."

---

## Slide 46: Step 2 - Setup
"Next, you set up your tokenizer and renderer. You get the tokenizer for your model, then get the appropriate renderer - the cookbook handles picking the right one. Then you load your dataset - in this case, the no_robots dataset from Hugging Face, which has high-quality instruction-following examples. The renderer will convert these conversations into the proper token format with loss weights."

---

## Slide 47: Step 3 - Create Training Client
"You create a ServiceClient, which manages your connection to Tinker. Then you use it to create a LoRA training client, specifying the base model and the LoRA rank. At this point, Tinker allocates GPU resources, loads the base model, and initializes those LoRA adapter matrices we talked about. You're ready to train."

---

## Slide 48: Step 4 - The Training Loop
"Here's the core training loop. For each batch, you first prepare the batch by selecting rows from your dataset and converting each conversation to a Datum using the renderer. Second, you submit a forward and backward pass with the cross-entropy loss function. Third, you submit an optimizer step to update the weights. Fourth, you wait for the results. Notice that you submit both operations before waiting - this keeps the GPU busy."

---

## Slide 49: The Async Pattern
"Let me emphasize this async pattern because it's important. You submit forward_backward and get a future. You immediately submit optim_step and get another future. Only then do you wait for the results. This is much better than submitting, waiting, submitting, waiting - that would leave the GPU idle between operations. This pattern maximizes GPU utilization."

---

## Slide 50: SL Workflow in Tinker
"To summarize the supervised learning workflow: prepare your dataset of prompt-completion pairs, render them to token format with appropriate weights, run your training loop where you batch your data, call forward_backward with cross-entropy loss, and call optim_step to update weights. Evaluate periodically on a validation set, and save checkpoints when you're done."

---

## Slide 51: Loss Functions - Cross-Entropy
"Cross-entropy is the standard loss function for supervised learning. It compares the model's predicted token probabilities to the targets. The loss is high when the model is uncertain or wrong, and low when the model confidently predicts the correct token. It's simple but effective."

---

## Slide 52: Example - Pig Latin Translation
"Here's a fun example: training a model to translate English to Pig Latin. Your dataset would be pairs like 'hello' maps to 'ellohay', 'world' maps to 'orldway'. You convert these to messages format, render them with weights - zero for the prompt, one for the completion. Train with cross-entropy loss, and then sample to test. If you ask it to translate 'goodbye', it should produce 'oodbyegay'. Simple but illustrative."

---

## Slide 53: Example - NoRobots Dataset
"A more realistic example is the NoRobots dataset, which has 10,000 high-quality instruction-following examples. Each example has messages - a list of role and content pairs - and a category for the task type. A common workflow is to filter or sample a subset of the data, render to Datum format, train for 100 to 500 steps, and evaluate on a held-out set."

---

## Slide 54: Hyperparameter Formulas
"Now, getting the learning rate right is crucial. There's actually a formula for this. The learning rate equals a base learning rate times a LoRA multiplier times a scaling factor based on the model's hidden dimension. The base learning rate is 5 times 10 to the minus 5. The LoRA multiplier is 10 for LoRA fine-tuning, 1 for full fine-tuning. H is the hidden dimension, and P is a model-specific exponent - 0.0775 for Qwen, 0.781 for Llama.

The good news is you don't have to calculate this yourself - there's a utility function get_lr that does it for you."

---

## Slide 55: Why LoRA Needs Higher Learning Rates
"Why does LoRA need higher learning rates? Remember, LoRA adapters are much smaller matrices. They must make larger relative updates to have the same effect as updating the full model. The typical multiplier is 20 to 100 times higher than full fine-tuning. The formula accounts for this with that LoRA multiplier of 10. Don't guess - use the provided utilities or formula."

---

## Slide 56: Batch Size Considerations
"Interestingly, smaller batches are often better. They require less data to see improvement, and you get more gradient updates for the same amount of data. The recommendation is 128 examples per batch. There's a trade-off: larger batches are more stable but give slower feedback. Smaller batches are noisier but let you iterate faster. A good rule of thumb is to aim for at least 100 training steps."

---

## Slide 57: Prompt Distillation
"Here's a cool application: prompt distillation. The goal is to train a student model to match a teacher model that uses a long prompt. The teacher uses a long prompt like 'You are an expert classifier with PhD-level knowledge...' - you collect the teacher's outputs on various queries. Then you train the student on just the query and the teacher's output, without that long prompt. The student 'internalizes' the prompt instructions into its parameters. This reduces latency and cost by eliminating the long prompt."

---

## Slide 58: Evaluation Strategies
"You should evaluate both during training and after. During training, track loss on a validation set, sample outputs to check quality qualitatively, and compute task-specific metrics like accuracy or F1 score. After training, benchmark on a held-out test set, run A/B tests against the base model to see if fine-tuning actually helped, and check for forgetting by evaluating on general tasks. Tinker supports inline evaluators that run during training."

---

## Slide 59: Part 4 - Reinforcement Learning
"Now let's shift gears to reinforcement learning - training with rewards instead of labels."

---

## Slide 60: RL Overview
"There are two main flavors of RL. RLVR - Reinforcement Learning with Verifiable Rewards - uses programmatic reward functions. For example, you can check if a math answer is correct or if code executes successfully. RLHF - Reinforcement Learning from Human Feedback - uses learned reward models based on human preferences. This is useful for subjective qualities like helpfulness or safety."

---

## Slide 61: RL Use Cases
"When should you use RL? It's great for training specialist models that excel at narrow tasks like math or coding. It's used in post-training research for alignment and safety. And it's useful for RL algorithms research - developing novel training methods. You should use RL when it's hard to provide labeled examples, easy to verify correctness, or when you want to optimize for subjective quality."

---

## Slide 62: RL Environments
"In Tinker, RL environments use a simple interface. The initial_observation method returns the initial prompt tokens. The step method takes an action - a token ID - and returns an observation, reward, and done flag. Note that this is a token-level interface, not strings. You're working directly with token IDs."

---

## Slide 63: Reward Functions
"Here's a simple example reward function for GSM8K math problems. You extract the numerical answer from the model's response and compare it to the ground truth. The base reward is 1.0 if correct, 0.0 if wrong. You might add a small bonus for proper formatting, like using a boxed answer. This encourages the model to follow conventions while getting the right answer."

---

## Slide 64: Example - GSM8K
"GSM8K is a dataset of grade school math word problems. The RL approach is: sample completions for each question, extract the answer from each completion, check correctness - plus one if right, zero if wrong - and use RL to increase the probability of correct completions. This is often better than supervised learning when there are multiple valid solution paths, or when you want to reward the reasoning process, not just the final answer."

---

## Slide 65: Training Loop Components
"An RL training loop has several components. First, your dataset - a batch of prompts or environments. Second, rollout - you sample completions from the current policy. Third, reward - you compute rewards for those completions. Fourth, advantages - you compute advantage estimates to determine which actions were better than expected. Fifth, training - you update the policy using an importance sampling loss. Then repeat."

---

## Slide 66: Rollout Collection
"Generating rollouts looks like this: you sample completions from your model with temperature 1.0 to get diverse outputs. You compute rewards for each response using your reward function. Then you create training data that includes the responses, rewards, and computed advantages. This becomes the data you'll use to update your policy."

---

## Slide 67: Importance Sampling Loss
"Here's a subtle but important point. In RL, your sampler policy - the model that generated the rollouts - is different from your learner policy - the model you're updating. This is called off-policy learning. To correct for this distribution mismatch, you use importance sampling with ratio clipping. In Tinker, you just specify loss_fn equals importance_sampling. This corrects for the distribution mismatch, prevents large policy updates, and is more stable than vanilla policy gradient."

---

## Slide 68: RL Hyperparameters
"For RL, the learning rate formula is the same as for supervised learning. But there are additional parameters: batch_size is the number of prompts, group_size is the number of completions per prompt, and the total rollouts is batch size times group size. An important tip: scale your learning rate with the square root of batch size for optimal training."

---

## Slide 69: KL Divergence Monitoring
"KL divergence measures how much your policy has changed. A KL divergence between sampler and learner of less than 0.01 is good - they're still close. Greater than 0.1 is too much drift. Why does this matter? Large KL means the learner is very different from the sampler, which breaks the assumptions of off-policy corrections. Best practice: track KL divergence and resample if it gets too high."

---

## Slide 70: Group-Based Training
"Here's a key insight for efficient RL: generate multiple completions per prompt. This has several advantages: better advantage estimates because you can compare within the group, you can filter out constant-reward groups where there's no learning signal, and it's more sample-efficient overall. For example, you might do 128 prompts times 4 completions equals 512 rollouts. You compare rewards within each group of 4 and update the policy to favor higher-reward completions."

---

## Slide 71: Group Training Example
"Let me make this concrete. Your setup is 128 prompts, each with 4 completions, giving you 512 total rollouts. You compare rewards within each group of 4 completions for the same prompt. Then you update the policy to favor the higher-reward completions. This group-based approach is much more efficient than treating each rollout independently."

---

## Slide 72: Multi-Step Environments
"So far we've talked about single-response tasks, but you can also have multi-step environments. For example, in a Twenty Questions game, if the action is a question, you return the answer as the observation with zero reward and done equals false - the episode continues. If the action is a guess, you return a reward of plus one if correct, minus one if wrong, and done equals true - the episode ends. This enables dialogue, games, and interactive tasks."

---

## Slide 73: Math RL Environment
"Let's look at a real MathEnv from the Tinker cookbook. It has three key methods: get_question returns the problem plus instructions to write the answer in boxed format. check_format checks if the response contains a boxed answer. check_answer extracts the answer and grades it using symbolic math. This is a complete, working RL environment for math problems."

---

## Slide 74: The Math RL Flow
"Here's how it works in practice. The environment gives a problem: 'What's 15 times 23? Write your answer in boxed format.' The model generates a response: 'Let me calculate: 15 times 23 equals 345. Therefore backslash boxed 345.' The environment grades it: check_format returns true because it has a boxed answer, check_answer returns true because 345 is correct, so the reward is plus 1.0. Training uses this reward to update the model. Over time, the model learns: correct answers in proper format equals high reward."

---

## Slide 75: SL vs RL - Key Differences
"Let me highlight the key differences between supervised learning and reinforcement learning. For the data source, SL uses human-written examples while RL has the model generate its own data. The learning signal in SL is cross-entropy loss on gold labels; in RL it's a reward signal from the environment. SL has no exploration - it follows human examples. RL generates diverse attempts and explores. SL optimizes to match human responses; RL optimizes to maximize expected reward. Use SL when you want to imitate human behavior. Use RL when you have clear success metrics."

---

## Slide 76: Group-Based Training (GRPO)
"Let me show you one clever trick called Group Reward Preference Optimization, or GRPO. You generate multiple attempts for the same problem - say 16 attempts for 'What's 15 times 23?' Some attempts get the boxed answer of 345, reward plus 1.0. Some get 340, reward minus 1.0. You center the rewards within the group by subtracting the mean. This helps the model learn relative quality. Then you update the model to increase the probability of high-advantage attempts. This is more sample-efficient than standard RL."

---

## Slide 77: Part 5 - Preferences & RLHF
"Now let's talk about learning from human feedback."

---

## Slide 78: Direct Preference Optimization (DPO)
"DPO is an alternative to RLHF that's simpler. The approach is: given pairs of a prompt, chosen response, and rejected response, you maximize the probability of the chosen response over the rejected one. You don't need a separate reward model. DPO is simpler than RLHF but can be less powerful for complex preference learning."

---

## Slide 79: DPO Loss Function
"In Tinker, you just call forward_backward with loss_fn equals DPO. The key parameter is dpo_beta, which is like a temperature parameter. Higher beta means more conservative - stay closer to the base model. Lower beta means more aggressive - fit the preferences more strongly. Typical values are 0.1 to 0.5."

---

## Slide 80: Preference Datasets
"Common preference datasets include Anthropic's HHH dataset - that stands for Helpful, Honest, Harmless - HelpSteer3, and UltraFeedback. The format is simple: a prompt like 'How do I bake a cake?', a chosen response with a helpful recipe, and a rejected response like 'I don't know.' The model learns to prefer the helpful response."

---

## Slide 81: RLHF - Two-Stage Process
"RLHF is more complex but more powerful. Stage 1: train a reward model using preference pairs. The model learns to predict which response is better. The output is a scalar reward for any completion. Stage 2: use RL with that reward model. You sample completions, score them with the reward model, and use RL to maximize the reward."

---

## Slide 82: Training Preference Models
"Here's how you train a reward model. You compare two completions: reward A is the model's score for prompt plus completion A. Reward B is the score for prompt plus completion B. You use the Bradley-Terry model: the probability that A is better is the sigmoid of reward A minus reward B. The loss is negative log probability if A was actually preferred. The result is a model that can score completion quality."

---

## Slide 83: RL with Learned Rewards
"Once you have a reward model, you combine it with RL. Sample completions from your policy, score each with the reward model, use these scores as rewards in RL, and update the policy to maximize reward. The challenge is that reward models can be exploited - the policy might find ways to game the reward model. The solution is to add a KL penalty to keep the policy close to the base model, preventing it from going too far off distribution."

---

## Slide 84: Part 6 - The Tinker Cookbook
"Now let's talk about the Tinker Cookbook, which is a collection of pre-built examples."

---

## Slide 85: What is the Tinker Cookbook?
"The Tinker Cookbook provides pre-built examples for 7 major use cases. It's organized into recipe families, each demonstrating a different training approach. Think of it as example code you can run immediately, templates to customize for your tasks, and best practices for different scenarios. It's probably the fastest way to get started with Tinker."

---

## Slide 86: Recipe Categories
"The first three recipe categories are: Chat SFT for supervised fine-tuning on conversational datasets like Tulu3 and NoRobots - use this for training chat models and instruction following. Math RL for reinforcement learning on mathematical reasoning using datasets like GSM8K and MATH - the reward is getting the correct answer in boxed format. And Preference Learning for learning from human preferences using methods like DPO and RLHF."

---

## Slide 87: More Recipe Categories
"The next two categories are: Tool Use for teaching models to use retrieval tools like RAG - the reward is correctness with the tool-retrieved context. And Prompt Distillation for internalizing long or complex prompts into model parameters - use this when you want model behavior without a long system prompt."

---

## Slide 88: Additional Recipe Types
"The final two categories are: Multi-Agent for multi-turn games between agents - includes games like guess-the-number, twenty-questions, and tic-tac-toe. And Distillation for transferring knowledge from a teacher model to a student, with both on-policy and off-policy methods."

---

## Slide 89: "Basic" vs "Loop" Scripts
"Each recipe has two entry points. The 'basic' scripts like sl_basic.py and rl_basic.py use cookbook abstractions, are configurable via CLI, have production-ready features like checkpointing, metrics, and Weights & Biases integration. Start here for real projects. The 'loop' scripts like sl_loop.py and rl_loop.py are minimal, flat training loops with direct Tinker API usage - only 150 to 200 lines of readable code. Use these to understand what's happening under the hood."

---

## Slide 90: Standard Recipe Structure
"Every recipe follows a consistent pattern. There's a README explaining what it does and how to run it. A train.py file is the main training script. For RL recipes, there's an environment definition file. There's a dataset builder module. And optionally, configuration dataclasses. This consistent structure makes it easy to navigate and customize recipes."

---

## Slide 91: Running Any Recipe
"The general pattern for running a recipe is: python -m tinker_cookbook.recipes.RECIPE.train, then override any config fields from the command line. Thanks to the chz library, you can override the model name, learning rate, batch size, log path, or weights and biases project. For example, to override learning rate, you just add learning_rate equals 1e-4. To override multiple fields, just list them all. It's very flexible."

---

## Slide 92: Key Features All Recipes Share
"All recipes come with built-in production features: automatic checkpointing every N steps, resume from interruptions - just rerun with the same log path, metrics logging to a jsonl file plus optional Weights & Biases integration, evaluation during training that's configurable with eval_every, and HTML transcripts for qualitative review. You get all of this for free just by using the cookbook recipes!"

---

## Slide 93: Example - Running Math RL
"Here's a concrete example of running the Math RL recipe. For a basic run, you specify the environment like gsm8k, the model name, and the group size. For a run with custom hyperparameters, you can override group_size, learning_rate, batch_size, log_path, and wandb_project. The recipe handles everything else - data loading, rendering, training loop, evaluation, checkpointing, all of it."

---

## Slide 94: How to Choose a Recipe
"How do you choose which recipe to use? If you want to fine-tune a chat model, use chat_sl. To improve math reasoning, use math_rl. To learn from preferences, use preference. To build a custom RL task, study math_rl and create your own environment. To reduce prompt length, use prompt_distillation. For multi-agent interactions, use multiplayer_rl. To distill a large model into a small one, use distillation. Pro tip: start with the closest recipe and customize it for your needs."

---

## Slide 95: Part 7 - Practical Considerations
"Let's wrap up with some practical tips for successful fine-tuning."

---

## Slide 96: Saving Checkpoints
"There are two types of checkpoints. For inference only, use save_weights_for_sampler - this is lightweight and just saves the LoRA adapters. For resuming training, use save_state - this saves the full training state including optimizer state. To load later, call load_state with the URI. Tinker gives you persistent URIs in the format tinker:// that you can store and load later."

---

## Slide 97: Best Practices
"Here are my best practices. Start small - test on a small model and dataset first. Use default hyperparameters from the utilities; they're well-tuned. Monitor metrics - loss, accuracy, KL divergence, entropy. Evaluate frequently - don't just watch the loss. Save checkpoints because things can go wrong. Check data quality - garbage in, garbage out. And always compare to a baseline to make sure fine-tuning is actually helping."

---

## Slide 98: Common Mistakes (1/2)
"Here are common mistakes, part one. First is using the wrong learning rate - too low, or forgetting the LoRA multiplier. Second is training too long and overfitting. Third is ignoring KL divergence in RL, which leads to unstable training. These are the top three issues I see."

---

## Slide 99: Common Mistakes (2/2)
"Part two of common mistakes: Fourth is poor data formatting - wrong weights, missing tokens, malformed examples. Fifth is not evaluating on diverse examples, so you don't catch when the model breaks on edge cases. Sixth is forgetting to update the sampler in off-policy RL, which breaks the training dynamics. Avoid these and you'll save yourself a lot of headaches."

---

## Slide 100: Summary (1/2)
"Let's summarize what we've learned. From Part 0, we covered the fundamentals: LLMs, pre-training versus fine-tuning, LoRA, and the basics of supervised learning and reinforcement learning. From Part 1, we learned about Tinker's architecture: the fundamental problem that distributed training is hard, Tinker's solution of CPU orchestration plus GPU service, and a clean API with full control over training loops."

---

## Slide 101: Summary (2/2)
"From Parts 2 and 3, we covered supervised learning: the anatomy of a training script like sl_loop.py, the critical role of renderers that convert conversations to tokens and weights, and async patterns for GPU efficiency."

---

## Slide 102: Summary (3/3)
"From Part 4, we covered reinforcement learning: RL environments and reward functions, a concrete Math RL example with MathEnv, and group-based training or GRPO for efficiency. From Part 5, we covered preferences and RLHF: DPO for direct preference optimization, and RLHF as a two-stage process with reward models. From Part 6, we covered the Cookbook: 7 recipe families for different use cases, and the difference between 'basic' and 'loop' scripts."

---

## Slide 103: Key Takeaways
"Here are the key takeaways. First, Tinker makes distributed training simple - you focus on algorithms, not infrastructure. Second, renderers are critical - they control what the model learns. Third, start with the recipes - they're pre-built examples for common scenarios. Fourth, LoRA is powerful but needs higher learning rates - use the formulas! Fifth, RL opens new possibilities - you can optimize for rewards, not just labels. Sixth, the cookbook has you covered for chat, math, preferences, tools, distillation, and multi-agent scenarios. Bottom line: you can fine-tune 8 billion to 405 billion parameter models without managing GPUs!"

---

## Slide 104: Next Steps
"So what should you do next? First, install Tinker and clone the cookbook. Second, run sl_loop.py to understand the basics - read the code, it's only 156 lines. Third, pick a recipe that matches your use case. Fourth, start with small models like 8B for fast iteration. Fifth, monitor metrics and evaluate frequently. For resources, check out the Tinker Cookbook on GitHub, the documentation at docs.tinker.ai, and the API reference. My pro tip: read sl_loop.py and rl_loop.py first - they're each only about 150 lines and they'll teach you everything you need to know."

---

## Slide 105: Questions?
"Thank you for your attention! Let me leave you with a few reminders: fine-tuning is powerful but requires careful hyperparameter tuning. Start simple and iterate based on metrics. Tinker makes the infrastructure easy so you can focus on your task. And the cookbook provides working examples for every major use case. Now let's make some fine-tuned models! I'm happy to take any questions."
