from .handsfree import handsfree

hf = handsfree()
if input() == "anwser":
    hf.anwser_calls()
    hf.on_call_start()