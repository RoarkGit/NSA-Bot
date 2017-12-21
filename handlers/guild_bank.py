from datetime import datetime

from pyotp import TOTP

from .handler import Handler


class GuildBank(Handler):

    def __init__(self, log_to_file, bank_channel_id, bank_role_id,
                 guild_server_id, totp_secret):
        super().__init__()
        self._log_to_file = log_to_file
        self._bank_channel_id = bank_channel_id
        self._bank_role_id = bank_role_id
        self._guild_server_id = guild_server_id
        self._totp = TOTP(totp_secret)
        self.bank_roles = []
        self.bank_channels = []

    # Checks that a user is permitted to access the guild bank and responds
    # accordingly.
    async def process_message(self, message):
        if message.channel in self.bank_channels:
            response = None
            # Check that requester is a member of guild bank role
            if any(role in self.bank_roles for role in message.author.roles):
                justification = message.content[4:].strip()
                # Check that a justification is present
                if justification:
                    await self._bot.send_message(message.author,
                                                 self._totp.now())
                    response = ('{user} has accessed guild bank 2FA: '
                                   '{justification}').format(
                        user=message.author.mention,
                        justification=justification)
                else:
                    response = 'Missing justification for guild bank access.'
            else:
                response = (
                    '{user} is not permitted to access guild bank.').format(
                        user=message.author.mention)
            await self._bot.send_message(message.channel, response)

            # Write to file if requested
            if self._log_to_file:
                dt = datetime.utcnow()
                with open(dt.date().isoformat() + '.log', 'a+') as f:
                    f.write(dt.timetz().isoformat() + ' ' +
                            (message.author.nick or message.author.name) +
                            ': ' + response + '\n')

    def client_ready(self):
        for server in self._bot.servers:
            if server.id == self._guild_server_id:
              for role in server.roles:
                  if role.id == self._bank_role_id:
                      self.bank_roles.append(role)
              for channel in server.channels:
                  if channel.id == self._bank_channel_id:
                      self.bank_channels.append(channel)

    def command_triggers(self):
        return ['!2fa']
