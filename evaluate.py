# Copied from https://github.com/avalds/QisCoin/blob/master/evaluation.py
# Code after: https://colab.research.google.com/drive/1KoAQ1C_BNtGV3sVvZCnNZaER9rstmy0s#scrollTo=ygl_gVmV_QP7

import numpy as np

def evaluate_model(model, env, nb_episodes=1000, verbose = False):
    episode_scores = [0.0]
    obs, infos = env.reset()
    score = 0
    done = False
    for no_episode in range(nb_episodes):
        while not done:
            command_id, command = model.act(obs, score, done, infos)
            obs, score, done, infos = env.step(command_id, command)

            #Need to take the first element in action, as sometimes it is a vector of length n.
            episode_scores[-1] += score
            if done:
                obs, infos = env.reset()
                episode_scores.append(0.0)
                if(verbose): print("vicory")

    mean_score = round(np.mean(episode_scores), 3)
    return mean_score, len(episode_scores)-1

def evaluate_random(env, num_steps=1000):
    episode_rewards = [0.0]
    obs = env.reset()
    for i in range(num_steps):
        obs, reward, done, _ = env.step(env.action_space.sample())
        episode_rewards[-1] += reward
        if done:
            obs = env.reset()
            episode_rewards.append(0.0)

    mean_reward = round(np.mean(episode_rewards), 3)
    return mean_reward, len(episode_rewards)-1
