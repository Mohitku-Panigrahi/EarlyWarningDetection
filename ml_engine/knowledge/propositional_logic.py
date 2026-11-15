from typing import Dict, Any, List, Set

class PropExpr:
    """Base class for Propositional Logic formulas."""
    def evaluate(self, model: Dict[str, bool]) -> bool:
        raise NotImplementedError

    def variables(self) -> Set[str]:
        raise NotImplementedError

    def to_string(self) -> str:
        raise NotImplementedError

class PropVar(PropExpr):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, model: Dict[str, bool]) -> bool:
        return bool(model.get(self.name, False))

    def variables(self) -> Set[str]:
        return {self.name}

    def to_string(self) -> str:
        return self.name

class PropNot(PropExpr):
    def __init__(self, expr: PropExpr):
        self.expr = expr

    def evaluate(self, model: Dict[str, bool]) -> bool:
        return not self.expr.evaluate(model)

    def variables(self) -> Set[str]:
        return self.expr.variables()

    def to_string(self) -> str:
        return f"¬({self.expr.to_string()})"

class PropAnd(PropExpr):
    def __init__(self, left: PropExpr, right: PropExpr):
        self.left = left
        self.right = right

    def evaluate(self, model: Dict[str, bool]) -> bool:
        return self.left.evaluate(model) and self.right.evaluate(model)

    def variables(self) -> Set[str]:
        return self.left.variables().union(self.right.variables())

    def to_string(self) -> str:
        return f"({self.left.to_string()} ∧ {self.right.to_string()})"

class PropOr(PropExpr):
    def __init__(self, left: PropExpr, right: PropExpr):
        self.left = left
        self.right = right

    def evaluate(self, model: Dict[str, bool]) -> bool:
        return self.left.evaluate(model) or self.right.evaluate(model)

    def variables(self) -> Set[str]:
        return self.left.variables().union(self.right.variables())

    def to_string(self) -> str:
        return f"({self.left.to_string()} ∨ {self.right.to_string()})"

class PropImplies(PropExpr):
    def __init__(self, antecedent: PropExpr, consequent: PropExpr):
        self.antecedent = antecedent
        self.consequent = consequent

    def evaluate(self, model: Dict[str, bool]) -> bool:
        # P -> Q is equivalent to (not P) or Q
        return (not self.antecedent.evaluate(model)) or self.consequent.evaluate(model)

    def variables(self) -> Set[str]:
        return self.antecedent.variables().union(self.consequent.variables())

    def to_string(self) -> str:
        return f"({self.antecedent.to_string()} → {self.consequent.to_string()})"

class PropositionalReasoner:
    """
    Evaluator and truth table generator for Propositional Logic in academic monitoring.
    Demonstrates CSE276 Unit II Propositional Logic.
    """

    @staticmethod
    def evaluate_expression(expr: PropExpr, model: Dict[str, bool]) -> Dict[str, Any]:
        result = expr.evaluate(model)
        return {
            "formula": expr.to_string(),
            "model": model,
            "evaluated_truth_value": result,
        }

    @staticmethod
    def generate_truth_table(expr: PropExpr) -> Dict[str, Any]:
        vars_list = sorted(list(expr.variables()))
        n = len(vars_list)
        rows = []

        # Generate all 2^n assignments
        for i in range(2 ** n):
            model = {}
            for j, v in enumerate(vars_list):
                # Bit value determines boolean
                model[v] = bool((i >> (n - 1 - j)) & 1)
            eval_val = expr.evaluate(model)
            row = dict(model)
            row["result"] = eval_val
            rows.append(row)

        is_tautology = all(r["result"] for r in rows)
        is_satisfiable = any(r["result"] for r in rows)
        is_contradiction = not is_satisfiable

        return {
            "formula": expr.to_string(),
            "variables": vars_list,
            "total_rows": len(rows),
            "rows": rows,
            "is_tautology": is_tautology,
            "is_satisfiable": is_satisfiable,
            "is_contradiction": is_contradiction,
        }
