# 直播间ID （dict）
rooms = {'1111111':'name','222222':'name2'}
# 需要转换mp3的直播间别名
convert_rooms = {'name'}
# env,终端环境有时只支持ascii
env = "origin"
# 检测是否开播间隔(秒)
check_interval=5*60
# ffmpeg路径，用于提取音频，留空不使用
ffmpeg_path = ""
