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
    
    def interpolate( self,bins : int, email:str, data : list, shapefile_path : str,contour_map : bool = True,crs : int = 4326, report :bool = False,title : str = "",model : str = "exp"):
        data = np.array(data)
        latitudes = data[:,0]
        longitudes = data[:,1]
        values = data [:,2]

        x_input = np.column_stack([longitudes,latitudes])
        krigging_model = SimpleKriging()
        krigging_model.load(X=x_input,y=values)
        krigging_model.variogram(bins=2)
        krigging_model.fit(model=model)
        z = []
        z.append(self.convert())
        plt.savefig("zz.png")
        
        initial_geoDataFrame = self.get_shapeFile(self.downdload_shapefile(shapefile_path,f"shapefiles/{email}"))
        final_geoDataFrame = initial_geoDataFrame.to_crs(epsg=crs)

        transformer = TransformerGDF()
        transformer.load(final_geoDataFrame)
        meshgrid = transformer.meshgrid(density=1)
        mask = transformer.mask()

        interpolated_values = krigging_model.predict(meshgrid)
        new_x, new_y = meshgrid
        interpolated_values[~mask] = None
        
        fig, ax = plt.subplots(figsize=(10,10))
        final_geoDataFrame.plot(ax=ax, facecolor='none',edgecolor='black',linewidth=1,zorder=6)
        if(contour_map):
            cbar = ax.contourf(new_x,new_y,interpolated_values,cmap='jet')
            fig.colorbar(cbar)
        else:
             cbar = ax.pcolormesh(new_x,new_y,interpolated_values,cmap='jet')
             fig.colorbar(cbar)   
        z.append(self.convert())
        if(report):
            print("222222222222\n\n\n\n\n\\n\n\n\n\n\n\n")
            stats = krigging_model.evaluate(groups=bins, return_=True)
            report = self.createReport(title,stats=stats)
            print(333)
            plt.close()
            print(report)
            return {"array":z, "report" : report}
        plt.close()
        return {"array":z, "report" : ""}
       # fig.savefig("out.png")

    def createReport(self,title : str, stats : str)->str:
        try:
            print("starting report")
            api_key = os.getenv("GEMINI_API_KEY")
            print(api_key, " key")
            genai.configure(api_key= api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"write a field report about {title} with these stats : {stats}")
            return f"{response.text}"
        except Exception:
            print(Exception)
           # return "Failed to generate"
    def downdload_shapefile(self,path : str, destination : str):
        response = requests.get(path)
        if response.status_code == 200 :
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extract(destination)
                return self.find_shapefiles(destination)


    def find_shapefiles(self,directory : str):
        shp_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.shp'):
                    shp_files.append(os.path.join(root, file))
        return shp_files
        
        

    
# def IDW(data: List[List[float]], target : List[float]) -> List[float]:
#     if len(data) < 1:
#         raise ValueError("Input data cannot be empty.")
#     if len(target) != 2:
#         raise ValueError("Target must have two elements")

#     data = np.array(data, dtype = float)
#     target = np.array(target, dtype = float)

#     if data.ndim != 2 or data.shape[1] != 3 or target.ndim != 1 :
#         raise ValueError(f"Input data should be of shape (*, 3), target should be of shape (*) but found data = {data.shape} and target = ({target.shape})")


#     # initializing the list of distance from target to data emelents using pythagorus theorem
#     distance = []
#     for sublist in data:
#         distance.append(math.sqrt((math.pow(sublist[0]-target[0],2) + math.pow(sublist[1]-target[1],2))))

#     #calculating weights
#     inverse_distance = 1/np.array(distance)
#     sum_of_inverse_distance = np.sum(inverse_distance)
#     normalized_inverse_distance = inverse_distance / sum_of_inverse_distance
#     weights = []
#     for sublist in data:
#         weights.append(sublist[-1])
#     prediction =np.sum( weights * normalized_inverse_distance)

#     return [[i for i in target], prediction]