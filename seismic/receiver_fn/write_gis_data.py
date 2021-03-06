"""
Generates geotiffs of the interpolated moho grid and gradient,
and shapefiles of the station/method locations.
"""
import os
import json

import click
import rasterio
import shapefile
import numpy as np

from seismic.receiver_fn.write_gmt_data import format_locations


# Plate Carree CRS
CRS = rasterio.crs.CRS.from_proj4(
            "+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 "
            "+datum=WGS84 +units=m +no_defs")


def _profile(data, nx, ny, bands=1, bounds=None):
    """
    Profile for writing depth and gradient. Dtype and band count needs
    to be set depending on data.
    """
    if bounds is not None:
        l, b, r, t = bounds
    else:
        l, b = np.min(data[:,0]), np.min(data[:,1])
        r, t = np.max(data[:,0]), np.max(data[:,1])

    with rasterio.Env():
        profile = rasterio.profiles.DefaultGTiffProfile()
        transform = rasterio.transform.from_bounds(l, b, r, t, nx, ny)
        profile.update(crs=CRS, transform=transform, width=nx, height=ny,
                       count=bands, dtype=data.dtype)

    return profile


def write_depth_grid(config_file):
    """
    Writes the interpolated depth grid as a geotiff.
    """
    print("Writing depth grid geotiff")
    with open(config_file, 'r') as fr:
        config = json.load(fr)
    
    outdir = config.get('output_dir', os.getcwd())
    grid_data = os.path.join(outdir, 'moho_grid.csv')
    with open(grid_data, 'r') as fr:
        nx = int(fr.readline())
        ny = int(fr.readline())
        grid_ds = np.loadtxt(fr, delimiter=',')

    bounds = config.get('bounds')
    gtiff_profile = _profile(grid_ds, nx, ny, bands=1, bounds=bounds)

    gis_outdir = os.path.join(outdir, 'gis_data')
    if not os.path.exists(gis_outdir):
        os.mkdir(gis_outdir)

    with rasterio.Env():
        # GDAL origin is top-left, so we need to flip the data so first element is top-left cell
        data = np.flipud(grid_ds[:, 2].reshape((ny, nx)))
        gtiff_profile.update(count=1, dtype=data.dtype)
        outfile = os.path.join(gis_outdir, 'moho_grid.tif')
        with rasterio.open(outfile, 'w', **gtiff_profile) as dst:
            dst.write(data, 1)

    print(f"Complete! File saved to '{outfile}'")


def write_gradient_grid(config_file):
    """
    Writes the gradient grid as a two band raster, first band is U
    components and second band is V components.
    """
    print("Writing gradient grid geotiff")
    with open(config_file, 'r') as fr:
        config = json.load(fr)
    
    outdir = config.get('output_dir', os.getcwd())
    grad_data = os.path.join(outdir, 'moho_gradient.csv')
    with open(grad_data, 'r') as fr:
        nx = int(fr.readline())
        ny = int(fr.readline())
        grad_ds = np.loadtxt(fr, delimiter=',')

    bounds = config.get('bounds')
    gtiff_profile = _profile(grad_ds, nx, ny, bands=2, bounds=bounds)

    gis_outdir = os.path.join(outdir, 'gis_data')
    if not os.path.exists(gis_outdir):
        os.mkdir(gis_outdir)

    with rasterio.Env():
        # GDAL origin is top-left, so we need to flip the data so first element is top-left cell
        u_data = np.flipud(grad_ds[:,2].reshape((ny, nx)))
        v_data = np.flipud(grad_ds[:,3].reshape((ny, nx)))
        gtiff_profile.update(count=2, dtype=u_data.dtype)
        outfile = os.path.join(gis_outdir, 'moho_gradient.tif')
        with rasterio.open(outfile, 'w', **gtiff_profile) as dst:
            dst.write(u_data, 1)
            dst.write(v_data, 2)

    print(f"Complete! File saved to '{outfile}'")


def write_sample_locations(config_file):
    print("Writing location shapefile")
    with open(config_file, 'r') as fr:
        config = json.load(fr)
    
    outdir = config.get('output_dir', os.getcwd())
    gis_outdir = os.path.join(outdir, 'gis_data')
    if not os.path.exists(gis_outdir):
        os.mkdir(gis_outdir)

    methods = config['methods']
    for method_params in methods:
        method = method_params['name']
        outfile = os.path.join(gis_outdir, f'{method}_locations')
        w = shapefile.Writer(outfile, shapeType=1)
        w.field('WEIGHT', 'N', decimal=2)
        data = format_locations(method_params)
        for d in data:
            w.point(d[0], d[1])
            w.record(WEIGHT=d[2])
        w.close()
        # Write .prj file
        with open(f'{outfile}.prj', 'w') as prj:
            prj.write(CRS.wkt)
            
    print(f"Complete! Location shapefiles written to '{gis_outdir}'")
        
   
@click.command()
@click.argument('config-file', type=click.Path(exists=True, dir_okay=False), required=True)
@click.option('--depth', is_flag=True)
@click.option('--gradient', is_flag=True)
@click.option('--locations', is_flag=True)
def main(config_file, depth, gradient, locations):
    if depth:
        write_depth_grid(config_file)
    if gradient:
        write_gradient_grid(config_file)
    if locations:
        write_sample_locations(config_file)

if __name__ == '__main__':
    main()
