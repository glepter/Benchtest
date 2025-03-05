import network
import time
import json

class WiFiManager:
    def __init__(self, filename='wifi_networks.json', github_url='https://raw.githubusercontent.com/glepter/Benchtest/new/main/wifi_networks.json'):
        self.filename = filename
        self.github_url = github_url
        self.wifi_networks = self.load_wifi_networks()
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def load_wifi_networks(self):
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except OSError:
            return []

    def save_wifi_networks(self):
        with open(self.filename, 'w') as file:
            json.dump(self.wifi_networks, file)

    def scan_networks(self):
        return self.wlan.scan()

    def connect_to_wifi(self, ssid, password):
        self.wlan.connect(ssid, password)
        
        timeout = 10  # seconds
        start_time = time.time()
        
        while not self.wlan.isconnected():
            if time.time() - start_time > timeout:
                return False
            time.sleep(1)
        
        return True

    def manage_connections(self):
        available_networks = self.scan_networks()
        available_ssids = [network[0].decode('utf-8') for network in available_networks]
        consecutive_failures = 0
        
        for network in self.wifi_networks:
            ssid = network['ssid']
            password = network['password']
            
            if ssid in available_ssids:
                print(f'Trying to connect to {ssid}...')
                
                if self.connect_to_wifi(ssid, password):
                    print(f'Connected to {ssid}')
                    consecutive_failures = 0
                    break
                else:
                    print(f'Failed to connect to {ssid}')
                    consecutive_failures += 1
                    
                    if consecutive_failures >= 3:
                        print('Failed to connect to WiFi after 3 attempts. Stopping.')
                        break
            else:
                print(f'{ssid} not found in range.')

    def add_wifi_network(self, ssid, password):
        self.wifi_networks.append({'ssid': ssid, 'password': password})
        self.save_wifi_networks()

    def update_wifi_networks_from_github(self):
        try:
            response = urequests.get(self.github_url)
            if response.status_code == 200:
                remote_data = response.json()
                if remote_data != self.wifi_networks:
                    with open(self.filename, 'w') as file:
                        json.dump(remote_data, file)
                    self.wifi_networks = remote_data
                    print('WiFi networks file updated from GitHub.')
                else:
                    print('Local WiFi networks file is already up-to-date.')
            else:
                print('Failed to fetch the file from GitHub.')
        except Exception as e:
            print(f'Error updating WiFi networks from GitHub: {e}')
