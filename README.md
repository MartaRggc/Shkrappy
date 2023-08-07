# Shkrappy

<p align="center">
  <img src="images/scrappy.png">
</p>

_Image source: https://www.reddit.com/r/Shrek/_

# Intro

En este primer proyecto completo de ETL (Extract-Transform-Load) he recogido y procesado datos de la actividad de posteo en varios foros de reddit, así como buscado información adicional que pudiera ser de interés para posteriores análisis. Para ello utilicé tres fuentes y dos métodos:

+ Scrapeo de los posts de los subreddits r/programming, r/memes, r/science, r/relationships, r/usa, r/canada y r/unitedkingdom vía Selenium
+ Scrapeo de una tabla de uso mayoritario de reddit por países ([semrush](https://www.semrush.com/website/reddit.com/overview/)) vía BeautifulSoup
+ Descarga de datos de búsqueda de noticias locales desde Google Trends, en Estados Unidos, Canadá e Inglaterra, en los últimos 7 días

El planteamiento general es obtener información interesante sobre la frecuencia de posteo en los subreddits elegidos, cuya densidad de usuarios es bastante grande (al menos 30k y en general más de 1M). Para ello he ido guardando el título, fecha, hora y url de la imagen (si la había) de cada post encontrado, scrolleando la página hasta llegar al límite fijado por reddit que varía según el foro. Reddit [no permite un scrolling infinito desde hace varios años](https://www.reddit.com/r/help/comments/1184gxn/scroll_down_limit/), por lo que he recogido todos los posibles para luego quedarme con una franja temporal común a todos.

La frecuencia de posteo podría ser útil de cara a diseñar estrategias publicitarias concretas para los distintos foros. Para complementar esta información, he buscado datos de actividad de búsqueda desde Google Trends, tomando la búsqueda de noticias locales como referencia (para otro tipo de búsqueda las curvas eran similares). Me he descargado los csv. correspondientes a Estados Unidos, Canadá e Inglaterra, que según la tabla scrapeada de semrush son los tres países mayoritarios en reddit.

Una posterior comparación entre ambos sets de datos podría permitirnos tantear si los porcentajes indicados por la tabla de samrush son plausibles, ya que la fecha y hora de posteo están expresadas en hora UTC y no nos dan información sobre el país de origen de cada post.

El proceso está desarrollado en 5 cuadernos de jpynb:

## 1.Reddit_scrapping

La idea es sacar el mayor número de posts posibles, guardando el título, la fecha y hora de publicación y la url de la imagen si la hay. Por suerte o por desgracia (imagino que es por esto por lo que hay un límite de entradas a mostrar), aunque las de reddit sean páginas dinámicas, los posts superiores no desaparecen cuando se scrollea hacia abajo para cargar los siguientes. Por ese motivo la función creada para scrapear scrollea primero lo máximo posible y sólo extrae los datos cuando ya no puede hacerlo más (cuando, tras scrollear, no ve posts nuevos).

Para todo el proceso he creado dos funciones:

+ extract: recibe un post concreto y extrae la información relevante.

+ scrappy: scrollea todo lo posible el subreddit de la url indicada, guarda los posts una vez acaba y que luego llama a extract para extraer la información de todos ellos y guardarla en un dataframe.


Una vez definidas, he utilizado joblib para paralelizar el proceso y poder scrapear todos los subreddits a la vez. Una vez recogidos los datos los he guardado en formato csv. en la carpeta 'reddit' dentro de 'data'.

![reddit](images/reddit.png)

## 2.Semrush_scrapping

El scrapeo de la tabla de semrush fue mucho más sencillo, ya que la información estaba en una única tabla accesible a través del html. Usando BeautifulSoup el proceso es directo, y una vez guardado el dataframe correspondiente lo he pasado a csv. y almacenado en 'redditusage' dentro de 'data'.

Hubiera sido interesante contar con la tabla completa de uso de reddit por países, ya que la vista previa sólo nos enseña los primeros mayoritarios. Aún así es información útil y nos servirá para sacar alguna conclusión preliminar.

![semrush](images/sem.png)


## 3.Processing_csv

Una vez recogidos los datos (los de Google Trends simplemente los descargué en formato csv. y los guardé en 'data/google_trends'), llegó el turno de procesarlos para preparar la subida a la base de datos y el análisis posterior. 

+ Tablas de subreddits: simplemente rellené los nulos que había en la columna de los links de imagen por 'no-image', ya que por el método de scrapeo estaban ya limpios en sí.
+ Tablas de Googe Trends: cambié las horas registradas por la hora internacional, ya que al descargar los datos te los proporciona según tu hora local y si no no podríamos comparar con las tablas de reddit.
+ Tabla de uso por países: ya le había retocado el formato tras el scrapeo, por lo que no quedaba más por hacer.

Por último, creé una función de agrupación por franja horaria para contar y normalizar el número de posts por hora a lo largo de los días, y poder medir la actividad en las tablas de reddit. Utilizando esta función, la apliqué sobre las tablas de los subreddits recortadas (quería la misma franja temporal en todas para poder comparar) y la uní a los datos de Google Trends, también recortados a la misma franja temporal. El resultado fue un dataframe que llamé 'activity' y que también subiré a la base de datos.

![activity](images/activity.png)


## 4.Mongo_loading

Para subir los datos a Mongo, importamos los csv y los transformamos en diccionarios. Una vez hecho eso, creamos la database desde jupyter notebook utilizando la librería pymongo, y la llenamos.

![mongodb](images/mongodb.png)


## 5.Data_analysis

