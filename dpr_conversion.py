import subprocess
import re
import os
import numpy as np
from osgeo import gdal

input_file = "/Users/judson/Downloads/2A.GPM.DPR.V9-20211125.20200214-S182040-E195315.033884.V07A.HDF5"
subdataset_path = "//FS/CSF/flagShallowRain"
output_file = '/Users/judson/Desktop/test.tif'

try:
    result = subprocess.run(
        ["gdalinfo", f"HDF5:{input_file}:{subdataset_path}"],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout
except subprocess.CalledProcessError as e:
    print("Error running gdalinfo:", e)
    print("Output:", e.output)
    exit(1)

gcps = []
gcp_pattern = r'\((\d+\.\d+),(\d+\.\d+)\) -> \(([\d\.-]+),([\d\.-]+),\d+\)'

matches = re.findall(gcp_pattern, output)

gcps = []
for match in matches:
    pixel, line, lon, lat = map(float, match)
    gcps.append({"pixel": pixel, "line": line, "lon": lon, "lat": lat})

xmin = min(item['lon'] for item in gcps)
xmax = max(item['lon'] for item in gcps)
ymin = min(item['lat'] for item in gcps)
ymax = max(item['lat'] for item in gcps)

gcps_gdal = []
for gcp_dict in gcps:
    # Create a gdal.GCP object from each dictionary entry
    gcp = gdal.GCP(
        gcp_dict['lon'],  # Longitude (GCPX)
        gcp_dict['lat'],  # Latitude (GCPY)
        0,                # Elevation (optional, default 0)
        gcp_dict['pixel'],  # Pixel (GCPPixel)
        gcp_dict['line']    # Line (GCPLine)
    )
    gcps_gdal.append(gcp)

gcps = gcps_gdal
#cps_gdal = [gdal.GCP(lon=i['lon'], lat=i['lat'], x=)]

# Open the input image (a satellite swath)
#dataset = gdal.Open(input_file)

# Apply GCPs to the image
#dataset.SetGCPs(gcps, gdal.GCPsToGeoTransform(gcps))

# Apply the correct projection (if it's in a non-WGS84 format, use the specific one)
#dataset.SetProjection("EPSG:4326")  # WGS84 Lat/Lon (if it's in WGS84, adjust if not)

# Save the image with applied GCPs and transformation
#gdal.Translate(output_file, dataset, format='GTiff')
input_filepath = f'HDF5:{input_file}:{subdataset_path}'
gdal_warp = f'gdalwarp -t_srs EPSG:4326 -te {xmin} {ymin} {xmax} {ymax} {input_filepath} {output_file}'

os.system(gdal_warp)
## Reproject image to desired projection (if needed, e.g., UTM)
#gdal.Warp('reprojected_output.tif', dataset, dstSRS="EPSG:32633")  # UTM for example
