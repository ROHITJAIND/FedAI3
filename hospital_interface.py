"""
Individual Hospital Web Interface
Each hospital runs this independently to train and push weights to global model
"""
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, Response, request, session, redirect, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
import json
import time
import threading
import requests
from queue import Queue
import os
import urllib.parse
from werkzeug.utils import secure_filename

sys.path.append(str(Path(__file__).parent))

from client.client import LocalClient
from utils.auth0_config import auth0_config
from utils.auth import login_required, get_user_info, get_logout_url
from utils.pdf_analyzer import PDFAnalyzer

# Hospital ID will be set via environment variable or command line
HOSPITAL_ID = os.environ.get('HOSPITAL_ID', 'A')

app = Flask(__name__)
CORS(app)

# Configure Auth0
try:
    auth0_config.validate()
    app.secret_key = auth0_config.SECRET_KEY
    
    # Initialize OAuth
    oauth = OAuth(app)
    auth0 = oauth.register(
        'auth0',
        client_id=auth0_config.AUTH0_CLIENT_ID,
        client_secret=auth0_config.AUTH0_CLIENT_SECRET,
        server_metadata_url=f'https://{auth0_config.AUTH0_DOMAIN}/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid profile email',
        }
    )
    AUTH0_ENABLED = True
    print("[INFO] Auth0 authentication enabled")
except ValueError as e:
    AUTH0_ENABLED = False
    app.secret_key = os.urandom(24).hex()
    print(f"[WARNING] Auth0 not configured: {e}")
    print("[WARNING] Running without authentication (development mode only!)")

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
    'logs': [],
    'pdf_analysis_available': True
}

