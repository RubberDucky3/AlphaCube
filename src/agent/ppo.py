import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
from src.agent.model import ActorCritic

class PPOAgent:
    def __init__(self, obs_dim, act_dim, lr=3e-4, gamma=0.99, eps_clip=0.2, k_epochs=4, hybrid_lambda=1.0):
        self.policy = ActorCritic(obs_dim, act_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.k_epochs = k_epochs
        self.hybrid_lambda = hybrid_lambda
        
        self.mse_loss = nn.MSELoss()
        self.ce_loss = nn.CrossEntropyLoss()
        
    def load_pretrained(self, path):
        if os.path.exists(path):
            self.policy.load_state_dict(torch.load(path))
            print(f"Loaded pre-trained weights from {path}")

    def select_action(self, obs, mask=None):
        state = torch.FloatTensor(obs).unsqueeze(0)
        logits, value = self.policy(state)
        
        if mask is not None:
            # Apply mask (mask=False means invalid)
            mask_t = torch.BoolTensor(mask).unsqueeze(0)
            logits[~mask_t] = -1e10
            
        dist = torch.distributions.Categorical(logits=logits)
        action = dist.sample()
        return action.item(), dist.log_prob(action).item(), value.item()

    def update(self, memory, expert_batch=None):
        # ... logic as before ...
        states = torch.FloatTensor(np.array([t[0] for t in memory]))
        actions = torch.LongTensor(np.array([t[1] for t in memory]))
        old_log_probs = torch.FloatTensor(np.array([t[2] for t in memory]))
        rewards = [t[3] for t in memory]
        dones = [t[4] for t in memory]

        # Monte Carlo estimate of returns
        returns = []
        discounted_sum = 0
        for reward, done in zip(reversed(rewards), reversed(dones)):
            if done:
                discounted_sum = 0
            discounted_sum = reward + (self.gamma * discounted_sum)
            returns.insert(0, discounted_sum)
            
        returns = torch.FloatTensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-7)
        
        # Optimize policy for K epochs
        for _ in range(self.k_epochs):
            logits, state_values = self.policy(states)
            dist = torch.distributions.Categorical(logits=logits)
            
            log_probs = dist.log_prob(actions)
            dist_entropy = dist.entropy()
            state_values = torch.squeeze(state_values)
            
            ratios = torch.exp(log_probs - old_log_probs)
            advantages = returns - state_values.detach()
            
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1-self.eps_clip, 1+self.eps_clip) * advantages
            
            ppo_loss = -torch.min(surr1, surr2) + 0.5 * self.mse_loss(state_values, returns) - 0.01 * dist_entropy
            
            # Hybrid Loss Logic
            loss = ppo_loss.mean()
            if expert_batch is not None and self.hybrid_lambda > 0:
                e_states, e_actions, e_dists = expert_batch # Now three elements
                e_states = torch.FloatTensor(e_states)
                e_actions = torch.LongTensor(e_actions)
                e_dists = torch.FloatTensor(e_dists)
                
                e_logits, e_values = self.policy(e_states)
                imitation_loss = self.ce_loss(e_logits, e_actions)
                dist_loss = self.mse_loss(e_values.squeeze(), e_dists)
                
                loss += self.hybrid_lambda * (imitation_loss + 0.1 * dist_loss)
            
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
        # Decay hybrid lambda
        self.hybrid_lambda *= 0.999 # Slow decay
