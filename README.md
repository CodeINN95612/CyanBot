# CyanBot
Un bot creado para guardar rabajos relizados por usuarios de discord.
  
Por el momento no hace nada...

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
    Por favor llena el archivo 'config.json' que fue creado con los valores correspondientes
```
Se debe llenar el archivo 'config.json' que fue creado (o crearlo) y debe seguir este formato:
```json
{
    "token": "TU TOKEN AQUI", 
    "sheet_name": "CyanBot"
}
```
Luego se puede volver a ejecutar
```bash
    py CyanBot.py
```