DEFAULT_PRIORITY_SCORE = 0.7
MIN_COVERAGE_DEPTH = 10

PRIORITY_FEATURE_WEIGHTS = {
    'non_candidate_gene': 0.4,
    'unknown_variant': 0.3,
    'no_hgmd_entry': 0.3,
    'low_coverage_depth': 0.3,
    'synonymous': 0.1,
    'intronic': 0,
}

PRIORITY_FEATURES = sorted(PRIORITY_FEATURE_WEIGHTS.keys())


def calculate_priority(ratios=None, **kwargs):
    "Calculates a priority score based on a number of attributes."
    if not ratios:
        ratios = PRIORITY_FEATURE_WEIGHTS
    scores = [DEFAULT_PRIORITY_SCORE]
    for key, value in kwargs.items():
        if key not in PRIORITY_FEATURE_WEIGHTS:
            raise KeyError('The following keyword arguments are supported: '
                           '{keys}'.format(keys=PRIORITY_FEATURES))
        if value is True:
            scores.append(PRIORITY_FEATURE_WEIGHTS[key])
    return float(sum(scores)) / len(scores)
