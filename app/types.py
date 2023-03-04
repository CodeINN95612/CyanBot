
import discord
from typing import Tuple

# Msg as string, Discord Message, UserId, isCommand, Discord Client, isSubmitChannel, isAdminChannel, isServer
CmdArgs = Tuple[str, discord.Message, str,
                bool, discord.Client, bool, bool]
