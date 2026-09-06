from app.experiments.assignment import assign_variant,bucket_for

def test_assignment_is_deterministic(): assert assign_variant("u1","e1",{"control":.5,"treatment":.5})==assign_variant("u1","e1",{"control":.5,"treatment":.5})
def test_distribution_is_close_to_expected():
    counts={"control":0,"treatment":0}
    for i in range(10000):counts[assign_variant(str(i),"exp",{"control":.5,"treatment":.5})]+=1
    assert abs(counts["control"]-5000)<180
