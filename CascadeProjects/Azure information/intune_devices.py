from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class IntuneDeviceManager:
    def __init__(self, tenant_id=None, client_id=None, client_secret=None):
        """
        Initialize with either environment variables or provided credentials
        """
        # Use provided credentials or fall back to environment variables
        self.tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
        self.client_id = client_id or os.getenv('AZURE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('AZURE_CLIENT_SECRET')
        
        self.credential = None
        self.graph_client = None
        
    def initialize(self):
        """
        Initialize the Graph client with credentials
        """
        try:
            if not all([self.tenant_id, self.client_id, self.client_secret]):
                raise ValueError("Missing required Azure AD credentials")
                
            self.credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            self.graph_client = GraphServiceClient(credentials=self.credential)
            return True
            
        except Exception as e:
            print(f"Error initializing Graph client: {str(e)}")
            return False
            
    def is_initialized(self):
        """Check if the manager is properly initialized"""
        return self.graph_client is not None

    def get_all_devices(self):
        """
        Retrieve all managed devices from Intune with their hardware details
        """
        if not self.is_initialized():
            raise ValueError("IntuneDeviceManager is not initialized")
        
        try:
            # Get managed devices
            devices = self.graph_client.devices.get()
            
            detailed_devices = []
            for device in devices.value:
                # Get detailed hardware inventory for each device
                device_detail = self.get_device_hardware_details(device.id)
                if device_detail:
                    detailed_devices.append(device_detail)
            
            return detailed_devices
            
        except Exception as e:
            print(f"Error getting devices: {str(e)}")
            return None
            
    def get_device_hardware_details(self, device_id):
        """
        Get detailed hardware inventory for a specific device
        """
        if not self.is_initialized():
            raise ValueError("IntuneDeviceManager is not initialized")
        
        try:
            # Get managed device details
            device = self.graph_client.devices.by_device_id(device_id).get()
            
            # Get additional hardware inventory details
            hw_info = self.graph_client.devices.by_device_id(device_id).get_hardware_information()
            
            # Combine device info with hardware details
            device_details = {
                'device_id': device.id,
                'display_name': device.display_name,
                'operating_system': device.operating_system,
                'os_version': device.operating_system_version,
                'manufacturer': hw_info.manufacturer,
                'model': hw_info.model,
                'serial_number': hw_info.serial_number,
                'processor': {
                    'name': hw_info.processor_name,
                    'architecture': hw_info.processor_architecture,
                    'speed': hw_info.processor_speed
                },
                'memory': {
                    'total_storage': hw_info.total_storage,
                    'free_storage': hw_info.free_storage,
                    'total_ram': hw_info.total_ram,
                    'free_ram': hw_info.free_ram
                },
                'network': {
                    'wifi_mac': hw_info.wifi_mac_address,
                    'ethernet_mac': hw_info.ethernet_mac_address,
                    'ip_address': hw_info.ip_address
                },
                'last_sync_time': device.approximate_last_sign_in_date_time.isoformat() if device.approximate_last_sign_in_date_time else None,
                'enrollment_date': device.enrollment_date.isoformat() if device.enrollment_date else None,
                'compliance_state': device.compliance_state,
                'management_state': device.management_state
            }
            
            return device_details
            
        except Exception as e:
            print(f"Error getting device details for {device_id}: {str(e)}")
            return None
            
    def export_to_json(self, devices, filename='device_inventory.json'):
        """
        Export device inventory to JSON file
        """
        try:
            with open(filename, 'w') as f:
                json.dump(devices, f, indent=2)
            print(f"Device inventory exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {str(e)}")
            return False
