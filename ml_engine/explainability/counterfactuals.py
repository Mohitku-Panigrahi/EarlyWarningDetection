from typing import Dict, Any, List

class CounterfactualSimulator:
    """
    Carefully constrained what-if counterfactual scenario generator.
    Explicitly labelled as a model simulation, not an absolute real-world guarantee.
    """

    @staticmethod
    def simulate_recovery(
        current_prob: float,
        attendance_pct: float,
        missing_count: int,
        target_attendance: float = 85.0,
    ) -> Dict[str, Any]:
        delta_att = max(0.0, target_attendance - attendance_pct)
        delta_sub = missing_count

        # Estimate reduced probability
        prob_reduction = (delta_att * 0.015) + (delta_sub * 0.08)
        projected_prob = max(0.08, round(current_prob - prob_reduction, 2))
        projected_status = "ON TRACK" if projected_prob < 0.40 else "WATCH"

        actions = []
        if delta_sub > 0:
            actions.append(f"Submit {delta_sub} pending assignment(s) within 48 hours")
        if delta_att > 0:
            actions.append(f"Attend next {int(round(delta_att / 3.0))} scheduled lectures without absence")
        if not actions:
            actions.append("Maintain consistent weekly study velocity")

        scenario_text = (
            f"If attendance increases from {attendance_pct:.1f}% to {target_attendance:.1f}% "
            f"and {delta_sub} overdue coursework submission(s) are completed"
        )

        return {
            "scenario": scenario_text,
            "current_probability": current_prob,
            "projected_probability": projected_prob,
            "projected_status": projected_status,
            "target_actions": actions,
            "model_disclaimer": "Counterfactual estimation based on model sensitivities under ceteris paribus conditions.",
        }

class TransparentBayesianUpdater:
    """
    Transparent pedagogical Bayesian inference updater (CSE276 Unit II Bayesian Reasoning).
    Computes P(H|E) = [P(E|H) * P(H)] / P(E)
    where:
      H = Academic Support Hypothesis (student requires intervention)
      E = Observed multi-indicator evidence
    Includes full denominator decomposition, probability normalization, and zero-probability safeguards.
    """

    def __init__(self, base_prior: float = 0.22):
        self.base_prior = max(0.001, min(0.999, float(base_prior)))

    def update(
        self,
        has_low_attendance: bool,
        has_low_marks: bool,
        has_overdue_work: bool,
        custom_prior: Optional[float] = None,
    ) -> Dict[str, Any]:
        prior = custom_prior if custom_prior is not None else self.base_prior
        prior = max(0.001, min(0.999, float(prior)))
        prior_neg = 1.0 - prior

        p_e_given_h = 1.0
        p_e_given_not_h = 1.0
        evidence_items = []

        if has_low_attendance:
            p_e_given_h *= 0.72
            p_e_given_not_h *= 0.15
            evidence_items.append("Attendance < 75%")
        else:
            p_e_given_h *= 0.28
            p_e_given_not_h *= 0.85

        if has_low_marks:
            p_e_given_h *= 0.68
            p_e_given_not_h *= 0.18
            evidence_items.append("Assessment Score Drop (>=10%)")
        else:
            p_e_given_h *= 0.32
            p_e_given_not_h *= 0.82

        if has_overdue_work:
            p_e_given_h *= 0.60
            p_e_given_not_h *= 0.20
            evidence_items.append("Pending/Overdue Tasks (>=2)")
        else:
            p_e_given_h *= 0.40
            p_e_given_not_h *= 0.80

        if not evidence_items:
            evidence_label = "Clean Academic Record (Satisfactory Attendance & Pacing)"
        else:
            evidence_label = " + ".join(evidence_items)

        numerator = p_e_given_h * prior
        complement_term = p_e_given_not_h * prior_neg
        p_e = numerator + complement_term

        if p_e < 1e-9:
            p_e = 1e-9

        posterior = numerator / p_e
        posterior_complement = complement_term / p_e
        lr = (p_e_given_h / max(1e-9, p_e_given_not_h))

        return {
            "hypothesis": "Student Requires Targeted Academic Support (H)",
            "prior": round(prior, 4),
            "prior_complement": round(prior_neg, 4),
            "evidence": evidence_label,
            "likelihood_P_E_given_H": round(p_e_given_h, 4),
            "likelihood_P_E_given_not_H": round(p_e_given_not_h, 4),
            "marginal_likelihood_P_E": round(p_e, 4),
            "likelihood_ratio": round(lr, 2),
            "posterior": round(float(posterior), 4),
            "posterior_complement": round(float(posterior_complement), 4),
            "is_normalized": abs((posterior + posterior_complement) - 1.0) < 1e-5,
            "calculation_formula": "P(H|E) = [P(E|H) * P(H)] / [P(E|H)*P(H) + P(E|¬H)*P(¬H)]",
            "assumptions": (
                "Prior P(H)=0.22 represents historical LPU departmental early-warning base rate. "
                "Evidence likelihoods assume conditional independence given hypothesis state."
            ),
        }
