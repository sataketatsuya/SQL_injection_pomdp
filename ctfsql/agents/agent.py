import re
from typing import List, Mapping, Any, Optional
from collections import defaultdict

import numpy as np

import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F

import const
from ctfsql.agents.command_scorer import CommandScorer

class NeuralAgent:
    """ Simple Neural Agent for playing TextWorld games. """

    def __init__(self, g_model, g_optimizer) -> None:
        self._initialized = False
        self._epsiode_has_started = False
        self.id2word = ["<PAD>", "<UNK>"]
        self.word2id = {w: i for i, w in enumerate(self.id2word)}

        self.g_model, self.g_optimizer = g_model, g_optimizer

        self.model = CommandScorer(input_size=const.MAX_VOCAB_SIZE, hidden_size=128)
        self.optimizer = optim.Adam(self.model.parameters(), 0.00003)

        self.mode = "test"

    def train(self):
        self.mode = "train"
        self.stats = {"max": defaultdict(list), "mean": defaultdict(list)}
        self.transitions = []
        self.model.reset_hidden(1)
        self.last_score = 0
        self.no_train_step = 0

    def test(self):
        self.mode = "test"
        self.model.reset_hidden(1)

    def _get_word_id(self, word):
        if word not in self.word2id:
            if len(self.word2id) >= const.MAX_VOCAB_SIZE:
                return self.word2id["<UNK>"]

            self.id2word.append(word)
            self.word2id[word] = len(self.word2id)

        return self.word2id[word]

    def _tokenize(self, text):
        # Simple tokenizer: strip out all non-alphabetic characters.
        text = re.sub("[^a-zA-Z0-9\- ]", " ", text)
        word_ids = list(map(self._get_word_id, text.split()))
        return word_ids

    def _process(self, texts):
        texts = list(map(self._tokenize, texts))
        max_len = max(len(l) for l in texts)
        padded = np.ones((len(texts), max_len)) * self.word2id["<PAD>"]

        for i, text in enumerate(texts):
            padded[i, :len(text)] = text

        padded_tensor = torch.from_numpy(padded).type(torch.long).to(const.DEVICE)
        padded_tensor = padded_tensor.permute(1, 0) # Batch x Seq => Seq x Batch
        return padded_tensor

    def _discount_rewards(self, last_values):
        returns, advantages = [], []
        R = last_values.data
        for t in reversed(range(len(self.transitions))):
            rewards, _, _, values = self.transitions[t]
            R = rewards + const.GAMMA * R
            adv = R - values
            returns.append(R)
            advantages.append(adv)

        return returns[::-1], advantages[::-1]

    def act(self, obs: str, score: int, done: bool, infos: Mapping[str, Any]):

        # Build agent's observation: html_feedback + look + status_code + url.
        input_ = "{}\n{}\n{}\n{}".format(obs, infos["description"], infos["status_code"], infos["url"])

        # Tokenize and pad the input and the commands to chose from.
        input_tensor = self._process([input_])
        commands_tensor = self._process(infos["admissible_commands"])

        # Get our next action and value prediction.
        outputs, indexes, values = self.model(input_tensor, commands_tensor)
        action_id = indexes[0].item()
        action = infos["admissible_commands"][indexes[0]]

        if self.mode == "test":
            if done:
                self.model.reset_hidden(1)
            return action_id, action

        self.no_train_step += 1

        if self.transitions:
            reward = score - self.last_score  # Reward is the gain/loss in score.
            self.last_score = score
            if infos["won"]:
                reward += const.FLAG_REWARD

            self.transitions[-1][0] = reward  # Update reward information.

        self.stats["max"]["score"].append(score)
        if infos["won"]:
            # Update model
            returns, advantages = self._discount_rewards(values)

            loss = 0
            for transition, ret, advantage in zip(self.transitions, returns, advantages):
                reward, indexes_, outputs_, values_ = transition

                advantage        = advantage.detach() # Block gradients flow here.
                probs            = F.softmax(outputs_, dim=2)
                log_probs        = torch.log(probs)
                log_action_probs = log_probs.gather(2, indexes_)
                policy_loss      = (-log_action_probs * advantage).sum()
                value_loss       = (.5 * (values_ - ret) ** 2.).sum()
                entropy     = (-probs * log_probs).sum()
                loss += policy_loss + 0.5 * value_loss - 0.1 * entropy

                self.stats["mean"]["reward"].append(reward)
                self.stats["mean"]["policy"].append(policy_loss.item())
                self.stats["mean"]["value"].append(value_loss.item())
                self.stats["mean"]["entropy"].append(entropy.item())
                self.stats["mean"]["confidence"].append(torch.exp(log_action_probs).item())

            msg = "{:6d}. ".format(self.no_train_step)
            msg += "  ".join("{}: {: 3.3f}".format(k, np.mean(v)) for k, v in self.stats["mean"].items())
            msg += "  " + "  ".join("{}: {:2d}".format(k, np.max(v)) for k, v in self.stats["max"].items())
            msg += "  vocab: {:3d}".format(len(self.id2word))
            msg += "  loss: {:3d}".format(loss)
            print(msg)
            self.stats = {"max": defaultdict(list), "mean": defaultdict(list)}

            loss.backward()
            self.g_optimizer.zero_grad()
            nn.utils.clip_grad_norm_(self.model.parameters(), 40)
            self.optimizer.step()
            self.optimizer.zero_grad()

            self.transitions = []
            self.model.reset_hidden(1)

            # pull global parameters
            self.model.load_state_dict(self.g_model.state_dict())
        else:
            # Keep information about transitions for Truncated Backpropagation Through Time.
            self.transitions.append([None, indexes, outputs, values])  # Reward will be set on the next call

        if done:
            self.last_score = 0  # Will be starting a new episode. Reset the last score.

        return action_id, action