# PDF upload configuration
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
REPORTS_FOLDER = Path('reports')
REPORTS_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['REPORTS_FOLDER'] = str(REPORTS_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Event queue for SSE
event_queue = Queue()

# Client instance
client = None

# PDF Analyzer instance
pdf_analyzer = None


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
    if AUTH0_ENABLED and 'user' not in session:
        return redirect(url_for('login'))
    
    user_info = get_user_info() if AUTH0_ENABLED else None
    return render_template('hospital_dashboard.html', hospital_id=HOSPITAL_ID, user=user_info)


@app.route('/login')
def login():
    """Redirect to Auth0 login page"""
    if not AUTH0_ENABLED:
        # In development mode without Auth0, create a mock session
        session['user'] = {'name': 'Developer', 'email': 'dev@localhost'}
        return redirect(url_for('index'))
    
    redirect_uri = url_for('callback', _external=True)
    return auth0.authorize_redirect(redirect_uri)


@app.route('/callback')
def callback():
    """Handle the callback from Auth0"""
    if not AUTH0_ENABLED:
        return redirect(url_for('index'))
    
    try:
        token = auth0.authorize_access_token()
        session['user'] = token['userinfo']
        
        # Redirect to the page they were trying to access, or home
        next_url = session.pop('next_url', url_for('index'))
        return redirect(next_url)
    except Exception as e:
        add_log(f'Authentication error: {str(e)}', 'error')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Clear session and redirect to Auth0 logout"""
    session.clear()
    
    if not AUTH0_ENABLED:
        return redirect(url_for('index'))
    
    # Redirect to Auth0 logout
    return_to = url_for('index', _external=True)
    logout_url = get_logout_url(
        auth0_config.AUTH0_DOMAIN,
        auth0_config.AUTH0_CLIENT_ID,
        return_to
    )
    return redirect(logout_url)


@app.route('/api/hospital-info')
def get_hospital_info():
    """Get hospital information"""
    return jsonify({
        'hospital_id': HOSPITAL_ID,
        'data_path': f'data/Hospital_{HOSPITAL_ID}',
        'server_status': check_global_server()
    })


@app.route('/api/download-global', methods=['POST'])
@login_required
def download_global():
    """Download global model"""
    if hospital_state['is_training']:
        return jsonify({'error': 'Cannot download while training'}), 400
    
    thread = threading.Thread(target=download_global_model_worker, daemon=True)
    thread.start()
    
    return jsonify({'status': 'downloading'})


@app.route('/api/train', methods=['POST'])
@login_required
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
@login_required
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


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload-pdf', methods=['POST'])
@login_required
def upload_pdf():
    """Handle PDF upload and analysis"""
    global pdf_analyzer
    
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        input_filename = f"{HOSPITAL_ID}_{timestamp}_{filename}"
        input_path = UPLOAD_FOLDER / input_filename
        file.save(str(input_path))
        
        add_log(f'PDF uploaded: {filename}', 'success')
        
        # Generate output filename
        output_filename = f"{HOSPITAL_ID}_{timestamp}_analysis_report.pdf"
        output_path = REPORTS_FOLDER / output_filename
        
        # Start analysis in background
        thread = threading.Thread(
            target=pdf_analysis_worker,
            args=(str(input_path), str(output_path), input_filename, output_filename),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'status': 'processing',
            'message': 'PDF analysis started',
            'input_file': input_filename
        })
    
    except Exception as e:
        add_log(f'PDF upload error: {str(e)}', 'error')
        return jsonify({'error': str(e)}), 500


def pdf_analysis_worker(input_path, output_path, input_filename, output_filename):
    """Background worker for PDF analysis"""
    global pdf_analyzer
    
    try:
        add_log(f'Starting AI analysis of {input_filename}...', 'info')
        
        # Perform analysis
        results = pdf_analyzer.analyze_pdf_and_generate_report(
            input_pdf_path=input_path,
            output_pdf_path=output_path,
            hospital_id=HOSPITAL_ID
        )
        
        if 'error' in results:
            add_log(f'Analysis failed: {results["error"]}', 'error')
            return
        
        add_log(f'Analysis complete!', 'success')
        add_log(f'Patient data extracted successfully', 'success')
        
        if results.get('prediction'):
            pred = results['prediction']
            add_log(f"AI Prediction: {pred['predicted_class']} ({pred['confidence']*100:.1f}% confidence)", 'success')
        
        add_log(f'Report generated: {output_filename}', 'success')
        
        # Notify via event stream
        event_queue.put(json.dumps({
            'type': 'pdf_analysis_complete',
            'data': {
                'output_file': output_filename,
                'prediction': results.get('prediction'),
                'patient_data': results.get('patient_data')
            }
        }))
        
    except Exception as e:
        add_log(f'PDF analysis error: {str(e)}', 'error')


@app.route('/api/download-report/<filename>')
@login_required
def download_report(filename):
    """Download generated PDF report"""
    try:
        from flask import send_file
        file_path = REPORTS_FOLDER / secure_filename(filename)
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(str(file_path), as_attachment=True, download_name=filename)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports')
@login_required
def list_reports():
    """List all generated reports for this hospital"""
    try:
        reports = []
        for file_path in REPORTS_FOLDER.glob(f'{HOSPITAL_ID}_*_analysis_report.pdf'):
            reports.append({
                'filename': file_path.name,
                'size': file_path.stat().st_size,
                'created': file_path.stat().st_ctime
            })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'reports': reports})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    global client, pdf_analyzer
    client = LocalClient(hospital_id=HOSPITAL_ID)
    
    # Initialize PDF Analyzer
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        try:
            pdf_analyzer = PDFAnalyzer(
                gemini_api_key=gemini_api_key,
                model_path=f"checkpoints/hospital_{HOSPITAL_ID}_model.pth",
                preprocessor_path="checkpoints"
            )
            add_log('PDF Analyzer initialized with Gemini AI', 'success')
        except Exception as e:
            add_log(f'PDF Analyzer initialization warning: {str(e)}', 'warning')
            pdf_analyzer = None
    else:
        add_log('GEMINI_API_KEY not found in environment. PDF analysis disabled.', 'warning')
        hospital_state['pdf_analysis_available'] = False
        pdf_analyzer = None
    
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
