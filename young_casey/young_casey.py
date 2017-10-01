import csv

def read_csv(csv_filename):

    data = []

    # Read CSV file and store to data
    with open(csv_filename, 'rb') as csv_file:
        reader = csv.reader(csv_file)

        for row in reader:
            data.append(row)

    # Return list of headings (first CSV row) and the data
    return (data[0], data[1:])

csvfile='../crashes.csv'
 
data=read_csv(csvfile)

j=data[0].index("YOUNG_DRIVER")

XY=open("google_map.js",'w')

## Google API heat map tutorial structure:
## https://developers.google.com/maps/documentation/javascript/examples/layer-heatmap

##Out .js file largely follows this structure

string1="""var map, heatmap;
function initMap() {
  map = new google.maps.Map(document.getElementById('googleMap'), {
    zoom: 9,
    center: {lat:-37.25, lng:144}
  });
  heatmap = new google.maps.visualization.HeatmapLayer({
    data: getPoints(),
    map: map
  });
}
function toggleHeatmap() {
  heatmap.setMap(heatmap.getMap() ? null : map);
}
function changeGradient() {
  var gradient = [
    'rgba(0, 255, 255, 0)',
    'rgba(0, 255, 255, 1)',
    'rgba(0, 191, 255, 1)',
    'rgba(0, 127, 255, 1)',
    'rgba(0, 63, 255, 1)',
    'rgba(0, 0, 255, 1)',
    'rgba(0, 0, 223, 1)',
    'rgba(0, 0, 191, 1)',
    'rgba(0, 0, 159, 1)',
    'rgba(0, 0, 127, 1)',
    'rgba(63, 0, 91, 1)',
    'rgba(127, 0, 63, 1)',
    'rgba(191, 0, 31, 1)',
    'rgba(255, 0, 0, 1)'
  ]
  heatmap.set('gradient', heatmap.get('gradient') ? null : gradient);
}
function changeRadius() {
  heatmap.set('radius', heatmap.get('radius') ? null : 20);
}
function changeOpacity() {
  heatmap.set('opacity', heatmap.get('opacity') ? null : 0.2);
}
// Heatmap data: 500 Points
function getPoints() {
  return ["""

string2="""];
}"""

XY.write(string1)

for row in data[1]:
	if int(row[j])>0:
		XY.write("new google.maps.LatLng("+str(row[1])+","+str(row[0])+"),")

XY.write(string2)