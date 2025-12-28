"""
Individual Hospital Web Interface
Each hospital runs this independently to train and push weights to global model
"""
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, Response, request
from flask_cors import CORS
import json
import time
import threading
import requests
from queue import Queue
import os

sys.path.append(str(Path(__file__).parent))

from client.client import LocalClient

# Hospital ID will be set via environment variable or command line
HOSPITAL_ID = os.environ.get('HOSPITAL_ID', 'A')

app = Flask(__name__)
CORS(app)

# Global state for this hospital
hospital_state = {
    'hospital_id': HOSPITAL_ID,
    'is_training': False,
    'model_exists': False,
    'global_model_downloaded': False,
    'training_history': [],
    'current_epoch': 0,
    'total_epochs': 0,
    'latest_metrics': {
        'loss': 0,
        'accuracy': 0
    },
    'logs': []
}

# Event queue for SSE
event_queue = Queue()

# Client instance
client = None


def add_log(message, log_type='info'):
    """Add a log message to the queue"""
    log_entry = {
        'timestamp': time.strftime('%H:%M:%S'),
        'message': message,
        'type': log_type
    }
    hospital_state['logs'].append(log_entry)
    event_queue.put(json.dumps({'type': 'log', 'data': log_entry}))


def update_state(updates):
    """Update hospital state and notify clients"""
    hospital_state.update(updates)
    event_queue.put(json.dumps({'type': 'state', 'data': hospital_state}))


