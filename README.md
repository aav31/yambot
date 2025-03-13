# yambot 🎲
Training a reinforcement learning agent to play Yamb, a Croatian dice game, because I could use all the help I can get.

## Features ✨
- 🎲 **Masked PPO Training** - Utilizes state-of-the-art [Proximal Policy Optimization with invalid action masking](https://arxiv.org/abs/2006.14171).
- 🏋️‍♂️ **Custom Gymnasium Environment** - Integrates [Gymnasium](https://gymnasium.farama.org/), an API standard for reinforcement learning, to simulate and train the AI model effectively.
- 💻 **GPU Acceleration** - Leverages Microsoft Azure's GPU resources for enhanced training efficiency.

## Rules of Yamb 📜

## How It Works 🧩

## Installation 🔧
All commands below should be run from the **root** directory.

Create environment:
`conda env create -f environment.yml`

To optionally create a new kernel for the terminal:
`conda activate yambot`
`python -m ipykernel install --user --name myenv --display-name "yambot"`

To run the unit tests, from the root directory run:
`python -m unittest discover -s tests -v`

## Folder Structure 📂
- [`configs`](configs): Contains ways of configuring the model to play Yamb.
- [`yamb`](yamb): A package containing the custom environment needed to simulate a game of Yamb.
- [`scripts`](scripts): Contains the scripts for training, testing, and evaluating yambot.

There are two folders hidden from git `models` and `logs` (folder which will contain log files for tensorboard).
You need to make these two folders.
Also drop the model_default_azure.zip into the models folder so you can use it.

## Usage 🚀
##### Training
To train from scratch (this will delete tensorboard logs and reset the episodes trained in the config file to be zero):
`python -m scripts.train --episodes 1000 --config "configs/model_default.json" --reset`

To continue training a model:
`python -m scripts.train --episodes 1000 --config "configs/model_default.json"`

On an azure machine or cluster use:
`python -m scripts.train --episodes 1000 --config "configs/model_default.json" --reset True --azure True`

To look at the results for each model:
`tensorboard --logdir=logs`

To create a new model create a new config `model_new.json`, set `episodes_trained=0`, rename `model_name=model_new`, run:
`python -m scripts.train --episodes 1000 --config "configs/model_new.json"`

##### Test and evaluation
If if you want to test the model by watching it play a game of yamb:
`python -m scripts.test --model_name model_default`

If you want to test the model by letting it play multpile games of yamb then be evaluated:
`python -m scripts.evaluate --model_name model_default --episodes 100`

##### Playing yamb yourself
This functionality is a way to play yamb yourself, and is more a full test of whether the environment is truly working as we expect:
`python -m scripts.yamb_yourself`

## License 📄

## Tests ✅
To run a single test module (`test_bla.py` file) you can run:
`python -m unittest tests.test_yamb_env`


