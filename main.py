from handsfree import handsfree
from routing import audio_route

hf = handsfree()
route = audio_route()
if input() == "1":
    hf.anwser_calls()
    route.on_call_start()