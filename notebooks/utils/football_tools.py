import gym
import numpy as np
from gfootball import env as fe

from ray.rllib.env.multi_agent_env import MultiAgentEnv


def create_football_env(n_vs_n=1, auto_GK=True, logdir="/tmp/football", add_checkpoint=True, dump_frequency=1):
    """
    Returns a custom gfootball environment

    n_vs_n=1  # 1...5 number of players
    auto_GK=True # let the computer control the GK
    """
    try:
        del env
    except:
        pass

    n_control = max(1, n_vs_n - int(auto_GK))
    auto_GK="_auto_GK" if auto_GK and n_vs_n > 1 else "" # auto_GK only when more than 1 player
    reward_type='checkpoint,scoring' if add_checkpoint else 'scoring'
    env = fe.create_environment(
        # env_name="academy_empty_goal_close",
        env_name=f"{n_vs_n}_vs_{n_vs_n}{auto_GK}",
        stacked=False,
        representation='simple115v2',
        # scoring is 1 for scoring a goal, -1 the opponent scoring a goal
        # checkpoint is +0.1 first time player gets to an area (10 checkpoint total, +1 reward max)
        rewards=reward_type,
        logdir=logdir,
        write_goal_dumps=True,
        write_full_episode_dumps=True,
        render=False,
        write_video=True,
        dump_frequency=dump_frequency,
        extra_players=None,
        number_of_left_players_agent_controls=n_control,
        number_of_right_players_agent_controls=0)
    return env


class RllibGFootball(MultiAgentEnv):
    def __init__(self, n_vs_n=1, auto_GK=True, logdir="/tmp/football", add_checkpoint=True, dump_frequency=1):
        self.env = create_football_env(n_vs_n=n_vs_n,
                                       auto_GK=auto_GK,
                                       logdir=logdir,
                                       add_checkpoint=add_checkpoint,
                                       dump_frequency=dump_frequency)

        num_agents = max(1, n_vs_n - int(auto_GK))
        self.action_space = self.env.action_space if \
                    num_agents else gym.spaces.Discrete(self.env.action_space.nvec[1])
        self.observation_space = self.env.observation_space if \
                    num_agents else gym.spaces.Box(
                                        low=self.env.observation_space.low[0],
                                        high=self.env.observation_space.high[0],
                                        dtype=self.env.observation_space.dtype)
        self.num_agents = num_agents
        self.reward_range = np.array((-np.inf, np.inf))
        self.metadata = {'render.modes': ['human', 'rgb_array'], 'video.frames_per_second': 50}
        self.spec = None

    def reset(self):
        original_obs = self.env.reset()
        obs = {}
        for x in range(self.num_agents):
            if self.num_agents > 1:
                obs['agent_%d' % x] = original_obs[x]
            else:
                obs['agent_%d' % x] = original_obs
        return obs

    def step(self, action_dict):
        actions = []
        for key, value in sorted(action_dict.items()):
            actions.append(value)
        o, r, d, i = self.env.step(actions)
        obs = {}
        rewards = {}
        dones = {}
        infos = {}
        for pos, key in enumerate(sorted(action_dict.keys())):
            infos[key] = i
            if self.num_agents > 1:
                rewards[key] = r[pos]
                obs[key] = o[pos]
                dones[key] = d
            else:
                rewards[key] = r
                obs[key] = o
                dones[key] = d
        dones['__all__'] = d
        return obs, rewards, dones, infos