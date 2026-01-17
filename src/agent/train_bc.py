
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from src.agent.model import ActorCritic
from src.agent.bc_data import generate_bc_dataset
import os

def train_bc(db_path, model_save_path="models/pretrained_policy.pth", epochs=100, batch_size=256, stage="cross"):
    print(f"Generating dataset from database (Stage: {stage})...")
    states, actions, distances = generate_bc_dataset(db_path, limit=100000, stage=stage)
    print(f"Dataset generated. Total samples: {len(states)}")
    
    # Convert to torch tensors
    states_t = torch.FloatTensor(states)
    actions_t = torch.LongTensor(actions)
    distances_t = torch.FloatTensor(distances)
    
    dataset = TensorDataset(states_t, actions_t, distances_t)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    obs_dim = states.shape[1]
    act_dim = 27 
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ActorCritic(obs_dim, act_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.5)
    
    ce_criterion = nn.CrossEntropyLoss()
    mse_criterion = nn.MSELoss()
    
    model.train()
    for epoch in range(epochs):
        epoch_loss = 0
        for b_states, b_actions, b_dists in loader:
            b_states, b_actions, b_dists = b_states.to(device), b_actions.to(device), b_dists.to(device)
            
            logits, values = model(b_states)
            
            # Policy loss (Imitation)
            p_loss = ce_criterion(logits, b_actions)
            # Value loss (Distance regression)
            v_loss = mse_criterion(values.squeeze(), b_dists)
            
            loss = p_loss + 0.1 * v_loss # Weighted combination
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        scheduler.step()
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} | Loss: {epoch_loss/len(loader):.4f} | LR: {scheduler.get_last_lr()[0]}")
            
    # Save the model
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    torch.save(model.state_dict(), model_save_path)
    print(f"Model saved to {model_save_path}")

if __name__ == "__main__":
    train_bc("reconstructions.db")
