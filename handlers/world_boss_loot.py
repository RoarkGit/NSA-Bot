from collections import defaultdict

from .handler import Handler


class WorldBossLoot(Handler):

    def __init__(self, wb_analysis_channel_id, wb_mod_role_id):
        self._kill_dict = defaultdict(int)
        self._scout_dict = defaultdict(int)
        self._wb_analysis_channel_id = wb_analysis_channel_id
        self._wb_mod_role_id = wb_mod_role_id
        self.channels = []
        self.mod_roles = []

    async def process_message(self, message):
        if (message.channel in self.channels and
            any(role in self.mod_roles for role in message.author.roles)):
            try:
                if message.content.startswith('!scout'):
                    self._scout_dict = self._parse_wb_string(message)
                    response = '```Successfully parsed scouting data:\n'
                    response += '\n'.join(
                        guild + ': ' + str(value) for guild, value in
                        self._scout_dict.items())
                    response += '```'
                    await self._bot.send_message(message.channel, response)
                if message.content.startswith('!kill'):
                    self._kill_dict = self._parse_wb_string(message)
                    response = '```Successfully parsed kill data:\n'
                    response += '\n'.join(
                        guild + ': ' + str(value) for guild, value in
                        self._kill_dict.items())
                    response += '```'
                    await self._bot.send_message(message.channel, response)
            except Exception as e:
                await self._bot.send_message(message.channel, 'Parsing error.')
                raise e
            if message.content.startswith('!calc'):
                try:
                    ranges = self._wb_calc()
                    response = '```Rolling ranges:\n'
                    response += '\n'.join(
                        guild + ': ' + str(value) for guild, value in ranges)
                    response += '```'
                    await self._bot.send_message(message.channel, response)
                except Exception as e:
                    await self._bot.send_message(
                        message.channel, 'Error performing calculation.')
                    raise e

    def client_ready(self):
        for server in self._bot.servers:
            for role in server.roles:
                if role.id == self._wb_mod_role_id:
                    self.mod_roles.append(role)
            for channel in server.channels:
                if channel.id == self._wb_analysis_channel_id:
                    self.channels.append(channel)

    # Parses scout and kill strings for world bosses
    def _parse_wb_string(self, message):
        tokens = message.content.split()[1:]
        d = defaultdict(int)
        for i in range(0, len(tokens), 2):
            guild, count = tokens[i].upper(), tokens[i + 1]
            d[guild] = int(count)
        return d

    # Calculates roll ranges for world boss loot
    def _wb_calc(self):
        total_scout = sum(self._scout_dict.values())
        total_kill = sum(self._kill_dict.values())
        guilds = set(
            list(self._scout_dict.keys()) + list(self._kill_dict.keys()))
        values = []
        total = 0

        # Compute the value for each guild based on scout and kill
        # participation.
        for g in guilds:
            if total_kill > 0:
                y = (100 * self._kill_dict[g] // total_kill) // 2
            else:
                y = 0
            if total_scout > 0:
                z = (100 * self._scout_dict[g] // total_scout) // 2
            else:
                z = 0
            x = z + y
            total += x
            values.append([g, x])
        values.sort(key=lambda x: x[1], reverse=True)
        if total == 0:
            return []

        # If total doesn't add up to 100, distribute missing points to guilds
        # starting with the highest one.
        idx = 0
        while total < 100:
            values[idx][1] += 1
            total += 1
            idx += 1
            idx %= len(values)

        # Construct range strings.
        ranges = []
        t = 100
        for g, v in values:
            l = t - v
            ranges.append((g, "%d-%d" % (l + 1, t)))
            t -= v
        return ranges

    def command_triggers(self):
        return ['!scout', '!kill', '!calc']
