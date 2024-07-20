import pygame
import argparse
from yamb import YambEnv, FlattenGrid
import time
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks

def main(args):
    model = MaskablePPO.load(f"models/{args.model_name}")
    try:
        env = YambEnv()
        # Comment / uncomment the line below if you need the grid to be flattened
        env = FlattenGrid(env)
        obs, _ = env.reset()
        terminated, truncated = False, False
        env.render()
        while not (terminated or truncated):
            time.sleep(1)
            action_masks = get_action_masks(env)
            action, _states = model.predict(obs, action_masks=action_masks)
            obs, reward, terminated, truncated, info = env.step(action)
            env.render()

        # This will pause the notebook and wait for the user to press Enter
        input("Press Enter to continue...")
        env.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch a yambot play as a test")
    parser.add_argument("--model_name", type=str, required=True, help="specify the model name e.g. model_default")
    args = parser.parse_args()
    main(args)