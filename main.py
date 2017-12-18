import argparse

from handlers import guild_bank
from handlers import world_boss_loot
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
    parser.add_argument('guild_server_id', type=str,
                        help='id for guild discord server')
    parser.add_argument('totp_secret', type=str,
                        help='secret used for OTP generation')
    parser.add_argument('wb_channel_id', type=str,
                        help=('id for channel used for world boss loot '
                              'calculations'))
    parser.add_argument('wb_role_id', type=str,
                        help=('id for role allowed to perform world boss '
                              'calculations'))
    parser.add_argument('wb_server_id', type=str,
                        help='id for world boss discord server')
    args = parser.parse_args()
    gbank = guild_bank.GuildBank(
        args.log_to_file, args.bank_channel_id, args.bank_role_id,
        args.guild_server_id, args.totp_secret)
    wboss = world_boss_loot.WorldBossLoot(args.wb_channel_id, args.wb_role_id,
                                          args.wb_server_id)
    NSABot([gbank, wboss]).run(args.bot_token)