import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import threading
import numpy as np

class SerialPlotter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LiveECG")
        self.geometry("800x600")

        self.serial_port = None
        self.baud_rate = 115200
        self.running = False
        self.max_points = 300  # maximum number of points on the plot
        self.data = np.array([])

        self.setup_ui()
        self.create_plot()
        
        self.data_filter = DataFilter()

    def setup_ui(self):
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill='x', padx=10, pady=10)

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(controls_frame, textvariable=self.port_var)
        self.port_combo['values'] = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.set('Select COM Port')
        self.port_combo.grid(row=0, column=0, padx=5, pady=5)

        self.start_button = ttk.Button(controls_frame, text="Start Plotting", command=self.start_plotting)
        self.start_button.grid(row=0, column=1, padx=5, pady=5)

        self.stop_button = ttk.Button(controls_frame, text="Stop Plotting", command=self.stop_plotting)
        self.stop_button.grid(row=0, column=2, padx=5, pady=5)

    def create_plot(self):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')  # 'r-' specifies a red line
        self.ax.set_xlim(0, self.max_points - 1)
        
        # Setting grid
        self.ax.grid(True)  # Enable the grid
        self.ax.set_axisbelow(True)  # Draw gridlines below plot elements
        
        # Optional: Customize grid appearance
        self.ax.grid(color='gray', linestyle='--', linewidth=0.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_plotting(self):
        if self.running:
            return
        self.running = True
        port = self.port_var.get()
        self.serial_port = serial.Serial(port, self.baud_rate)
        self.thread = threading.Thread(target=self.read_from_port, daemon=True)
        self.thread.start()

    def stop_plotting(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def read_from_port(self):
        try:
            while self.running:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line.isdigit():
                    adc_value = int(line)
                    filtered_value = self.data_filter.apply_filter(adc_value)
                    self.data = np.append(self.data, filtered_value)
                    if len(self.data) > self.max_points:
                        self.data = self.data[-self.max_points:]
                    self.update_plot()
        except Exception as e:
            print("Error reading from serial port:", e)

    def update_plot(self):
        # Auto-adjust the y-axis limits
        if len(self.data) > 0:
            y_min, y_max = self.data.min(), self.data.max()
            y_range = y_max - y_min
            self.ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

        self.line.set_data(np.arange(len(self.data)), self.data)
        self.canvas.draw()
        self.canvas.flush_events()

class DataFilter:
    def __init__(self):
        self.order = 3
        self.fs = 200.0  # Sample rate, Hz
        self.cutoff = 50.0  # Desired cutoff frequency of the filter, Hz
        self.b, self.a = butter(self.order, self.cutoff / (0.5 * self.fs), btype='low', analog=False)
        self.previous_data = np.array([])

    def apply_filter(self, data_point):
        self.previous_data = np.append(self.previous_data, data_point)
        if len(self.previous_data) > self.order:
            self.previous_data = self.previous_data[-(self.order+1):]
        filtered_data = lfilter(self.b, self.a, self.previous_data)
        return filtered_data[-1] if len(filtered_data) > 0 else data_point

if __name__ == "__main__":
    app = SerialPlotter()
    app.mainloop()