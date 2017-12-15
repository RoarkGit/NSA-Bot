# Bot used for administrative functions for NSA guild on Lightbringer.
#
# Current functionality:
#   1) Acts as 2FA generator for guild bank use.

import asyncio
import datetime
import discord
import pyotp

class NSABot(discord.Client):
  def __init__(self, log_to_file, bank_channel_id, bank_role_id,
               guild_server_id, totp_secret):
    super().__init__()
    self._log_to_file = log_to_file
    self._bank_channel_id = bank_channel_id
    self._bank_role_id = bank_role_id
    self._guild_server_id = guild_server_id
    self._totp = pyotp.TOTP(totp_secret)

  async def on_ready(self):
    # Determine bank role
    for server in self.servers:
      if server.id == self._guild_server_id:
        for role in server.roles:
          if role.id == self._bank_role_id:
            self._bank_role = role
    print('Connected.')

  async def on_message(self, message):
    if message.channel.id == self._bank_channel_id:
      if message.content.startswith('!2fa'):
        await self.handle_2fa(message)

  async def handle_2fa(self, message):
    log_message = None
    # Check that requester is a member of guild bank role
    if self._bank_role in message.author.roles:
      justification = message.content[4:].strip()
      # Check that a justification is present
      if justification:
        await self.send_message(message.author, self._totp.now())
        log_message =  ('{user} has accessed guild bank 2FA: '
                        '{justification}').format(user=message.author.mention,
                                                  justification=justification)
      else:
        log_message = 'Missing justification for guild bank access.'
    else:
      log_message = ('{user} is not a member of {role}.').format(
          user=message.author.mention, role=self._bank_role.name)
    await self.send_message(message.channel, log_message)
    # Write to file if requested
    if self._log_to_file:
      dt = datetime.datetime.utcnow()
      with open(dt.date().isoformat() + '.log', 'a+') as f:
        f.write(dt.timetz().isoformat() + ' ' +
                (message.author.nick or message.author.name) + ': ' +
                log_message + '\n')

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--log_to_file', action='store_true',
                      help='log access requests to local file')
  parser.add_argument('bank_channel_id', type=str,
                      help='id of the channel for logging bank access')
  parser.add_argument('bank_role_id', type=str,
                      help='id for role allowed to access guild bank')
  parser.add_argument('guild_server_id', type=str,
                      help='id for guild discord server')
  parser.add_argument('totp_secret', type=str,
                      help='secret used for OTP generation')
  parser.add_argument('bot_token', type=str,
                      help='token used for connecting bot to server')
  args = parser.parse_args()
  NSABot(args.log_to_file, args.bank_channel_id, args.bank_role_id,
         args.guild_server_id, args.totp_secret).run(args.bot_token)
