# RL CFOP/ZB Rubik’s Cube Agent – Full Specification

This document is a **complete, implementation-ready design** for a Rubik’s Cube agent that:

* Learns by **playing with the cube**
* Is rewarded for **shorter, more human-like solutions**
* Naturally discovers **CFOP, ZB, x-crosses**, and EO tricks
* Is **not strictly constrained**, but strongly biased toward speedcubing style

This is **reinforcement learning with shaped rewards**, bootstrapped from recon data.

---

## 1. Core Philosophy

> The model is not a rule follower.
> It is a **style-constrained optimizer**.

* CFOP / ZB are **soft biases**, not hard rules
* Fewer moves & rotations are **hard objectives**
* Human-like structure is **rewarded**, not enforced

This allows:

* x-crosses
* EO tricks
* non-textbook but efficient solutions

---

## 2. Environment Definition

### 2.1 State Representation (Rotation-Safe)

Use a **cubie-based encoding**:

* Corners: position (0–7) + orientation (0–2)
* Edges: position (0–11) + orientation (0–1)

Optional binary features (recommended):

* Cross solved
* Number of F2L slots solved
* EO solved
* Cube solved

> Do NOT rely on fixed face colors. Rotations must be safe.

---

### 2.2 Action Space

Include **face turns + cube rotations**:

```
U D L R F B
U' D' L' R' F' B'
U2 D2 L2 R2 F2 B2
x y z x' y' z' x2 y2 z2
```

Rotations are allowed but **penalized**, not forbidden.

---

### 2.3 Episode Definition

* Start from a scrambled cube
* End when:

  * Cube is solved, OR
  * Step limit reached (e.g. 200)

Scramble length is **curriculum-based** (see Section 7).

---

## 3. Reward Function (Critical Section)

The reward is **dense, shaped, and style-aware**.

### 3.1 Step Penalty (Always On)

Encourages shorter solutions.

```
R_step = -0.01 per step
```

---

### 3.2 Action Cost (Human Bias)

```
Single face turn   = -0.05
Double turn (U2)   = -0.08
Cube rotation      = -0.10
```

This discourages excessive rotations without banning them.

---

### 3.3 Progress Rewards (Dense Signal)

#### Cross

```
+0.5 per correctly placed cross edge
+2.0 for completing the cross
```

#### F2L

```
+1.0 per solved F2L slot
-0.5 if a solved slot is broken
```

#### EO (for ZB)

```
+1.0 when EO is solved
```

#### Last Layer

```
+1.0 when OLL state reached
+3.0 when cube is fully solved
```

---

### 3.4 Style Rewards (Soft CFOP / ZB Bias)

These are small, guiding rewards.

#### CFOP-like behavior

```
+0.2 if cross completed before F2L
+0.2 if F2L slots filled without breaking cross
```

#### ZB encouragement

```
+0.3 if EO preserved during last F2L slot
+0.2 if ZBLL used instead of OLL+PLL
```

---

### 3.5 Penalties (Anti-Garbage)

```
-1.0 if cross broken after completion
-0.5 for excessive rotations in short window
-0.3 for slice-move spam (optional)
```

These prevent reward hacking while keeping freedom.

---

## 4. Learning Algorithm

### 4.1 Recommended Starter

* **PPO** (Proximal Policy Optimization)
* Single policy network
* Value head for advantage estimation

Why PPO:

* Stable
* Handles large action spaces
* Easy to tune

---

### 4.2 Network Architecture

Input:

* Cubie encoding (+ optional flags)

Backbone:

* MLP or small Transformer

Outputs:

* Policy logits over action space
* State value estimate

---

## 5. Using Recon Data (Bootstrapping)

### 5.1 Behavior Cloning Pretraining

Train the policy using supervised learning:

```
(state → human action)
```

* Rotations ARE allowed
* Actions are face turns or rotations

This gives:

* CFOP competence
* Human priors

---

### 5.2 RL Fine-Tuning with Regularization

During RL:

```
Total Loss = PPO Loss + λ * Imitation Loss
```

* λ starts high (e.g. 1.0)
* Gradually decays

This prevents drift into alien solutions.

---

## 6. How Improvement Emerges

The agent discovers better solutions by:

* Trying alternative move orders
* Finding cancellations
* Preserving EO naturally
* Using x-crosses when beneficial

No explicit programming of these concepts is required.

---

## 7. Curriculum Learning (Mandatory)

Do NOT train on full scrambles immediately.

| Stage | Scramble Length | Focus       |
| ----- | --------------- | ----------- |
| 1     | 3–5             | Mechanics   |
| 2     | 7–10            | Cross       |
| 3     | 10–15           | F2L         |
| 4     | 15–20           | EO / ZB     |
| 5     | 25              | Full solves |

Increase difficulty only after stable success.

---

## 8. Preventing Common RL Failures

### Symptom: Endless rotations

* Increase rotation penalty
* Add windowed rotation penalty

### Symptom: Never finishing

* Increase terminal reward
* Increase step penalty

### Symptom: Breaking solved parts

* Increase break penalty

---

## 9. Evaluation Metrics

Track continuously:

* Average move count
* Rotation count
* Cross length
* F2L moves per slot
* % ZB usage
* Solve success rate

Improvement should be **gradual and stable**.

---

## 10. Key Insight (Do Not Skip)

> Imitation gives **style**.
> Reinforcement learning gives **strength**.
> Reward shaping decides **what kind of strength**.

This setup mirrors AlphaGo’s evolution, but is tailored for speedcubing.

---

## 11. Recommended Build Order

1. Cube simulator (rotation-safe)
2. Reward function implementation
3. PPO baseline
4. Recon behavior cloning
5. Curriculum training
6. Reward tuning

---

## 12. End Goal

A solver that:

* Solves consistently
* Looks human
* Uses CFOP/ZB naturally
* Discovers x-crosses and EO tricks
* Improves over time without losing style

This is a **research-grade system**, not a toy.

---

**This document is intended to be directly coded from.**
