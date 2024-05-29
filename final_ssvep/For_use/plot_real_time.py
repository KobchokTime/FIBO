import threading
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
import flet as ft
import io
import base64

class GraphControl(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.running = False

    def did_mount(self):
        self.running = True
        self.thread = threading.Thread(target=self.update_graph, args=(), daemon=True)
        self.thread.start()

    def will_unmount(self):
        self.running = False

    def update_graph(self):
        while self.running:
            # Generate random data for the graph
            x = np.linspace(0, 10, 100)
            y = np.random.randn(100)

            # Clear the previous plot
            plt.clf()

            # Plot the new data
            plt.plot(x, y)
            plt.xlabel('X Label')
            plt.ylabel('Y Label')
            plt.title('Random Data Graph')

            # Convert the plot to base64 format
            fig = plt.gcf()
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            data = base64.b64encode(buf.read()).decode()

            # Update the graph in the UI
            self.graph_control.src_base64 = data
            self.update()
            sleep(1)

    def build(self):
        self.graph_control = ft.Image()
        return self.graph_control

def main(page: ft.Page):
    page.add(GraphControl())

ft.app(target=main)
