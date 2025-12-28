"""
Central Federated Learning Server - Phase 4
FastAPI backend that coordinates federated learning
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import torch
from pathlib import Path
import sys
import uvicorn
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from aggregator import FederatedAggregator
from models.model import create_model
from utils.config import SERVER_CONFIG, MODEL_CONFIG
from utils.helpers import save_model, load_model


# Initialize FastAPI app
app = FastAPI(
    title="FetalScanFL Server",
    description="Central server for federated learning on fetal ultrasound images",
    version="1.0.0"
)

# Global aggregator
aggregator = FederatedAggregator()

# Initialize global model
global_model = create_model(
    num_classes=MODEL_CONFIG['num_classes'],
    architecture=MODEL_CONFIG['architecture'],
    pretrained=MODEL_CONFIG['pretrained'],
    device=torch.device('cpu')
)

# Load existing model if available
model_path = SERVER_CONFIG['model_save_path']
if model_path.exists():
    global_model = load_model(global_model, model_path)
    aggregator.global_weights = global_model.state_dict()
else:
    # Initialize with current model weights
    aggregator.global_weights = global_model.state_dict()


# Pydantic models for request/response
class WeightsUpload(BaseModel):
    """Request model for uploading weights"""
    hospital_id: str
    weights: Dict[str, List]  # Serialized tensors as nested lists


class GlobalModelResponse(BaseModel):
    """Response model for global model"""
    round: int
    num_clients: int
    timestamp: str
    weights: Dict[str, List]


class ServerStatus(BaseModel):
    """Server status information"""
    status: str
    round: int
    num_connected_clients: int
    model_architecture: str
    num_classes: int


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - server information"""
    return {
        "service": "FetalScanFL Central Server",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "/status": "Get server status",
            "/upload_weights": "Upload client weights (POST)",
            "/global_model": "Download global model (GET)",
            "/aggregate": "Trigger aggregation (POST)"
        }
    }


@app.get("/status", response_model=ServerStatus)
async def get_status():
    """Get current server status"""
    return ServerStatus(
        status="active",
        round=aggregator.round,
        num_connected_clients=len(aggregator.client_weights),
        model_architecture=MODEL_CONFIG['architecture'],
        num_classes=MODEL_CONFIG['num_classes']
    )


@app.post("/upload_weights")
async def upload_weights(data: WeightsUpload):
    """
    Receive model weights from a client hospital
    
    This is the endpoint where hospitals "Push" their learned knowledge.
    """
    try:
        print(f"\n[IN] Receiving weights from Hospital {data.hospital_id}...")
        
        # Convert serialized weights back to tensors
        weights = {
            k: torch.tensor(v) 
            for k, v in data.weights.items()
        }
        
        # Add to aggregator
        aggregator.add_client_weights(data.hospital_id, weights)
        
        return {
            "status": "success",
            "message": f"Weights received from Hospital {data.hospital_id}",
            "hospital_id": data.hospital_id,
            "round": aggregator.round,
            "num_clients_ready": len(aggregator.client_weights)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing weights: {str(e)}")


@app.get("/global_model")
async def get_global_model():
    """
    Send the global model to clients
    
    This is the endpoint where hospitals "Pull" the collective knowledge.
    """
    try:
        if aggregator.global_weights is None:
            # If no aggregation yet, send initial model
            weights = global_model.state_dict()
        else:
            weights = aggregator.global_weights
        
        # Serialize weights for transmission
        weights_serialized = {
            k: v.cpu().numpy().tolist() 
            for k, v in weights.items()
        }
        
        return {
            "status": "success",
            "round": aggregator.round,
            "num_clients": len(aggregator.client_weights),
            "timestamp": datetime.now().isoformat(),
            "weights": weights_serialized
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending global model: {str(e)}")


@app.post("/aggregate")
async def trigger_aggregation(background_tasks: BackgroundTasks):
    """
    Manually trigger weight aggregation
    
    This combines all the knowledge from different hospitals.
    """
    try:
        if len(aggregator.client_weights) == 0:
            raise HTTPException(
                status_code=400, 
                detail="No client weights available for aggregation"
            )
        
        print(f"\n[*] Triggering aggregation...")
        
        # Perform aggregation
        global_weights = aggregator.aggregate()
        
        # Update global model
        global_model.load_state_dict(global_weights)
        
        # Save to disk
        model_path = SERVER_CONFIG['model_save_path']
        model_path.parent.mkdir(parents=True, exist_ok=True)
        save_model(global_model, model_path, {
            'round': aggregator.round,
            'num_clients': len(aggregator.client_weights)
        })
        
        num_clients = len(aggregator.client_weights)
        
        # Clear client weights for next round
        aggregator.clear_client_weights()
        
        return {
            "status": "success",
            "message": "Aggregation completed successfully",
            "round": aggregator.round,
            "num_clients_aggregated": num_clients,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during aggregation: {str(e)}")


@app.post("/reset")
async def reset_server():
    """
    Reset the server state (for testing purposes)
    """
    global aggregator, global_model
    
    # Reset aggregator
    aggregator = FederatedAggregator()
    
    # Reinitialize global model
    global_model = create_model(
        num_classes=MODEL_CONFIG['num_classes'],
        architecture=MODEL_CONFIG['architecture'],
        pretrained=MODEL_CONFIG['pretrained'],
        device=torch.device('cpu')
    )
    
    aggregator.global_weights = global_model.state_dict()
    
    return {
        "status": "success",
        "message": "Server reset successfully",
        "round": aggregator.round
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# Run server
def start_server(host: str = None, port: int = None):
    """
    Start the FastAPI server
    
    Args:
        host: Host address (default from config)
        port: Port number (default from config)
    """
    host = host or SERVER_CONFIG['host']
    port = port or SERVER_CONFIG['port']
    
    print("=" * 60)
    print("FETALSCNAFL CENTRAL SERVER")
    print("=" * 60)
    print(f"[START] Starting server at http://{host}:{port}")
    print(f"[DATA] Model: {MODEL_CONFIG['architecture']}")
    print(f"[NUM] Classes: {MODEL_CONFIG['num_classes']}")
    print(f"[SAVE] Model save path: {SERVER_CONFIG['model_save_path']}")
    print("=" * 60)
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
