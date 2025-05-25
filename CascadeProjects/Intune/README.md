# Intune Device Inventory Manager

A Flask web application that connects to Microsoft Intune using Microsoft Graph API to list and manage device hardware inventory details.

## Features

- View all managed devices in a responsive, searchable table
- Detailed device information including:
  - System information (OS, manufacturer, model)
  - Hardware details (processor, memory, storage)
  - Network information (IP, MAC addresses)
  - Management status and compliance
- Secure configuration management:
  - Import/Export encrypted configurations
  - Web interface for Azure AD credentials
  - Session-based credential storage
- JSON export functionality for device inventory
- Responsive, modern UI with dark theme

## Prerequisites

- Python 3.8 or higher
- Azure AD tenant with Intune
- Azure AD application registration with the following permissions:
  - Device.Read.All
  - DeviceManagementManagedDevices.Read.All

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Intune
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Configure your Azure AD credentials in `.env` or through the web interface

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:8080
```

3. If you haven't configured your Azure AD credentials, you'll be redirected to the configuration page.

## Configuration

You can configure the application in two ways:

1. Web Interface:
   - Navigate to the Configuration page
   - Enter your Azure AD credentials
   - Save the configuration

2. Environment Variables:
   - Copy `.env.example` to `.env`
   - Fill in your Azure AD credentials:
     ```
     AZURE_TENANT_ID=your_tenant_id
     AZURE_CLIENT_ID=your_client_id
     AZURE_CLIENT_SECRET=your_client_secret
     ```

## Security Features

- Credentials are encrypted before storage
- Configuration files are encrypted when exported
- Secure file upload handling
- Session-based credential storage
- Input validation and sanitization
- File size limits
- Temporary file cleanup

## API Endpoints

- `/api/devices` - Get device inventory in JSON format
- `/api/export` - Export device inventory to JSON file
- `/config/export` - Export encrypted configuration
- `/config/clear` - Clear stored configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
