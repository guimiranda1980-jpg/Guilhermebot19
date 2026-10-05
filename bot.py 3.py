import os
import threading
from flask import Flask
import discord
from discord import app_commands
from discord.ext import commands
from google import genai

app = Flask('')

@app.route('/')
def home():
    return "Bot Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run).start()

client_ia = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
NOME_MODELO = 'gemini-3.6-flash' 



intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.suporte_channel_id = None  # Guarda o ID do canal configurado

    async def setup_hook(self):
        # Sincroniza os comandos / (Slash Commands) com o Discord
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f'Bot ligado com sucesso como {bot.user}!')


@bot.tree.command(name="config", description="Define o canal onde o bot vai tirar dúvidas.")
@app_commands.describe(canal="Escolha o canal de texto para o suporte.")
async def config(interaction: discord.Interaction, canal: discord.TextChannel):
    bot.suporte_channel_id = canal.id
    await interaction.response.send_message(f"✅ Canal de suporte configurado com sucesso para: {canal.mention}")


@bot.event
async def on_message(message):
    # Ignora mensagens do próprio bot para não entrar em loop
    if message.author == bot.user:
        return

    # Verifica se a mensagem foi enviada no canal configurado pelo /config
    if bot.suporte_channel_id and message.channel.id == bot.suporte_channel_id:
        # Mostra que o bot está a "escrever" enquanto pensa na resposta
        async with message.channel.typing():
            try:
                # Envia a dúvida da pessoa para a Inteligência Artificial (Nova sintaxe)
                response = client_ia.models.generate_content(
                    model=NOME_MODELO,
                    contents=message.content
                )
                # Envia a resposta da IA de volta para o chat do Discord
                await message.reply(response.text)
            except Exception as e:
                await message.reply("Desculpa, tive um problema ao processar a tua dúvida. Tenta novamente.")
                print(f"Erro na IA: {e}")

    # Permite que outros comandos normais continuem a funcionar
    await bot.process_commands(message)


import os  

import discord
from discord.ext import commands


bot.run(os.getenv('DISCORD_TOKEN'))


