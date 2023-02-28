import json
import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from tabulate import tabulate
import datetime
import pymongo

connectionStr = 'mongodb+srv://CyanBot:Halo28082@cluster0.ma6se8i.mongodb.net/?retryWrites=true&w=majority'
client = pymongo.MongoClient(connectionStr)
db = client.staff_temple

token = 'MTA2NzIxNzU2Mzk3ODgzMzk3MA.GTKWfQ.g0WVbzs8d1Vz5Ci0zRYUNKZQyT8MJmLvH03xaM'
intents = discord.Intents.all()
prefix = '#'

bot = commands.Bot(intents=intents, command_prefix=prefix)


@has_permissions(administrator=True)
@bot.command(name='iobra', help='Inserta una obra a la lista de obras aceptadas.')
async def iobra(ctx, *args):
    nombre_obra = ' '.join(args)
    if db.obras.count_documents({'nombre': nombre_obra}) > 0:
        embed = discord.Embed(
            title=f'La obra \'{nombre_obra}\' ya existe.', color=0xff0000)
        await ctx.message.reply(embed=embed)
        return

    db.obras.insert_one({'nombre': nombre_obra})
    embed = discord.Embed(
        title=f'La obra \'{nombre_obra}\' insertada', color=0x00ffff)
    await ctx.message.reply(embed=embed)


@has_permissions(administrator=True)
@bot.command(name="eobra", help="Elimina una obra a la lista de obras aceptadas si el usuario es administrador.")
async def eobra(ctx, *args):
    nombre_obra = ' '.join(args)
    if db.obras.count_documents({'nombre': nombre_obra}) == 0:
        embed = discord.Embed(
            title=f'La obra \'{nombre_obra}\' no existe.', color=0xff0000)
        await ctx.message.reply(embed=embed)
        return

    db.obras.delete_one({'nombre': nombre_obra})
    embed = discord.Embed(
        title=f'La obra \'{nombre_obra}\' eliminada', color=0x00ffff)
    await ctx.message.reply(embed=embed)


@bot.command(name='lobra', help="Lista todas las obras")
async def lobra(ctx):
    obras = db.obras.find({}).sort([('nombre', 1)])
    lista = 'Lista de Obras Permitidas: \n'
    i = 1
    for obra in obras:
        lista += f'{i}. ' + obra['nombre'] + '\n'
        i += 1
    await ctx.message.reply(lista)


@has_permissions(administrator=True)
@bot.command(name='stat', help='Muestra las estadisticas de un usuario en el servidor')
async def stat(ctx, *, username: str):
    user = discord.utils.find(
        lambda m: m.name == username or m.display_name == username, ctx.guild.members)
    if user is None:
        embed = discord.Embed(
            title=f'Usuario \'{username}\' no encontrado en el servidor', color=0xff0000)
        await ctx.message.reply(embed=embed)
        return

    now = datetime.datetime.now()
    works = db.trabajos.find({"usuario": user.id, 'fecha': {"$gte": datetime.datetime(
        now.year, now.month, 1), "$lt": datetime.datetime(now.year, now.month+1, 1)}, 'servidor': ctx.guild.id})

    works_count = {}
    for work in works:
        if work['funcion'] in works_count:
            works_count[work['funcion']] += 1
        else:
            works_count[work['funcion']] = 1

    if not works_count:
        embed = discord.Embed(
            title=f'Usuario \'{user.display_name}\' no ha realizado trabajos durante este mes', color=0xff0000)
        await ctx.message.reply(embed=embed)
        return

    table = tabulate(works_count.items(), headers=[
                     'Función', 'Conteo'], tablefmt='fancy_grid')
    await ctx.message.reply(f'```Estadísticas de trabajos de \'{user.display_name}\' en el mes actual en el servidor:\n{table}```')


@has_permissions(administrator=True)
@bot.command(name='stats', help='Stats globales de todos los usuarios')
async def stats(ctx, funcion: str = None):
    now = datetime.datetime.now()
    thirty_days_ago = now - datetime.timedelta(days=30)
    usuarios = db.users.find({'servidor': ctx.guild.id})

    trabajos = []
    for us in usuarios:
        if funcion is None:
            trabajos_30 = db.trabajos.count_documents(
                {'usuario': us['usuario'], 'servidor': us['servidor'], 'fecha': {'$gte': thirty_days_ago}})
            trabajos_total = db.trabajos.count_documents(
                {'usuario': us['usuario'], 'servidor': us['servidor']})
        else:
            trabajos_30 = db.trabajos.count_documents(
                {'usuario': us['usuario'], 'servidor': us['servidor'], 'fecha': {'$gte': thirty_days_ago}, 'funcion': funcion})
            trabajos_total = db.trabajos.count_documents(
                {'usuario': us['usuario'], 'servidor': us['servidor'], 'funcion': funcion})

        usuario = (await ctx.guild.fetch_member(us['usuario'])).name
        if funcion is None or trabajos_30 > 0:
            trabajos.append([usuario, trabajos_30, trabajos_total])
    headers = ['Usuario', '30 días', 'Total']
    table = tabulate(trabajos, headers=headers, tablefmt='fancy_grid')
    if funcion is None:
        await ctx.message.reply(f'```Estadísticas por usuario: \n{table}```')
        return
    await ctx.message.reply(f'```Estadísticas por usuario de la funcion {funcion}: \n{table}```')


@bot.event
async def on_message(msg):

    if msg.author.bot:
        return

    if msg.content.startswith("#"):
        await bot.process_commands(msg)
        return

    obra, funcion, capitulo = None, None, None

    try:

        contenido = msg.content
        if '@' in msg.content:
            contenido = contenido.split('@')[0]
            contenido = contenido.split('<')[0]
            contenido = contenido.strip()
        mensaje = contenido.split(' ')
        if (len(mensaje) < 3):
            raise ValueError()
        obra = ' '.join(mensaje[0:-2])
        funcion = mensaje[-2]
        funcion = funcion.upper()
        capitulo = mensaje[-1]
        if (not capitulo.isdigit()):
            raise ValueError()

    except ValueError or IndexError:
        embed = discord.Embed(title='Formato no valido', color=0xff0000)
        embed.add_field(name='Formato Esperado:',
                        value='Nombre de Obra <funcion> <capitulo>')
        await msg.reply(embed=embed)
        return

    if db.obras.count_documents({'nombre': obra}) == 0:
        embed = discord.Embed(
            title='Obra No detectada entre obras aceptadas', color=0xff0000)
        await msg.reply(embed=embed)
        return

    if db.users.count_documents({'usuario': msg.author.id, 'servidor': msg.guild.id}) == 0:
        db.users.insert_one(
            {'usuario': msg.author.id, 'servidor': msg.guild.id})

    trabajo = {
        'nombre_obra': obra,
        'usuario': msg.author.id,
        'fecha': msg.created_at,
        'funcion': funcion,
        'capitulo': capitulo,
        'servidor': msg.guild.id,
        'canal': msg.channel.id
    }

    db.trabajos.insert_one(trabajo)
    embed = discord.Embed(title='Guardado Correctamente', color=0x00ffff)
    await msg.reply(embed=embed)
    await bot.process_commands(msg)

bot.run(token)
