import numpy as np
import geopandas as gpd
from geokrige.methods import SimpleKriging
from geokrige.tools import TransformerGDF
from matplotlib import pyplot as plt 
import io
import base64
import matplotlib
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
import zipfile
import tempfile

matplotlib.use("agg")
load_dotenv()


class Interpolate:
    def __init__(self) -> None:
        pass

    def get_shapeFile(self, shape_file_path : str) -> gpd.GeoDataFrame:
        try:
            gdf = gpd.read_file(shape_file_path)            
            return gdf.set_crs(epsg=32736)

        except(Exception):
            print(Exception)

    def convert(self):
        buf = io.BytesIO()
        plt.savefig(buf, format = "png",bbox_inches='tight', pad_inches=0.5)   
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')  
        buf.close()
        plt.close()
        return {"answer": img_base64,"type" : "image"}
    
    def interpolate(self, bins: int, data: list, shapefile_path: str, contour_map: bool = True, crs: int = 4326, report: bool = False, email: str = "file/to/extract", title: str = "", model: str = "exp"):
        data = np.array(data)
        latitudes = data[:, 0]
        longitudes = data[:, 1]
        values = data[:, 2]

        x_input = np.column_stack([longitudes, latitudes])
        krigging_model = SimpleKriging()
        krigging_model.load(X=x_input, y=values)
        krigging_model.variogram(bins=2)
        krigging_model.fit(model=model)
        z = []
        z.append(self.convert())

        initial_geoDataFrame = self.download_shapefile_to_generate_geo_dataframe(shapefile_path)
        final_geoDataFrame = initial_geoDataFrame.to_crs(epsg=crs)

        transformer = TransformerGDF()
        transformer.load(final_geoDataFrame)
        meshgrid = transformer.meshgrid(density=1)
        mask = transformer.mask()

        interpolated_values = krigging_model.predict(meshgrid)
        new_x, new_y = meshgrid
        interpolated_values[~mask] = None

        fig, ax = plt.subplots(figsize=(10, 10))
        final_geoDataFrame.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1, zorder=6)
        if contour_map:
            cbar = ax.contourf(new_x, new_y, interpolated_values, cmap='jet')
            fig.colorbar(cbar)
        else:
            cbar = ax.pcolormesh(new_x, new_y, interpolated_values, cmap='jet')
            fig.colorbar(cbar)
        z.append(self.convert())
        if report:
            stats = krigging_model.evaluate(groups=bins, return_=True)
            report = self.createReport(title, stats=stats)
            print(333)
            plt.close()
            print(report)
            return {"array": z, "report": report}
        plt.close()
        return {"array": z, "report": ""}

    def createReport(self, title: str, stats: str) -> str:
        try:
            print("starting report")
            api_key = os.getenv("GEMINI_API_KEY")
            print(api_key, " key")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"write a field report about {title} with these stats : {stats}")
            return f"{response.text}"
        except Exception as e:
            print(e)
            return "Failed to generate"

    def downdload_shapefile(self, path: str, destination: str):
        response = requests.get(path)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                if not os.path.exists(destination):
                    os.makedirs(destination)
                z.extractall(destination)  # Extract all contents
            return self.find_shapefiles(destination)
        else:
            raise Exception(f"Failed to download file. Status code: {response.status_code}")

    def find_shapefiles(self, directory: str):
        shp_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.shp'):
                    shp_files.append(os.path.join(root, file))
        return shp_files
    

    def download_shapefile_to_generate_geo_dataframe(self,path : str):
        response = requests.get(path)
        response.raise_for_status()
        zip_file = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_file) as z:
            with tempfile.TemporaryDirectory() as tmpdir:               
                z.extractall(path=tmpdir) 
                shapefile_path = next(
                    os.path.join(tmpdir, name) for name in os.listdir(tmpdir) if name.endswith('.shp')
                )
                gdf = gpd.read_file(shapefile_path)
                return gdf.set_crs(epsg=32736)
