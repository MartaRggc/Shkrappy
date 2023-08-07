import pylab as plt
import seaborn as sns
import re
import pandas as pd


#Ploteo de valores nulos:

def nanplot(df):  
    
    plt.figure(figsize = (10, 6))
    sns.heatmap(df.isna(),
                yticklabels = False,
                cmap ='viridis',
                cbar = False,  
                )
    plt.show()

    
# Resaltado de celdas en un dataframe
    
def yellow(df, index, cols): # Los inputs son el dataframe, una lista de índices y una lista de columnas
    
    m = pd.DataFrame('', index = df.index, columns = df.columns) # Creamos un df vacío de iguales dimensiones
    for i,col in zip(index,cols):
        m.loc[i, col] = 'background-color: yellow' # En las celdas indicadas, guardamos el style amarillo

    styled_df = df.style.apply(lambda x: m, axis = None) # Aplicamos el styling de 'm' al dataframe 

    return styled_df
   
   
 
# Función de análisis inicial de un dataframe desconocido, printea información básica
   
def firstglance(df):
    
    display(df.head())
    print("\nShape:",df.shape)
    print("\nNull values count:\n")
    print(df.isna().sum())
    print("\nTable info:\n")
    display(df.info())


# Función de scrapeado de posts de reddit:

def extract(post):
    
    try:
        date = post.get_attribute('created-timestamp').split('T') # Partimos la fecha por la T
        time = pd.to_datetime(date[1].split('.')[0]).time() # La segunda parte es la hora UTC
        day = pd.to_datetime(date[0]).date() # La segunda parte es la fecha
        title = post.get_attribute('post-title') # Sacamos el título del post
        
        try: # Esta parte es para obtener la url de los posts que tengan una imagen 
            link = post.find_elements(By.TAG_NAME, 'faceplate-img')[1].get_attribute('src')
            return [day,time,title,link]
        except:
            return [day,time,title] # Por si no hay imagen
    except:
        print('Oups! Something went wrong.')


# Función de scrolling y scrapeado global de reddit:

def scrappy(url):
    
    # Establecemos unos índices para el scrolleo contando el número de posts que podemos ver en la página:
    
    oldlen = 0
    newlen = 1
    newposts = newlen > oldlen 
    
    # Abrimos el navegador y buscamos los posts:
    
    driver = webdriver.Chrome(PATH)    
    driver.get(url)    
    posts = driver.find_elements(By.TAG_NAME, 'shreddit-post') # Busca los posts
    
    # Scrolling todo lo que podamos, hasta que no cambie el último post que encontremos:

    while newposts: 
        oldlen = newlen # Guardamos los posts que podemos ver ahora.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scrolleamos hasta abajo.
        time.sleep(3) # Esperamos a que cargue.
        posts = driver.find_elements(By.TAG_NAME, 'shreddit-post') # Buscamos de nuevo los posts.
        newlen = len(posts) # Contamos cuantos hay.
        newposts = newlen > oldlen # Miramos si hay los mismos que antes de scrollear, y si no repetimos proceso.
                 
    print('Scroll completed.') 
    
    # Ahora usamos extract para extraer los datos de los posts totales que hemos conseguido.
    # Los guardamos en un dataframe, le ponemos nombre a las columnas y cerramos el navegador:
    
    data = pd.DataFrame([extract(i) for i in posts])
    try:
        data.columns = ['date','time','title']
    except:
        data.columns = ['date','time','title','link']
        
    driver.quit()

    return data


# Versión para posts con datos dentro de shadows (al final no me ha hecho falta, pero es interesante conservarla):


def shadowscrappy(url):

    
    oldlen = 0
    newlen = 1
    newposts = newlen > oldlen    
        
    driver = Shadow(webdriver.Chrome(PATH)) # Ahora abriremos el driver con el paquete pyshadow
    driver.chrome_driver.get(url) 
    posts = driver.find_elements('shreddit-post')
        
    while newposts: # Scrolling
        oldlen = newlen
        driver.scroll_to(posts[-1]) # Scrolleamos hasta el último post con este método propio de objetos shadow
        time.sleep(3)
        posts = driver.find_elements('shreddit-post') 
        newlen = len(posts)   
        newposts = newlen > oldlen
            
    print('Scroll completed.')
    
    data = pd.DataFrame([extract(i) for i in posts])
    try:
        data.columns = ['date','time','title','link']
    except:
        data.columns = ['date','time','title']

    return data


# Función para contar y normalizar los registros de un dataframe según intervalos horarios predefinidos:

def timegroup(df):
    
    rows = []
    
    for i in days: # Por cada día distinto
        for j in range(len(hours)-1): # Y cada intervalo horario
            row = [i,str(hours[j].time()),df[(df.date == i)&\
                                 (df.time>str((hours[j]-timedelta(hours=0.5)).time()))&\
                                 (df.time<str((hours[j+1]+timedelta(hours=0.5)).time()))].shape[0]] # Contamos
            
            # Límites:
            if str(row[0]) == cutdate1 and str(row[1]) < cuthour11 or str(row[0]) == cutdate2 and str(row[1]) > cuthour22: 
                continue
            else:
                rows.append(row) # Si está dentro de las franjas que nos interesan, guardamos la fila
        
    data = pd.DataFrame(rows)
    data[2] = data[2].apply(lambda x: int(100*x/max(data[2]))) # Normalizamos la actividad
    data.columns = ['date','time','activity']
    
    return data