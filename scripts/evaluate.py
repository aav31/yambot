import argparse
from yamb import YambEnv, FlattenGrid
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.evaluation import evaluate_policy


def main(args):
    model = MaskablePPO.load(f"models/{args.model_name}")
    env = YambEnv()
    # Comment / uncomment the line below if you need the grid to be flattened
    env = FlattenGrid(env)
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=args.episodes, warn=False)
    print(f"Mean reward: {mean_reward}, Std reward: {std_reward}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate how yambot plays over a certain number of episodes")
    parser.add_argument("--model_name", type=str, required=True, help="Specify the model name e.g. model_default")
    parser.add_argument("--episodes", type=int, required=True, help="Number of games which yambot should play")
    args = parser.parse_args()
    main(args)