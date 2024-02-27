import sys
from PySide6.QtCore import Qt, QAbstractListModel, QByteArray
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QVBoxLayout, QWidget, QPushButton, QListView, QMessageBox
from PySide6.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo, QLowEnergyController, QLowEnergyService


class BLEDeviceModel(QAbstractListModel):
    def __init__(self, devices=[], parent=None):
        super().__init__(parent)
        self.devices = devices

    def rowCount(self, parent):
        return len(self.devices)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            device = self.devices[index.row()]
            return f"{device.name()} ({device.address().toString()})"
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Пример сканера BLE")
        self.setGeometry(100, 100, 640, 480)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.grid_layout = QGridLayout(self.central_widget)

        # device
        self.widget_device = QWidget()
        self.layoutV_device = QVBoxLayout(self.widget_device)
        # label_device
        self.label_devices = QLabel("Devices")
        self.layoutV_device.addWidget(self.label_devices)
        self.layoutV_device.setAlignment(self.label_devices, Qt.AlignCenter)
         # label_state_scanner_device
        self.label_scan_device = QLabel("")
        self.layoutV_device.addWidget(self.label_scan_device)
        # list_view_device
        self.list_view_device = QListView()
        self.layoutV_device.addWidget(self.list_view_device)
        self.device_model = BLEDeviceModel()
        self.list_view_device.setModel(self.device_model)
        # button_scanner_devices
        self.button_scanner_devices = QPushButton("Find Device")
        self.button_scanner_devices.clicked.connect(self.start_scan)
        self.layoutV_device.addWidget(self.button_scanner_devices)
        # button_connect_devices
        self.button_connect_devices = QPushButton("Connect")
        self.button_connect_devices.clicked.connect(self.connect_to_device)
        self.layoutV_device.addWidget(self.button_connect_devices)
        
        self.grid_layout.addWidget(self.widget_device, 0, 0)

        # services
        self.widget_services = QWidget()
        self.layoutV_services = QVBoxLayout(self.widget_services)
        # label_services
        self.label_services = QLabel("Services")
        self.layoutV_services.addWidget(self.label_services)
        self.layoutV_services.setAlignment(self.label_services, Qt.AlignCenter)
        # list_view_services
        self.list_view_services = QListView()
        self.layoutV_services.addWidget(self.list_view_services)
        # button_descover_services
        self.button_descover_services = QPushButton("Discover services")
        # self.button_descover_services.clicked.connect(self.descover_services)
        self.layoutV_services.addWidget(self.button_descover_services)
        # button_connect_services
        self.button_connect_services = QPushButton("Connect service")
        # self.button_connect_services.clicked.connect(self.connect_to_service)
        self.layoutV_services.addWidget(self.button_connect_services)
        
        self.grid_layout.addWidget(self.widget_services, 0, 1)

        # characteristics
        self.widget_characteristics = QWidget()
        self.layoutV_characteristics = QVBoxLayout(self.widget_characteristics)
        # label_characteristics
        self.label_characteristics = QLabel("Characteristics")
        self.layoutV_characteristics.addWidget(self.label_characteristics)
        self.layoutV_characteristics.setAlignment(self.label_characteristics, Qt.AlignCenter)
        # list_view_characteristics
        self.list_view_characteristics = QListView()
        self.layoutV_characteristics.addWidget(self.list_view_characteristics)
        # button_read_characteristics
        self.button_read_characteristics = QPushButton("Read characteristics")
        self.layoutV_characteristics.addWidget(self.button_read_characteristics)
        # self.button_descover_characteristics.clicked.connect(self.descover_characteristics)   

        self.grid_layout.addWidget(self.widget_characteristics, 0, 2) 

        self.discovery_agent = QBluetoothDeviceDiscoveryAgent()
        self.discovery_agent.setLowEnergyDiscoveryTimeout(5000)
        self.discovery_agent.deviceDiscovered.connect(self.addDevice)
        self.discovery_agent.finished.connect(self.scanFinished)

    # Start scan devices
    def start_scan(self):
        self.device_model.devices.clear()
        self.device_model.layoutChanged.emit()
        self.label_scan_device.setText("Сканирование...")
        self.discovery_agent.start(QBluetoothDeviceDiscoveryAgent.LowEnergyMethod)   

    # Finished scan devices
    def scanFinished(self):
        self.label_scan_device.setText("Сканирование закончено!")

    # Add device
    def addDevice(self, info: QBluetoothDeviceInfo):
        if info.coreConfigurations() & QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
            self.device_model.devices.append(info)
            self.device_model.layoutChanged.emit()

    def connect_to_device(self):
        if self.button_connect_devices.text() == "Connect":
            index = self.list_view_device.currentIndex()
            if index.isValid():
                device_info = self.device_model.devices[index.row()]
                self.controller = QLowEnergyController.createCentral(device_info, self)
                self.controller.connected.connect(self.on_connected)
                self.controller.disconnected.connect(self.on_disconnected)
                self.controller.errorOccurred.connect(self.on_error)
                self.controller.discoveryFinished.connect(self.on_service_discovered_finished)
                self.controller.connectToDevice()
        elif self.button_connect_devices.text() == "Disconnect":
            self.controller.disconnectFromDevice()
    
    def on_connected(self):
        self.button_connect_devices.setText("Disconnect")

    def on_disconnected(self):
        self.button_connect_devices.setText("Connect")

    def on_error(self, error):
        pass

    def on_service_discovered_finished(self):
        pass
    



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())