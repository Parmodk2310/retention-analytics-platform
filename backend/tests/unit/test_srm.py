from app.experiments.srm import sample_ratio_mismatch
def test_balanced_not_srm(): assert not sample_ratio_mismatch({"control":5000,"treatment":5000},{"control":.5,"treatment":.5})["detected"]
def test_45_55_is_srm(): assert sample_ratio_mismatch({"control":4500,"treatment":5500},{"control":.5,"treatment":.5})["detected"]
