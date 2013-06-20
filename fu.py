from ampanal.funcgen import FunctionGenerator

fg = FunctionGenerator()
fg.start()
while True:
    what = raw_input("> ")
    try:
        freq = int(what)
        fg.sine(freq)
    except:
        pass
    if what == 'stop':
        fg.silence()
    if what == 'quit':
        fg.close()
        break
