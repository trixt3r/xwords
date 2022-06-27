import socket

from _thread import start_new_thread
# import threading
import pickle

# serveur de "base de données"
# récupèr les requêtes en provenance de flask (ou autre)
# effectue la recherche
# sérialise la réponse et la renvoie

# V0.1
# todo: plein de trucs, être thread safe, mise à jour à la volée, gestion
# des options de recherche

with open("data/test_phon_index.dmp", "rb") as f:
    phon_idx = pickle.load(f)

with open('data/test_index.dmp', "rb") as f:
    idx = pickle.load(f)

with open("data/gramm.dmp", "rb") as f:
    gramm = pickle.load(f)


def threaded(c):
    global idx
    while True:
        # data received from client
        data = c.recv(1024)
        if not data:
            print('Bye')
            # lock released on exit
            # print_lock.release()
            break
        mode_options = data[0]

        print("mode_options = " + str(mode_options))
        keep_accents = (mode_options & 2) == 2
        rs = None
        data = data[1:]
        words_request = data.decode('utf8')
        print("request for %s " % words_request)
        if mode_options & 1 == 0:
            rs = idx.search_anagrammes(data.decode('utf8'), keep_accents=keep_accents)
            print("%d" % len(rs._items))
            # for x in rs.items:
            #     print(x.mot)
            # seralize
            data = pickle.dumps(rs)
            # on send data length
            c.send(len(data).to_bytes(4, byteorder='big'))
            # send data
            c.send(data)
        else:
            # TODO:
            # faire une liste de mots,  chercher les inconnus, désambiguation (hétérophones)
            words = data.decode('utf8').split(" ")
            w_ok = []
            w_unknown = []
            w_ambigus = []
            for w in words:
                if w not in gramm:
                    # mot inconnu:
                    # todo: aller le chercher sur wiktionnary
                    w_unknown.append(w)
                    continue
                wg = gramm[w]
                if len(set([x.api for x in wg])) == 1:
                    # mot connu, une seule prononciation
                    w_ok.append(wg)
                else:
                    # mot connu, mais ambigü: plusieurs prononciations possibles
                    w_ambigus.append(wg)
            if len(w_ambigus) == 0 and len(w_unknown) == 0:
                rqst = ""
                for w in w_ok:
                    rqst += w[0].api
                rqst = rqst.replace('.', '')
                rs = phon_idx.search_anagrammes(rqst)
            else:
                rs = (w_ok, w_unknown, w_ambigus)
            data = pickle.dumps(rs)
            # on envoie la longueur du paquet de données
            c.send(len(data).to_bytes(4, byteorder='big'))
            # on envoie les données
            c.send(data)
    # connection closed
    c.close()


def Main():
    host = ""

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 12346
    connected = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while connected is False:
        try:
            s.bind((host, port))
        except OSError:
            port += 1
        else:
            connected = True
    print("socket bound to port", port)
    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()
        # lock acquired by client
        # print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])
        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
    s.close()


if __name__ == '__main__':
    Main()
