# Bot used for administrative functions for NSA guild on Lightbringer.
#
# Current functionality:
#   1) Acts as 2FA generator for guild bank use.
#   2) Calculates roll ranges for world boss loot based on coalition formula.

from discord import Client


class NSABot(Client):
    _handlers = {}

    def __init__(self, handler_list):
        super().__init__()
        for handler in handler_list:
            for trigger in handler.command_triggers():
                self._handlers[trigger] = handler
            handler.register_bot(self)

    async def on_ready(self):
        print('Connected.')

    async def on_message(self, message):
        if message.content:
            cmd = message.content.split()[0]
            if cmd in self._handlers.keys():
                await self._handlers[cmd].process_message(message)