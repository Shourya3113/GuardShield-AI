"""
Paired-perturbation audit harness for prompt-injection guards (Paper 1).

Every perturbation is label-blind: an attack and its benign twin receive exactly the
same transformation and template, so a guard can only score well by separating
intent, not by reacting to the format. See paper1/SPEC.md.
"""
