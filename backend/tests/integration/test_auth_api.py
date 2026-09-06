import os,pytest
pytestmark=pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="set TEST_DATABASE_URL to run integration tests")
def test_integration_environment_contract(): assert os.getenv("TEST_DATABASE_URL")
