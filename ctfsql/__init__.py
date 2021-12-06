from gym.envs.registration import register
# import agents, domain, env, mdp, planning, pomdp

register(
    id='ctfsql-v0',
    entry_point='ctfsql.env:CTFSQLEnv',
)

register(
    id='ctfsql-v1',
    entry_point='ctfsql.env:CTFSQLEnv1',
)
