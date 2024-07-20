import os
import argparse
import json
from stable_baselines3.common.env_checker import check_env
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.evaluation import evaluate_policy
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env
from yamb import YambEnv, FlattenGrid


def create_vec_env(num_envs: int) -> SubprocVecEnv:
    """Create a vectorized yamb environment
    
    :param num_envs: number of environments you want to train in parallel
    
    :return: vectorized environment
    """
    def mask_fn(e): return e.action_masks()
    # here you specify whether or not to flatten the grid in the environment
    # remember if you flatten the grid in the environment, the test.py will need to reflect this
    vec_env = make_vec_env(YambEnv, n_envs=num_envs, vec_env_cls=SubprocVecEnv, wrapper_class=FlattenGrid)
    return vec_env
    
def reset():
    """Reset the config episodes_trained to zero and additionally delete all logs
    for that particular model
    """
    with open(args.config, "r") as f:
        config = json.load(f)
        
    config["episodes_trained"] = 0
    
    with open(args.config, "w") as f:
        json.dump(config, f, indent=4)
    
    log_path = f"logs/{config["model_name"]}_0"
    if os.path.exists(log_path):
        for filename in os.listdir(log_path):
            file_path = os.path.join(log_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                    print(f"Deleted {file_path}")
                elif os.path.isdir(file_path):
                    print(f"Skipping directory {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        os.rmdir(log_path)
        

def main(args):
    vec_env = create_vec_env(4)
    
    if args.reset:
        reset()
    
    with open(args.config, "r") as f:
        config = json.load(f)
        
    if config["episodes_trained"] == 0:
        print("Creating new model ...")
        model = MaskablePPO("MultiInputPolicy", vec_env, verbose=1, **config["params"], tensorboard_log="logs/")
    else:
        print("Loading model ...")
        model = MaskablePPO.load(f"models/{config["model_name"]}")
        model.set_env(vec_env)
        
    episode_length = 168
    
    # train for an extra args.episodes
    model.learn(total_timesteps=args.episodes * episode_length, reset_num_timesteps=False, tb_log_name=config["model_name"])
    
    # save the model and update configs
    model.save(f"models/{config["model_name"]}")
    config["episodes_trained"] += args.episodes
    with open(args.config, "w") as f:
        json.dump(config, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a maskable PPO model with sb3 contrib")
    parser.add_argument('--episodes', type=int, required=True, help="Number of episodes of training")
    parser.add_argument('--config', type=str, required=True, help="Path to the config file")
    parser.add_argument('--reset', type=bool, default=False, help="If true resets the config and wipes the logs")
    args = parser.parse_args()
    main(args)