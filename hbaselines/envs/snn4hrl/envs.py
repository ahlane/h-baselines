"""Script for importing the modified AntGather environment."""
import math
import numpy as np
from gym.spaces import Box
from rllab.envs.mujoco.gather.gather_env import GatherEnv
from sandbox.snn4hrl.envs.mujoco.ant_env import AntEnv
from sandbox.snn4hrl.envs.mujoco.swimmer_env import SwimmerEnv
from hbaselines.envs.snn4hrl.snake_gather import SnakeEnv


class AntGatherEnv(GatherEnv):
    """Ant Gather environment.

    See: https://arxiv.org/pdf/1704.03012.pdf

    Attributes
    ----------
    step_number : int
        the number of steps since the current rollout began
    current_context : array_like
        the contextual term (passed to the highest-level policy)
    """

    MODEL_CLASS = AntEnv
    ORI_IND = 3
    HORIZON = 500

    def __init__(self,
                 n_apples=8,
                 n_bombs=8,
                 activity_range=10.,
                 robot_object_spacing=2.,
                 catch_range=1.,
                 n_bins=10,
                 sensor_range=6.,
                 sensor_span=2. * math.pi,
                 coef_inner_rew=0.,
                 dying_cost=0,
                 *args,
                 **kwargs):
        """Instantiate the environment class.

        In order to match the environment presented in the article, we modify
        the following default values:

        * activity_range: 6 -> 10
        * sensor_span: pi -> 2*pi
        * dying_cost: -10 -> 0

        We also add a horizon attribute which is set to 500.

        Parameters
        ----------
        n_apples : int
            Number of apples in each episode
        n_bombs : int
            Number of bombs in each episode
        activity_range : float
            The span for generating objects (x, y in [-range, range])
        robot_object_spacing : float
            Number of objects in each episode
        catch_range : float
            Minimum distance range to catch an object
        n_bins : float
            Number of objects in each episode
        sensor_range : float
            Maximum sensor range (how far it can go)
        sensor_span : float
            Maximum sensor span (how wide it can span), in radians
        coef_inner_rew : float
            inner (AntEnv) reward weighting coefficient
        dying_cost : float
            reward assigned with dying in the environment
        """
        super(AntGatherEnv, self).__init__(
            n_apples=n_apples,
            n_bombs=n_bombs,
            activity_range=activity_range,
            robot_object_spacing=robot_object_spacing,
            catch_range=catch_range,
            n_bins=n_bins,
            sensor_range=sensor_range,
            sensor_span=sensor_span,
            coef_inner_rew=coef_inner_rew,
            dying_cost=dying_cost,
            *args,
            **kwargs
        )
        self.step_number = 0
        self.current_context = None

    def step(self, action):
        """Advance the simulation by one step.

        The done mas here is modified to include the horizon ending.
        """
        obs, reward, done, _ = super(AntGatherEnv, self).step(action)

        # Check if the time horizon has been met.
        self.step_number += 1
        done = done or self.step_number == self.horizon

        # Separate the observation by agent observation and context.
        self.current_context = obs[-2 * self.n_bins:]
        obs = obs[:-2 * self.n_bins]

        return obs, reward, done, {}

    def reset(self, also_wrapped=True):
        """Reset the environment."""
        # Reset the timer.
        self.step_number = 0

        obs = super(AntGatherEnv, self).reset(also_wrapped)

        # Separate the observation by agent observation and context.
        self.current_context = obs[-2 * self.n_bins:]
        obs = obs[:-2 * self.n_bins]

        return obs

    @property
    def horizon(self):
        """Return the environment time horizon."""
        return self.HORIZON

    @property
    def observation_space(self):
        """Return the shape and bounds of the observations."""
        return self.robot_observation_space

    @property
    def context_space(self):
        """Return the shape and bounds of the contextual term."""
        return Box(
            low=-float("inf"),
            high=float("inf"),
            shape=(2 * self.n_bins,),
            dtype=np.float32)


class SwimmerGatherEnv(AntGatherEnv):
    """Swimmer Gather environment."""

    MODEL_CLASS = SwimmerEnv
    ORI_IND = 2
    HORIZON = 500


class SnakeGatherEnv(AntGatherEnv):
    """Snake Gather environment."""

    MODEL_CLASS = SnakeEnv
    ORI_IND = 2
    HORIZON = 800