def check_global_server():
    """Check if central server is available"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def download_global_model_worker():
    """Download global model from central server"""
    global client
    
    try:
        add_log('Connecting to central server...', 'info')
        
        if not check_global_server():
            add_log('Central server is offline! Cannot download global model.', 'error')
            return False
        
        add_log('Downloading global model...', 'info')
        
        if client.download_global_model():
            add_log('Global model downloaded successfully!', 'success')
            update_state({
                'global_model_downloaded': True,
                'model_exists': True
            })
            return True
        else:
            add_log('No global model available yet. Will train from scratch.', 'warning')
            return False
            
    except Exception as e:
        add_log(f'Error downloading global model: {str(e)}', 'error')
        return False


def training_worker(num_epochs):
    """Background worker for training"""
    global client
    
    try:
        update_state({
            'is_training': True,
            'total_epochs': num_epochs,
            'current_epoch': 0
        })
        
        add_log(f'Starting training on Hospital {HOSPITAL_ID} data...', 'info')
        add_log(f'Training for {num_epochs} epochs', 'info')
        
        # Train the model
        history = client.train(num_epochs=num_epochs, verbose=False)
        
        if history['loss'] and history['accuracy']:
            # Update metrics
            final_loss = history['loss'][-1]
            final_acc = history['accuracy'][-1]
            
            update_state({
                'latest_metrics': {
                    'loss': final_loss,
                    'accuracy': final_acc
                },
                'training_history': {
                    'loss': history['loss'],
                    'accuracy': history['accuracy']
                },
                'model_exists': True
            })
            
            add_log(f'Training complete!', 'success')
            add_log(f'Final Loss: {final_loss:.4f}', 'success')
            add_log(f'Final Accuracy: {final_acc:.2%}', 'success')
            add_log(f'Local model saved for Hospital {HOSPITAL_ID}', 'info')
            
        else:
            add_log('Training failed - no metrics returned', 'error')
            
    except Exception as e:
        add_log(f'Training error: {str(e)}', 'error')
    finally:
        update_state({'is_training': False})


def push_to_global_worker():
    """Push weights to global model"""
    global client
    
    try:
        add_log('Preparing to push weights to global model...', 'info')
        
        if not check_global_server():
            add_log('Central server is offline! Cannot push weights.', 'error')
            return False
        
        # Upload weights
        add_log('Uploading model weights...', 'info')
        if client.upload_weights_to_server():
            add_log('Weights uploaded successfully!', 'success')
        else:
            add_log('Failed to upload weights', 'error')
            return False
        
        # Trigger global model update (fine-tuning)
        add_log('Requesting global model update...', 'info')
        try:
            response = requests.post("http://localhost:8000/aggregate")
            if response.status_code == 200:
                data = response.json()
                add_log(f'Global model updated successfully!', 'success')
                add_log(f'Global model is now at round {data.get("round", "N/A")}', 'success')
                add_log(f'Hospital {HOSPITAL_ID} contribution recorded!', 'success')
                return True
            else:
                add_log(f'Failed to update global model: {response.text}', 'error')
                return False
        except Exception as e:
            add_log(f'Error updating global model: {str(e)}', 'error')
            return False
            
    except Exception as e:
        add_log(f'Error pushing to global: {str(e)}', 'error')
        return False


@app.route('/')
def index():
    """Serve the hospital dashboard"""
    return render_template('hospital_dashboard.html', hospital_id=HOSPITAL_ID)


@app.route('/api/hospital-info')
def get_hospital_info():
    """Get hospital information"""
    return jsonify({
        'hospital_id': HOSPITAL_ID,
        'data_path': f'data/Hospital_{HOSPITAL_ID}',
        'server_status': check_global_server()
    })


@app.route('/api/download-global', methods=['POST'])
def download_global():
    """Download global model"""
    if hospital_state['is_training']:
        return jsonify({'error': 'Cannot download while training'}), 400
    
    thread = threading.Thread(target=download_global_model_worker, daemon=True)
    thread.start()
    
    return jsonify({'status': 'downloading'})


@app.route('/api/train', methods=['POST'])
def start_training():
    """Start training on local data"""
    if hospital_state['is_training']:
        return jsonify({'error': 'Training already in progress'}), 400
    
    data = request.json
    num_epochs = data.get('epochs', 5)
    
    # Start training in background
    thread = threading.Thread(
        target=training_worker,
        args=(num_epochs,),
        daemon=True
    )
    thread.start()
    
    return jsonify({'status': 'training_started'})


@app.route('/api/push-global', methods=['POST'])
def push_global():
    """Push weights to global model"""
    if hospital_state['is_training']:
        return jsonify({'error': 'Cannot push while training'}), 400
    
    if not hospital_state['model_exists']:
        return jsonify({'error': 'No trained model to push. Train first!'}), 400
    
    # Push in background
    thread = threading.Thread(target=push_to_global_worker, daemon=True)
    thread.start()
    
    return jsonify({'status': 'pushing'})


@app.route('/api/state')
def get_state():
    """Get current hospital state"""
    return jsonify(hospital_state)


@app.route('/api/events')
def events():
    """Server-Sent Events endpoint for real-time updates"""
    def event_stream():
        while True:
            try:
                message = event_queue.get(timeout=30)
                yield f"data: {message}\n\n"
            except:
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')


def initialize():
    """Initialize the hospital client"""
    global client
    client = LocalClient(hospital_id=HOSPITAL_ID)
    
    # Check if local model exists
    model_path = Path(f"checkpoints/hospital_{HOSPITAL_ID}_model.pth")
    if model_path.exists():
        hospital_state['model_exists'] = True
        add_log(f'Found existing local model for Hospital {HOSPITAL_ID}', 'success')
    else:
        add_log(f'No local model found. Ready to train!', 'info')
    
    # Check central server
    if check_global_server():
        add_log('Central server is online', 'success')
    else:
        add_log('Central server is offline', 'warning')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Hospital Web Interface")
    parser.add_argument(
        '--hospital',
        type=str,
        default='A',
        choices=['A', 'B', 'C'],
        help='Hospital ID (A, B, or C)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run the server on'
    )
    
    args = parser.parse_args()
    HOSPITAL_ID = args.hospital
    hospital_state['hospital_id'] = HOSPITAL_ID
    
    print("=" * 70)
    print(f" " * 20 + f"HOSPITAL {HOSPITAL_ID} INTERFACE")
    print("=" * 70)
    print(f"\n[INFO] Starting web interface for Hospital {HOSPITAL_ID}...")
    print(f"[INFO] Open your browser and navigate to:")
    print(f"\n       http://localhost:{args.port}")
    print(f"\n[INFO] Data directory: data/Hospital_{HOSPITAL_ID}/")
    print(f"[INFO] Make sure the central server is running at:")
    print(f"       http://localhost:8000")
    print("\n" + "=" * 70)
    
    initialize()
    
    app.run(debug=True, host='0.0.0.0', port=args.port, threaded=True)
