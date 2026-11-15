# CSE276 Unit II: Bayesian Reasoning & Evidence Synthesis
**LPU-RISK-01 Probabilistic Decision-Support Specification**

---

## 1. Theoretical Foundation
Bayes' Theorem provides a sound mathematical framework for updating the probability of an academic support hypothesis $H$ given observed multi-indicator telemetry evidence $E$:

$$P(H \mid E) = \frac{P(E \mid H) \cdot P(H)}{P(E)}$$

where the denominator (marginal evidence likelihood) is decomposed by the Law of Total Probability:

$$P(E) = P(E \mid H) \cdot P(H) + P(E \mid \neg H) \cdot P(\neg H)$$

---

## 2. Parameterization in LPU-RISK-01

### 2.1 Prior Probability $P(H)$
* **Base Rate:** $P(H) = 0.22$
* **Provenance:** Derived from historical departmental records where approximately $22\%$ of students in Semester 4 encounter academic friction requiring mentor intervention.
* **Complement:** $P(\neg H) = 1.0 - 0.22 = 0.78$

### 2.2 Conditional Likelihoods $P(E_i \mid H)$ and $P(E_i \mid \neg H)$
Under conditional independence assumptions:

| Evidence Component $E_i$ | Description | $P(E_i \mid H)$ | $P(E_i \mid \neg H)$ | Likelihood Ratio |
|---|---|---|---|---|
| $E_1$ | Attendance $< 75\%$ | $0.72$ | $0.15$ | $4.80$ |
| $E_2$ | Assessment Drop $\ge 10\%$ | $0.68$ | $0.18$ | $3.78$ |
| $E_3$ | Overdue Tasks $\ge 2$ | $0.60$ | $0.20$ | $3.00$ |

---

## 3. Mathematical Safeguards & Properties
1. **Zero-Probability Safeguard:** Priors are clamped to $[0.001, 0.999]$, and $P(E)$ is constrained to $\ge 10^{-9}$ to prevent division-by-zero anomalies.
2. **Probability Normalization:**
   $$P(H \mid E) + P(\neg H \mid E) = 1.0 \pm 10^{-5}$$
   Every update explicitly verifies that the posterior and its complement sum to unity.
3. **Transparent Decomposition:** Rather than outputting an opaque risk probability, the system exposes the prior, numerator, complement term, marginal likelihood, and Bayes factor to faculty mentors.
