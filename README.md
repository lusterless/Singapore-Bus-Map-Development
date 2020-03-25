# Punggol-Map-Development

This map uses an A* algorithm to reduce the time complexity for calculating each route. A* algorithms are build from dijkstra with enhancement using priority queue and heuristics. In order to further improve the time complexity of accessing each nodes and edges, a DOUBLE HASH table is used to achieve an O(1) complexity.
- [x] Drive
- [x] Bus
- [x] Walk
- [x] LRT

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Using [pip](https://pip.pypa.io/en/stable/) install:
* **These are the main dependencies, there could be other smaller dependencies such as math modules, time module**
```
pip install django
```
```
pip install django-Leaflet
```
* Nodes and edges Files can be found in [Django\map\webmap\data](https://github.com/lusterless/Singapore-Bus-Map-Development/tree/master/Django/map/webmap/data)
```
pip install json
```
```
pip install geopy 
```
* OSMnx is built on top of geopandas, networkx, and matplotlib. Please ensure that you have these dependencies installed before attempting to install OSMnx.
```
pip install osmnx
```
* If you have any trouble installing OSMnx, pip install all files [here](whlfiles) and
```
pip install geopandas
```
```
pip install networkx
```
```
pip install matplotlib
```
* Alternatively, you may read OSMnx docs [here](https://osmnx.readthedocs.io/en/stable/)


## Running the tests

Using cmd, cd "Django\map"
```
cd "Django\map"
```
Run Django-Webserver
```
python manage.py runserver
```
![capture1](https://user-images.githubusercontent.com/57383960/77459367-97abd200-6e3a-11ea-93c9-af2791d3b68f.JPG)

## Deployment

Go to your browser and enter [URL](127.0.0.1:8000/map)
```
127.0.0.1:8000/map
```

## Built With

* [Python3](https://www.python.org/downloads/) - Language used
* [Django](https://www.djangoproject.com/download/) - The web framework used
* [Django-Leaflet](https://pypi.org/project/django-leaflet/) - Web framework design
* [OSMnx](https://osmnx.readthedocs.io/en/stable/) - Used to generate graphs
* [Geopy](https://pypi.org/project/geopy/) - Reverse geocode


## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Koh Kai Quan** - *Initial work* - [Lusterless](https://github.com/lusterless)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
