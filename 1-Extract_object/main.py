import os
import ezdxf
from collections import defaultdict
from shapely.geometry import Polygon, LineString, box
import rasterio
from rasterio.mask import mask
from rasterio.transform import rowcol
import numpy as np
from dotenv import load_dotenv 

load_dotenv()
ORTO_DIR = os.getenv("ORTO_DIR")
DXF_DIR = os.getenv("DXF_DIR")
OUTPUT_PATH = os.getenv("OUTPUT_PATH")

# Camadas de interesse
layers_interest = ['PAINEL_FOTOVOLTAICO_2023', 'QUADRA_ESPORTES_TOPONIMIA_2016', 'QUADRA_ESPORTES_TOPONIMIA_2023', 'PISCINA_TOPONIMIA_2016', 'PISCINA_2023']

# Mapeamento de classes agrupadas
class_group_mapping = {
    'PAINEL_FOTOVOLTAICO_2023': 0,
    'PISCINA_TOPONIMIA_2016': 1,  # Grupo PISCINA
    'PISCINA_2023': 1,  # Grupo PISCINA
    'QUADRA_ESPORTES_TOPONIMIA_2016': 2,  # Grupo QUADRA_ESPORTES
    'QUADRA_ESPORTES_TOPONIMIA_2023': 2  # Grupo QUADRA_ESPORTES
}


def process_directories(orto_dir, dxf_dir, output_path):
    cont = 0
    for file_name in os.listdir(orto_dir):
        if file_name.endswith('.tif'):
            orto_path = os.path.join(orto_dir, file_name)
            tfw_path = os.path.join(orto_dir, file_name.replace('.tif', '.tfw'))

            if not os.path.exists(tfw_path):
                print(f"Arquivo .tfw correspondente não encontrado para {file_name}. Ignorando...")
                continue

            dxf_path = os.path.join(dxf_dir, file_name.replace('.tif', '.dxf'))
            if not os.path.exists(dxf_path):
                print(f"Arquivo .dxf correspondente não encontrado para {file_name}. Ignorando...")
                continue
            
            export_region_from_layer(orto_path, tfw_path, dxf_path, output_path, layers_interest, cont)
        cont = cont + 1


def read_tfw(tfw_path):
    with open(tfw_path, 'r') as f:
        lines = f.readlines()
        transform = [float(line.strip()) for line in lines]
    return rasterio.Affine.from_gdal(*transform)


def read_dxf_and_extract_geometries(dxf_path, layers_interest):
    dxf = ezdxf.readfile(dxf_path)
    models = dxf.modelspace()
    layer_entities = defaultdict(list)

    for entity in models:
        layer_name = entity.dxf.layer
        if layer_name in layers_interest and entity.dxftype() != 'TEXT':
            try:
                if entity.dxftype() == 'POLYLINE':
                    points = [(point.x, point.y) for point in entity.points()]
                    polygon = Polygon(points) if len(points) > 2 else LineString(points)
                    if polygon.is_valid:
                        layer_entities[layer_name].append(polygon)

                elif entity.dxftype() == 'LWPOLYLINE':
                    points = [(point[0], point[1]) for point in entity.vertices()]
                    polygon = Polygon(points) if len(points) > 2 else LineString(points)
                    if polygon.is_valid:
                        layer_entities[layer_name].append(polygon)
            except Exception as e:
                print(f"Erro ao processar entidade na camada {layer_name}: {e}")

    return layer_entities


def expand_region(region, margin_percentage):
    minx, miny, maxx, maxy = region.bounds
    width = maxx - minx
    height = maxy - miny
    margin_x = width * margin_percentage
    margin_y = height * margin_percentage
    return box(minx - margin_x, miny - margin_y, maxx + margin_x, maxy + margin_y)


# Calcula as coordenadas normalizadas
def save_normalized_coordinates(txt_path, region, out_transform, class_index, cropped_width, cropped_height):
    pixel_coords = []
    for x, y in region.exterior.coords:
        row, col = rowcol(out_transform, x, y)
        norm_x = col / cropped_width  
        norm_y = row / cropped_height
        pixel_coords.append((norm_x, norm_y))

    with open(txt_path, "w") as f:
        f.write(f"{class_index} ")
        for norm_x, norm_y in pixel_coords:
            f.write(f"{norm_x} {norm_y} ")
        f.write("\n")

    print(f"Arquivo .txt gerado: {txt_path}")


def export_region_from_layer(orto_path, tfw_path, dxf_path, output_dir, layers_interest, cont, margin_percentage=0.4):
    transform = read_tfw(tfw_path)
    layer_entities = read_dxf_and_extract_geometries(dxf_path, layers_interest)

    with rasterio.open(orto_path) as orto:
        for layer_name, geometries in layer_entities.items():
            for i, region in enumerate(geometries):
                try:
                    expanded_bounds = expand_region(region, margin_percentage)

                    # Expande a região para imagens de 640x640
                    out_image, out_transform = mask(orto, [expanded_bounds], crop=True)
                    cropped_width = out_image.shape[2]  
                    cropped_height = out_image.shape[1] 

                    if cropped_width < 640:
                        difference = 640 - cropped_width
                        cropped_width_yolo = cropped_width + difference

                    if cropped_height < 640:
                        difference = 640 - cropped_height
                        cropped_height_yolo = cropped_height + difference

                    out_meta = orto.meta.copy()
                    out_meta.update({
                        "driver": "GTiff",
                        "height": cropped_height_yolo,
                        "width": cropped_width_yolo,
                        "transform": out_transform
                    })

                    output_path = os.path.join(output_dir, f"{layer_name}_region_{cont}_{i+1}.jpg")
                    os.makedirs(output_dir, exist_ok=True)
                    with rasterio.open(output_path, "w", **out_meta) as dest:
                        dest.write(out_image)

                    # Pega o de-para layer-index
                    class_index = class_group_mapping[layer_name]

                    txt_path = os.path.join(output_dir, f"{layer_name}_region_{cont}_{i+1}.txt")
                    save_normalized_coordinates(
                        txt_path, region, out_transform, class_index,
                        cropped_width, cropped_height
                    )

                except Exception as e:
                    print(f"Erro ao processar a camada '{layer_name}', região {i+1}: {e}")


if __name__ == "__main__":
    process_directories(ORTO_DIR, DXF_DIR, OUTPUT_PATH)