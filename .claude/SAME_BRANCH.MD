This branch's sole purpose is to be able to run on every environment from the same branch.

Rules to take into account when fixing tests:
1. To run on dev and stage and prod(only if the test is marked with sanity)
2. Before runnning on stage to check that the tests also works there, please tell so I can add a session id cause otherwise you will encounter fastly.