# Abstract class used for handling commands.


class Handler:
    _bot = None

    # Adds reference to bot in order to access bot functions.
    def register_bot(self, bot):
        self._bot = bot

    # Processes a given message.
    async def process_message(self, message):
        pass

    # Returns a list of commands that trigger this handler.
    def command_triggers(self):
        return []