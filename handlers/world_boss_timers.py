from collections import defaultdict
from datetime import datetime, timedelta, tzinfo, timezone
import re

from .handler import Handler

class GMT1(tzinfo): # directly from pydocs B-)
    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)
    def dst(self, dt):
        d = datetime(dt.year, 4, 1)
        # summer time starts on last sunday of march
        self.dston = d - timedelta(days=d.weekday() + 1)
        d = datetime(dt.year, 11, 1)
        # ends before the last sunday of october
        self.dstoff = d - timedelta(days=d.weekday() + 1)
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return timedelta(hours=1)
        else:
            return timedelta(0)
    def tzname(self, dt):
        return "GMT +1"



class WorldBossTimers(Handler):
    def __init__(self, wb_channel_id, wb_role_id, wb_server_id):
        self.timezone = GMT1()
        self.channels = []
        self.roles = []
        self._wb_channel_id = wb_channel_id
        self._wb_role_id = wb_role_id
        self._wb_server_id = wb_server_id
        self._wb_tod = { "azu": None, "kaz": None, "drg": None, }
        for key in self._wb_tod:
            self._wb_tod[key] = datetime(1900, 1, 1, 0, 0, 0, 0, self.timezone)

    def client_ready(self):
        for serv in self._bot.servers:
            if serv.id == self._wb_server_id:
                for role in serv.roles:
                    if role.id == self._wb_role_id:
                        self.roles.append(role)
                for chan in serv.channels:
                    if chan.id == self._wb_channel_id:
                        self.channels.append(chan)

    async def process_message(self, message):
        if message.channel in self.channels:
            try:
                if message.content.startswith('!tod'):
                    if any(role in message.author.roles for role in self.roles):
                        response = self._parse_tod_string(message)
                        await self._bot.send_message(message.channel, response)
                if message.content.startswith('!timers'):
                    response = self._construct_timer_response()
                    await self._bot.send_message(message.channel, response)
            except Exception as e:
                await self._bot.send_message(message.channel,
                        'Caught unhandled exception')
                raise e

    # Parses scout and kill strings for world bosses
    def _parse_tod_string(self, message):
        msg_split = message.content.split(maxsplit=2)
        name = msg_split[1]
        timestr = ""
        if len(msg_split) > 2:
            timestr = msg_split[2]
        key = name.lower()[:3]
        if key in self._wb_tod:
            try:
                dt = self.timestr_to_datetime(timestr)
            except Exception as e:
                return 'Parsing error: could not interpret "{}"'.format(timestr)
            self._wb_tod[key] = dt
            return 'Changed TOD of {} to {:%Y-%m-%d %H:%M}'.format(key, dt)
        else:
            return 'Parsing error: key {} does not match any of {}'.format(key,
                                                ", ".join(self._wb_tod.keys()))

    def timestr_to_datetime(self,timestr):
        dt = datetime.now(self.timezone)
        y,m,d,H,M,*_ = dt.timetuple()
        numbers = [int(n) for n in re.findall("\d+", timestr)]
        if len(numbers) >= 5:
            y,m,d,H,M,*_ = numbers
        elif len(numbers) == 4:
            m,d,H,M = numbers
        elif len(numbers) == 2:
            H,M = numbers
        elif len(numbers) in [1,3]:
            raise ValueException
        return dt.replace(year=y, month=m, day=d, hour=H, minute=M)

    def _construct_timer_response(self):
        response = "```Servertime: {servertime:%a %d %b %H:%M}\n{lines}```"
        line_fmt = "{}: starts {:%a %d %b %H:%M}, ends {:%a %d %b %H:%M} {}"
        cur_dt = datetime.now(self.timezone)
        timer_lines = []
        for key, val in self._wb_tod.items():
            start_dt = val + timedelta(days=3)
            if key == "drg":
                start_dt += timedelta(days=1)
            end_dt = val + timedelta(days=7)
            additional = ""
            if cur_dt < start_dt:
                diff = start_dt-cur_dt
                d,h = diff.days, diff.seconds//3600
                additional = "opens in {}d {}h".format(d,h)
            elif cur_dt <= end_dt:
                diff = end_dt-cur_dt
                d,h = diff.days, diff.seconds//3600+1
                additional = "closes in {}d {}h".format(d,h)
            else:
                additional = "window has passed"
            timer_lines.append(line_fmt.format(key,start_dt,end_dt,additional))
        return response.format(servertime=cur_dt, lines="\n".join(timer_lines))

    def command_triggers(self):
        return ['!tod', '!timers']

def main():
    d = datetime.now()

if __name__ == "__main__":
    main()
