"""
Visualization modules for the Pathfinder application.
"""

from ui.visualizations.academic import (
    plot_selectivity_scatter,
    plot_sat_distribution,
    plot_test_policy_distribution,
    plot_test_scores_trend,
    plot_admission_trend,
    plot_enrollment_trend,
    plot_admission_rate_card,
    plot_test_policy_card,
    plot_sat_score_card,
    plot_act_score_card
)

from ui.visualizations.cost import (
    plot_tuition_distribution,
    plot_tuition_vs_size,
    plot_state_tuition_comparison,
    plot_net_price,
    plot_tuition_trend
)

from ui.visualizations.outcomes import (
    plot_graduation_rate_histogram,
    plot_debt_earnings_scatter,
    plot_graduation_trend,
    plot_detailed_debt,
    plot_debt_comparison,
    plot_graduation_rate_card,
    plot_detailed_debt_comparison,
    plot_admission_debt_earnings_ratio
)

from ui.visualizations.institution import (
    plot_control_type_distribution,
    plot_institution_size_distribution
)

from ui.visualizations.diversity import (
    plot_diversity_composition,
    plot_diversity_comparison_by_control,
    plot_gender_comparison,
    plot_gender_ratio_by_type,
    plot_staff_diversity_composition,
    plot_staff_gender_ratio_by_type
)
