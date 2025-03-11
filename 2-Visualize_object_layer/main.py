import os
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon
import rasterio
import numpy as np
from matplotlib.path import Path
from dotenv import load_dotenv 

load_dotenv()
IMAGE_DIR = os.getenv("IMAGE_DIR")

class InteractiveLayerMover:
    def __init__(self, root, image_dir):
        self.root = root
        self.image_dir = image_dir
        self.files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
        self.index = 0

        self.image = None
        self.polygons = []  
        self.drawing_new_polygon = False  
        self.new_polygon_coords = []  
        self.class_index = "0"  # Classe padrão
        self.selected_polygon_index = None  
        self.dragging = False  
        self.drag_start = None  

        # Dicionário para mapear índices de classe para nomes
        self.class_mapping = {
            "0": "painel solar",
            "1": "piscina",
            "2": "quadra"
        }

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.create_controls()
        self.load_current_image()

        # Atalhos do teclado
        self.root.bind("<Left>", lambda e: self.prev_image())   
        self.root.bind("<Right>", lambda e: self.next_image())  
        self.root.bind("<Delete>", lambda e: self.delete_selected_polygon())  
        self.root.bind("d", lambda e: self.delete_current_image())  

        # Eventos do mouse
        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)

    def create_controls(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X)

        btn_prev = ttk.Button(control_frame, text="← Anterior", command=self.prev_image)
        btn_prev.pack(side=tk.LEFT, padx=5, pady=5)

        btn_next = ttk.Button(control_frame, text="Próxima →", command=self.next_image)
        btn_next.pack(side=tk.LEFT, padx=5, pady=5)

        btn_delete_polygon = ttk.Button(control_frame, text="Excluir Seleção", command=self.delete_selected_polygon)
        btn_delete_polygon.pack(side=tk.RIGHT, padx=5, pady=5)

        self.btn_new = ttk.Button(control_frame, text="Nova Anotação", command=self.toggle_new_polygon_mode)
        self.btn_new.pack(side=tk.LEFT, padx=5, pady=5)

        btn_delete_image = ttk.Button(control_frame, text="Excluir Imagem", command=self.delete_current_image)
        btn_delete_image.pack(side=tk.RIGHT, padx=5, pady=5)

        self.class_var = tk.StringVar(value="painel solar") 
        self.class_combobox = ttk.Combobox(control_frame, textvariable=self.class_var, values=list(self.class_mapping.values()))  # Exibe os nomes das classes
        self.class_combobox.pack(side=tk.LEFT, padx=5, pady=5)
        self.class_combobox.bind("<<ComboboxSelected>>", self.on_class_select)

    def on_class_select(self, event):
        selected_class_name = self.class_var.get()
        # Obtém o índice da classe selecionada com base no nome
        self.class_index = next(key for key, value in self.class_mapping.items() if value == selected_class_name)

    def toggle_new_polygon_mode(self):
        self.drawing_new_polygon = not self.drawing_new_polygon
        self.new_polygon_coords = []
        if self.drawing_new_polygon:
            self.btn_new.config(text="Cancelar Anotação")
        else:
            self.btn_new.config(text="Nova Anotação")
        self.plot()

    def load_current_image(self):
        if not self.files:
            return

        self.image_path = os.path.join(self.image_dir, self.files[self.index])
        self.txt_path = self.image_path.replace('.jpg', '.txt')

        if not os.path.exists(self.txt_path):
            print(f"Arquivo TXT não encontrado para {self.image_path}")
            return

        self.load_image()
        self.load_coords()
        self.plot()

    def load_image(self):
        with rasterio.open(self.image_path) as src:
            if src.count >= 3:
                self.image = np.dstack((src.read(1), src.read(2), src.read(3)))
            else:
                self.image = src.read(1)
            self.image = self.image / self.image.max()

    def load_coords(self):
        if not os.path.exists(self.txt_path):
            self.polygons = []
            return

        with open(self.txt_path, 'r') as f:
            data = f.readlines()

        self.polygons = []
        for line in data:
            parts = line.strip().split()
            class_index = parts[0]
            coords = list(map(float, parts[1:]))
            polygon_coords = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]
            self.polygons.append((class_index, polygon_coords))

    def save_coords(self):
        with open(self.txt_path, 'w') as f:
            for class_index, polygon_coords in self.polygons:
                f.write(f"{class_index} ")
                for x, y in polygon_coords:
                    f.write(f"{x:.6f} {y:.6f} ")
                f.write("\n")
        print(f"Coordenadas salvas em: {self.txt_path}")

    def plot(self):
        self.ax.clear()
        self.ax.imshow(self.image, origin='upper')
        self.ax.set_title(f"Imagem {self.index + 1}/{len(self.files)}")

        for idx, (class_index, polygon_coords) in enumerate(self.polygons):
            color = 'red' if idx != self.selected_polygon_index else 'yellow'
            polygon = Polygon(
                [(x * self.image.shape[1], y * self.image.shape[0]) for x, y in polygon_coords],
                closed=True, edgecolor=color, facecolor='none', linewidth=2
            )
            self.ax.add_patch(polygon)

        if self.drawing_new_polygon and len(self.new_polygon_coords) > 0:
            self.ax.plot(
                [x * self.image.shape[1] for x, y in self.new_polygon_coords],
                [y * self.image.shape[0] for x, y in self.new_polygon_coords],
                marker='o', color='blue', linestyle='-', linewidth=2
            )

        self.canvas.draw()

    def on_mouse_press(self, event):
        if event.inaxes != self.ax:
            return

        if self.drawing_new_polygon:
            x, y = event.xdata / self.image.shape[1], event.ydata / self.image.shape[0]

            if event.dblclick:
                if len(self.new_polygon_coords) > 2:
                    self.polygons.append((self.class_index, self.new_polygon_coords))
                    self.new_polygon_coords = []
                    self.drawing_new_polygon = False
                    self.btn_new.config(text="Nova Anotação")
                    self.save_coords()
                    self.plot()
                else:
                    print("Não é possível fechar um polígono com menos de 3 vértices.")
            else:
                self.new_polygon_coords.append((x, y))
                self.plot()
        else:
            for i, (class_index, polygon_coords) in enumerate(self.polygons):
                polygon_path = Path([(x * self.image.shape[1], y * self.image.shape[0]) for x, y in polygon_coords])
                if polygon_path.contains_point((event.xdata, event.ydata)):
                    self.selected_polygon_index = i
                    self.dragging = True
                    self.drag_start = (event.xdata, event.ydata)
                    self.plot()
                    return

    def on_mouse_move(self, event):
        if self.dragging and event.xdata and event.ydata:
            dx = (event.xdata - self.drag_start[0]) / self.image.shape[1]
            dy = (event.ydata - self.drag_start[1]) / self.image.shape[0]
            class_index, polygon_coords = self.polygons[self.selected_polygon_index]
            self.polygons[self.selected_polygon_index] = (class_index, [(x + dx, y + dy) for x, y in polygon_coords])
            self.drag_start = (event.xdata, event.ydata)
            self.plot()

    def move_selected_polygon(self, dx, dy):
        if self.selected_polygon_index is not None:
            class_index, polygon_coords = self.polygons[self.selected_polygon_index]
            self.polygons[self.selected_polygon_index] = (class_index, [(x + dx, y + dy) for x, y in polygon_coords])
            self.plot()
            self.save_coords()

    def on_key_press(self, event):
        if event.keysym == 'Up':
            self.move_selected_polygon(0, -0.01)
        elif event.keysym == 'Down':
            self.move_selected_polygon(0, 0.01)
        elif event.keysym == 'Left':
            self.move_selected_polygon(-0.01, 0)
        elif event.keysym == 'Right':
            self.move_selected_polygon(0.01, 0)

        # No método __init__, adicione o seguinte:
        self.root.bind("<KeyPress>", self.on_key_press)

    def on_mouse_release(self, event):
        self.dragging = False
        self.save_coords()

    def delete_selected_polygon(self):
        if self.selected_polygon_index is not None:
            self.polygons.pop(self.selected_polygon_index)
            self.selected_polygon_index = None
            self.save_coords()
            self.plot()

    def delete_current_image(self):
        os.remove(self.image_path)
        os.remove(self.txt_path)
        self.files.pop(self.index)
        if self.index >= len(self.files):
            self.index = max(0, len(self.files) - 1)
        self.load_current_image()

    def prev_image(self):
        """Carrega a imagem anterior na lista."""
        if self.index > 0:
            self.save_coords()
            self.index -= 1
            self.load_current_image()

    def next_image(self):
        """Carrega a próxima imagem na lista."""
        if self.index < len(self.files) - 1:
            self.save_coords()
            self.index += 1
            self.load_current_image()

def main():
    root = tk.Tk()
    root.title("Editor de Segmentação")
    app = InteractiveLayerMover(root, IMAGE_DIR)
    root.mainloop()

if __name__ == "__main__":
    main()