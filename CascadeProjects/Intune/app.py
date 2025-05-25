from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash, send_file
from intune_devices import IntuneDeviceManager
from config_manager import ConfigManager
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Initialize managers
device_manager = IntuneDeviceManager()
config_manager = ConfigManager()

def get_credentials_from_session():
    """Get Azure AD credentials from session"""
    encrypted_creds = session.get('encrypted_credentials')
    if encrypted_creds:
        return config_manager.decrypt_credentials(encrypted_creds)
    return {
        'tenant_id': None,
        'client_id': None,
        'client_secret': None
    }

@app.route('/')
def index():
    """Render the main page with device inventory or redirect to config if not configured"""
    credentials = get_credentials_from_session()
    
    if not all(credentials.values()):
        return redirect(url_for('config'))
        
    try:
        # Initialize device manager with session credentials
        device_manager.__init__(**credentials)
        if not device_manager.initialize():
            flash('Failed to initialize connection to Microsoft Graph API', 'error')
            return redirect(url_for('config'))
            
        devices = device_manager.get_all_devices()
        return render_template('intune_devices.html', devices=devices)
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('config'))

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Handle Azure AD configuration"""
    if request.method == 'POST':
        if 'import_config' in request.files:
            # Handle config import
            file = request.files['import_config']
            if file:
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    credentials = config_manager.import_config(filepath)
                    os.remove(filepath)  # Clean up
                    
                    if credentials:
                        # Validate imported credentials
                        device_manager.__init__(**credentials)
                        if device_manager.initialize():
                            # Store encrypted credentials in session
                            session['encrypted_credentials'] = config_manager.encrypt_credentials(credentials)
                            flash('Configuration imported successfully', 'success')
                            return redirect(url_for('index'))
                    
                    flash('Invalid configuration file', 'error')
                except Exception as e:
                    flash(f'Error importing configuration: {str(e)}', 'error')
            return redirect(url_for('config'))
            
        # Handle manual configuration
        credentials = {
            'tenant_id': request.form.get('tenant_id'),
            'client_id': request.form.get('client_id'),
            'client_secret': request.form.get('client_secret')
        }
        
        # Validate credentials
        device_manager.__init__(**credentials)
        if device_manager.initialize():
            # Store encrypted credentials in session
            session['encrypted_credentials'] = config_manager.encrypt_credentials(credentials)
            flash('Successfully connected to Microsoft Graph API', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to connect to Microsoft Graph API. Please check your credentials.', 'error')
    
    # Get current credentials from session
    credentials = get_credentials_from_session()
    return render_template('config.html', credentials=credentials)

@app.route('/config/export')
def export_config():
    """Export encrypted configuration file"""
    credentials = get_credentials_from_session()
    
    if not all(credentials.values()):
        flash('No configuration to export', 'error')
        return redirect(url_for('config'))
        
    try:
        # Create temporary file for configuration
        temp_dir = tempfile.gettempdir()
        filename = f'intune_config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        filepath = os.path.join(temp_dir, filename)
        
        if config_manager.export_config(credentials, filepath):
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='application/json'
            )
        else:
            flash('Failed to export configuration', 'error')
    except Exception as e:
        flash(f'Error exporting configuration: {str(e)}', 'error')
    
    return redirect(url_for('config'))

@app.route('/config/clear', methods=['POST'])
def clear_config():
    """Clear stored credentials"""
    session.clear()
    flash('Configuration cleared', 'success')
    return redirect(url_for('config'))

@app.route('/api/devices')
def get_devices():
    """API endpoint to get device inventory in JSON format"""
    credentials = get_credentials_from_session()
    
    if not all(credentials.values()):
        return jsonify({'error': 'Azure AD credentials not configured'}), 401
        
    try:
        device_manager.__init__(**credentials)
        if not device_manager.initialize():
            return jsonify({'error': 'Failed to initialize Microsoft Graph API connection'}), 500
            
        devices = device_manager.get_all_devices()
        return jsonify(devices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export')
def export_devices():
    """Export device inventory to JSON file"""
    credentials = get_credentials_from_session()
    
    if not all(credentials.values()):
        return jsonify({'error': 'Azure AD credentials not configured'}), 401
        
    try:
        device_manager.__init__(**credentials)
        if not device_manager.initialize():
            return jsonify({'error': 'Failed to initialize Microsoft Graph API connection'}), 500
            
        devices = device_manager.get_all_devices()
        if device_manager.export_to_json(devices):
            return jsonify({'message': 'Device inventory exported successfully'})
        else:
            return jsonify({'error': 'Failed to export device inventory'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
