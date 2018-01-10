import argparse

from handlers import guild_bank
from handlers import world_boss_loot
from handlers import world_boss_timers
from nsabot import NSABot

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_to_file', action='store_true',
                        help='log access requests to local file')
    parser.add_argument('bot_token', type=str,
                        help='token used for connecting bot to server')
    parser.add_argument('bank_channel_id', type=str,
                        help='id of the channel for logging bank access')
    parser.add_argument('bank_role_id', type=str,
                        help='id for role allowed to access guild bank')
    parser.add_argument('totp_secret', type=str,
                        help='secret used for OTP generation')
    parser.add_argument('wb_analysis_channel_id', type=str,
                        help='id for world boss analysis channel')
    parser.add_argument('wb_general_channel_id', type=str,
                        help='id for world boss general channel')
    parser.add_argument('wb_mod_role_id', type=str,
                        help='id for world boss mod role')
    parser.add_argument('--wb_timer_shelve_file', type=str, default=None,
                        help='path to file for storing world boss timers')
    args = parser.parse_args()
    gbank = guild_bank.GuildBank(
        args.log_to_file, args.bank_channel_id, args.bank_role_id,
        args.totp_secret)
    wboss = world_boss_loot.WorldBossLoot(
        args.wb_analysis_channel_id, args.wb_mod_role_id)
    timer = world_boss_timers.WorldBossTimers(
        args.wb_analysis_channel_id, args.wb_general_channel_id,
        args.wb_mod_role_id, args.wb_timer_shelve_file)
    NSABot([gbank, wboss, timer]).run(args.bot_token)
