# CyanBot
Un bot creado para guardar rabajos relizados por usuarios de discord.

> **Warning**  
> Este branch no es master / main!.  Sus textos se encuentran en portugues

## ¿Qué Hace?
Este bot, por el momento, cumple estas funcionalidades:
- Actualizar un canal de discord con los últimos mangas subidas al link en `config.json`.
- Contabilizar, almacenar y establecer el dinero de los trabajos realizados por el equipo de traducción y de administración de mangas en el bot.

Para más detalles leer la sección **"¿Cómo Funciona?"** más abajo.

---

## Clonar el Repositorio
En una carpeta ejecutar
```bash
git clone https://github.com/CodeINN95612/CyanBot.git
```
---

## Ejecucion
Se debe instalar los requerimientos con
```bash
pip install -r requirements.txt
```
Luego se puede ejecutar con
```bash
py CyanBot.py
```

La primera ejecución es posible que falle con el error:
```txt
El archivo de configuración no existe.
Por favor llena el archivo 'data/config.json' que fue creado con los valores correspondientes
```
Se debe llenar el archivo 'data/config.json' que fue creado (o crearlo) y debe seguir este formato: *Se explica como llenar mas abajo)
```json
{
    "token": "",
    "prefix": "$",
    "discordDelay": 300,
    "updateLink": "",
    "updateDelay": 300,
    "scanDays": 30,
    "updateSpreadsheetName": "Data",
    "submitChannel": "",
    "testChannel": "",
    "adminChannel": "",
    "updateChannels": [
    ],
    "admins": [
    ],
    "roles": [
        {
            "name": "TS",
            "value": 1.5
        }
    ]
}
```
Luego se puede volver a ejecutar
```bash
py CyanBot.py
```

(Si aqui vuelve a lanzar un error de falta de archivos puede ser necesario crear dos archivos: `data/msg.json` y `data/series.json`)

---

## ¿Cómo Funciona?

### Comandos
Los comandos solo funcionarán en el canal cuya *Id* que haya sido ingresado en el apartado de `adminChannel` en el archivo `data/config.json` y si es utilizado por aquellos usuarios cuya *Id* este ingresada en el arreglo de `admins` en el archivo. 
Además solo funcionarán con el `prefix` definido.
- **help**: Despliega una ayuda con información de los comandos.
- **update**: Genera un archivo de hoja de cálculo, contabilizando el monto que se debe pagar a los usuarios segun los roles trabajados en el **mes actual**. Para definir estos roles es que se debe llenar en el archivo de `data/config.json` los objetos con un `"name"` y un `"value"`. El name es el rol y value es el monto por cada rol.
- **stats [user/role]**: Muestra estadisticas del usuario o del rol. en caso de dejar vacio muestra estadisticas globales. 

### Actualizaciones
Tomará el link definido en el campo de `updateLink` definido en el archivo `data/config.json` y de esa página ira sacando las últimas actualizaciones de mangas traducidos.
En el archivo `data/config.json` se debe definir el campo de `updateChannels`. se debe tener en cuenta que pueden haber mas de uno por lo tanto se debe llenar el arreglo con los *Id* de los canales que desean recibir las actualizaciones:
```js
//config.json
{
//...
  "updateChannels": [
    "12345678",
    "12344556"
  ]
//...
}
```
En este momento esta "quemada" la forma de leer las actualizaciones a leer el HTML de la página en cuestion y buscar utilizando los elementos y clases css para encontrar las actualizaciones. Si se desea cambiar la funcionalidad se debe modificar el método `parse` en el archivo `app/updates.py` a que lea correctamente el HTML correspondiente a la página que se desea escanear.
La frecuencia con la que se escanea la página y con que se envían las actualizaciones se puede alterar con el campo `updateDelay` y `discordDelay` del archivo `data/config.json`.
Las series ya actualizadas serán insertadas en un archivo `data/series.json` con el formato:
```
{
  "<hash de serie>": "<hash de ultimo capiitulo>"
}
```
Para así evitar mostrar la misma serie y capítulo nuevamente.

### Subir trabajos
Para subir los trabajos, es importante definir todos los roles en el archivo `data/config.json` como fue explicado mas arriba. Además, se debe definir el campo `submitChannel` con el *Id* del canal en el que se va a realizar la subida.
Cada vez que el bot inicia por primera vez, va a escanear todos los mensajes enviados en ese canal por los pasados 30 dias, parametrizables con el campo de `scanDays`. Esto para poder utilizar el comando **update** desde el primer momento.
Para subir un trabajo cada usuario deberá escribir un mensaje normal (sin prefijo) con el formato: `<Nombre de la obra> <Rol> <Capitulo> [@menciones]` (El nombre de la obra puede estar separado por espacios y además las menciones son opcionales aunque siempre deben llevar un `@`. Las mayúsculas y minusculas no importan ni en el rol ni el nombre de la obra ya que de fondo será transformado a minúscula.
Ejemplo:
```
Mi amiga es un monstruo TS 45. 
```
Estos trabajos son almacenados en el archivo `data/msg.json`.

### Eliminar Trabajos
Si durante la ejecución del bot, se sube un trabajo y luego se elimina el mensaje. El trabajo también será eliminado.

### Testeo
Si se incluye la *Id* de un canal de testeo en `testChannel` del archivo `data/config.json`, en ese canal se imprimiran cosas ligeramente importantes o que se consideren necesarias, por ejemplo si un usuario trata de subir un trabajo, en este canal se mostrará lo que se está almacenando en el archivo de mensajes y además si cumple el formato necesario, de no cumplir el formato necesario, menciona que "no se insertará el trabajo". Este canal solo debería ser visible por admins para validar en caso de que una persona cometa errores.
