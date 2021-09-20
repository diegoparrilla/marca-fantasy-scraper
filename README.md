# Marca Fantasy Scraper

Web scraper del API de LaLiga Fantasy de Marca. Descarga la información existente en la Liga Fantasy Marca sobre los equipos y jugadores de la temporada. 

# Cómo funciona
Necesitas tener instalado en tu equipo Python version 3. El programa scraper.py creará un directorio llamado laliga, y dentro de este directorio encontraremos un directorio por cada equipo y dos ficheros CSV con información sobre los jugadores e información detallada del rendimiento de cada jugador.

## Directorios de los equipos
Dentro de cada directorio por equipo se creará un fichero JSON con la información detallada de cada jugador. Cada vez que se ejecute el programa scraper.py, esta información se sobreescribirá.

## Fichero players.csv
Este fichero contiene la información de cada jugador por línea. Cada jugador tiene su puntuación en la fantasy de la semana. Cada vez que se ejecute el programa scraper.py, esta información se sobreescribirá.

## Fichero players-performance.csv
Este fichero contiene la información de cada jugador y jornada por línea. Cada jugador y jornada tiene el detalle de su rendimiento en la fantasy de la semana. Cada vez que se ejecute el programa scraper.py, esta información se sobreescribirá.

# Instalación
## Librerías necesarias
El programa scraper.py necesita la librería requests, por lo que debe instalarse con anterioridad:

pip install -r requirements

# Ejecución
Para ejecutar el programa, solo hay que invocar scraper.py

python scraper.py 

o 

python3 scraper.py



