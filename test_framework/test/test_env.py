import os

env = None
env = os.getenv('VIZIO_TEST_ENV')
assert env is not None
print('from test_env.py  env=', env)
