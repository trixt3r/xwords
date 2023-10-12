port = 12346
host = ""
stop_switch = False

def cli_threaded(arg):
    global port
    global host
    global stop_switch
    while True:
        text = input("")
        text = text.rstrip("\n")
        print("lu: %s" % text)
        cmd = text.split(" ")
        if cmd[0] == "get":
            if len(cmd) == 1:
                if cmd[1] == 'port':
                    print("server port: %d" %port)
                if cmd[1] == 'host':
                    print("server host: %s" % host)
        if cmd[0] == "stop":
            print("server will stop now")
            stop_switch = True
