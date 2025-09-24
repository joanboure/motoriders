import gpxpy
import matplotlib.pyplot as plt
import contextily as ctx
import pyproj
import os

def gpx_to_png(gpx_file, png_file):
    with open(gpx_file, 'r') as f:
        gpx = gpxpy.parse(f)
    lats, lons, alts = [], [], []
    wp_lats, wp_lons = [], []
    total_distance = 0.0
    total_ascent = 0.0

    for track in gpx.tracks:
        for segment in track.segments:
            prev_point = None
            for point in segment.points:
                lats.append(point.latitude)
                lons.append(point.longitude)
                alts.append(point.elevation)
                if prev_point:
                    total_distance += point.distance_3d(prev_point)
                    delta_alt = point.elevation - prev_point.elevation
                    if delta_alt > 0:
                        total_ascent += delta_alt
                prev_point = point

    # Waypoints
    for wp in gpx.waypoints:
        wp_lats.append(wp.latitude)
        wp_lons.append(wp.longitude)

    # Convertir a Web Mercator (EPSG:3857)
    proj = pyproj.Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    x, y = proj.transform(lons, lats)
    if wp_lons and wp_lats:
        x_wp, y_wp = proj.transform(wp_lons, wp_lats)
    else:
        x_wp, y_wp = [], []

    plt.figure(figsize=(10, 8))
    plt.plot(x, y, 'b-', linewidth=2)
    if x_wp and y_wp:
        plt.scatter(x_wp, y_wp, marker='*', color='red', s=150, label='Waypoints')
    plt.axis('equal')
    plt.axis('off')
    ax = plt.gca()
    ctx.add_basemap(ax, crs="epsg:3857", source=ctx.providers.OpenStreetMap.Mapnik)

    filename = os.path.basename(gpx_file)
    km = total_distance / 1000
    ascent = total_ascent
    text = f"{filename}\nDistancia: {km:.1f} km\nAscenso acumulado: {ascent:.0f} m"
    plt.text(0.01, 0.99, text, transform=ax.transAxes, fontsize=12,
             verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    plt.savefig(png_file, bbox_inches='tight', pad_inches=0)
    plt.close()

# Procesar todos los archivos GPX en la carpeta 'gpx' y generar readme.md
gpx_folder = 'gpx'
md_filename = 'readme.md'
entries = []

for filename in os.listdir(gpx_folder):
    if filename.lower().endswith('.gpx'):
        gpx_path = os.path.join(gpx_folder, filename)
        png_path = os.path.splitext(gpx_path)[0] + '.png'
        gpx_to_png(gpx_path, png_path)
        name = os.path.splitext(filename)[0]
        github_path = f"https://github.com/joanboure/motoriders/gpx/{name}"
        entry = f"### {name}\n\n![{name}]({github_path}.png)\n\n[Descargar GPX]({github_path}.gpx)\n"
        entries.append(entry)

with open(md_filename, 'w', encoding='utf-8') as md_file:
    md_file.write("# Motoriders\n\n")
    md_file.write("\n---\n".join(entries))