from app.experiments.stats import analyze_binary
def test_known_example_is_not_significant_at_five_percent():
    result=analyze_binary(324,1000,365,1000)
    assert 0.05<result["p_value"]<0.06
    assert not result["significant"]
