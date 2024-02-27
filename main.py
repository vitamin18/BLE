import sys
from PySide6.QtCore import Qt, QAbstractListModel, QByteArray
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QListView, QMessageBox
from PySide6.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo, QLowEnergyController, QLowEnergyService, QBluetoothUuid, QBluetoothLocalDevice

import numpy as np

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

class BLEScannerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Пример сканера BLE")
        self.setGeometry(100, 100, 640, 480)

        layout = QVBoxLayout()

        self.device_list = QLabel()
        layout.addWidget(self.device_list)

        self.device_list_view = QListView()
        layout.addWidget(self.device_list_view)

        self.scan_button = QPushButton("Find Device")
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_device)
        layout.addWidget(self.connect_button)

        self.discover_services_button = QPushButton("Connect Services")
        self.discover_services_button.clicked.connect(self.connect_services)
        layout.addWidget(self.discover_services_button)

        self.discover_characteristics_button = QPushButton("Write characteristics")
        self.discover_characteristics_button.clicked.connect(self.write_characteristics)
        layout.addWidget(self.discover_characteristics_button)

        self.discover_characteristics_button = QPushButton("Disconnects device")
        self.discover_characteristics_button.clicked.connect(self.disconnect_device)
        layout.addWidget(self.discover_characteristics_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.device_model = BLEDeviceModel()
        self.device_list_view.setModel(self.device_model)

        self.discovery_agent = QBluetoothDeviceDiscoveryAgent()
        self.discovery_agent.setLowEnergyDiscoveryTimeout(5000)
        self.discovery_agent.deviceDiscovered.connect(self.addDevice)
        self.discovery_agent.finished.connect(self.scanFinished)


    def start_scan(self):
        self.device_model.devices.clear()
        self.device_model.layoutChanged.emit()
        self.device_list.setText("Сканирование...")
        self.discovery_agent.start(QBluetoothDeviceDiscoveryAgent.LowEnergyMethod)

    def scanFinished(self):
        self.device_list.setText("Сканирование закончено!")

    def addDevice(self, info: QBluetoothDeviceInfo):
         if info.coreConfigurations() & QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
            self.device_model.devices.append(info)
            self.device_model.layoutChanged.emit()

    def connect_to_device(self):
       index = self.device_list_view.currentIndex()
       if index.isValid():
        device_info = self.device_model.devices[index.row()]
        self.controller = QLowEnergyController.createCentral(device_info, self)
        self.controller.connected.connect(self.on_connected)
        self.controller.disconnected.connect(self.on_disconnected)
        self.controller.errorOccurred.connect(self.on_error)
        self.controller.discoveryFinished.connect(self.on_service_discovered_finished)
        self.controller.connectToDevice()
    
    def disconnect_device(self):
        self.controller.disconnectFromDevice()

    def on_connected(self):
        print("Успешно подключено к устройству.")
        self.controller.discoverServices()

    def on_disconnected(self):
        print("Подключение к устройству разорвано.")

    def on_error(self, error):
        print(f"Произошла ошибка при подключении: {error}.")

    def on_service_discovered_finished(self):
        service_list = self.controller.services()
        for service in service_list:
            print(service)

    def connect_services(self):
        service_list = self.controller.services()
        self.service = self.controller.createServiceObject(service_list[0])
        self.service.stateChanged.connect(self.on_state_changed)
        self.service.characteristicChanged.connect(self.on_characteristic_changed)
        self.service.discoverDetails()
        
    def on_state_changed(self, state):
        print("Service state changed:", state)
        if state == QLowEnergyService.ServiceState.RemoteServiceDiscovered:
            characteristics = self.service.characteristics()
            for characteristic in characteristics:
                print("Characteristic UUID:", characteristic.uuid(), " Value:", characteristic.value())

    def write_characteristics(self):
        value = QByteArray(247, 0)
        characteristics = self.service.characteristics()
        print(characteristics[0].properties())
        self.service.writeCharacteristic(characteristics[0], value, QLowEnergyService.WriteWithoutResponse)

    def on_characteristic_changed(self, characteristic, value):
        print("Characteristic changed:", characteristic.uuid(), value)

    def discover_characteristics(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BLEScannerWindow()
    window.show()

    sys.exit(app.exec())