import socket

from _thread import start_new_thread
import threading
import pickle

import server_global
import ResultSet

# serveur de "base de données"
# récupère les requêtes en provenance de flask (ou autre)
# effectue la recherche
# sérialise la réponse et la renvoie

# V0.1
# todo: plein de trucs, 
# être thread safe, 
# mise à jour à la volée, 
# gestion des options de recherche (tris) [pas très utile car on a déjà tri en Javascript]
# gestion des mots manquants (chercher, ajouter, sauvegarder l'arbre)
# gestion des ambiguïtés de prononciations

# base_directory = "C:\\Users\\vincent\\OneDrive\\Documents\\code\\python\\words\\src\\words\\"
base_directory = "C:\\Users\\Dell\\Desktop\\code\\python\\words\\src\\words\\"

# with open("data/test_phon_index.dmp", "rb") as f:
with open(base_directory+"data\\test_phon_index.dmp", "rb") as f:
    phon_idx = pickle.load(f)

# with open('data/test_index.dmp', "rb") as f:
with open(base_directory+'data\\test_index.dmp', "rb") as f:
    idx = pickle.load(f)

# with open("data/gramm.dmp", "rb") as f:
with open(base_directory+"data\\gramm.dmp", "rb") as f:
    gramm = pickle.load(f)


def rq_server_threaded(c):

    while not server_global.stop_switch:
        # data received from client
        data = c.recv(1024)
        if not data:
            print('Bye')
            # lock released on exit
            # print_lock.release()
            break

        mode_options = data[0]
        keep_accents = (mode_options & 2) == 2
        rs:ResultSet = None
        data = data[1:]
        words_request = data.decode('utf8')
        print("mode_options = " + str(mode_options))
        print("request for %s " % words_request)
        #############################################
        #TODO: si les données sont en phonétique, forcer mode phonétique

        #############################################
        # mode 0 == mode anagrammes (lettres)
        if mode_options & 1 == 0:

            rs = idx.search_anagrammes(data.decode('utf8'), keep_accents=keep_accents)
            print("%d" % len(rs._items))
            # for x in rs.items:
            #     print(x.mot)

            #############################################
            # TODO: better serialization ?
            # seralize
            data = pickle.dumps(rs)
            # on send data length
            c.send(len(data).to_bytes(4, byteorder='big'))
            # send data
            c.send(data)
        else:
            # mode 1 == mode phonétique
            # TODO:
            # faire une liste de mots,  chercher les inconnus, désambiguation (hétérophones)
            words = data.decode('utf8').split(" ")

            # ici on trie les mots: ok, ambigus, inconnus
            w_ok = []
            w_unknown = []
            w_ambigus = []
            for w in words:
                if w not in gramm:
                    # mot inconnu:
                    # todo: le demander au crawler ?
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
                # meilleur cas: tous les mots sont connus, et ont une unique prononciation
                rqst = ""
                for w in w_ok:
                    rqst += w[0].api
                rqst = rqst.replace('.', '')
                rs = phon_idx.search_anagrammes(rqst)
            else:
                # autrement, on renvoie trois listes
                # les mots non trouvés seront gérés je sais pas comment ?
                # les ambigus peuvent etre traités avec une page/un popup intermédiaire de désambiguation
                rs = (w_ok, w_unknown, w_ambigus)
            data = pickle.dumps(rs)
            #TODO: better serialization ?
            #serialize
            # on envoie la longueur du paquet de données
            c.send(len(data).to_bytes(4, byteorder='big'))
            # on envoie les données
            c.send(data)
    # connection closed
    c.close()


def Main():
    
    connected = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while connected is False:
        try:
            s.bind((server_global.host, server_global.port))
        except OSError:
            server_global.port += 1
        else:
            connected = True
    print("socket bound to port %d" % server_global.port)
    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    # cli thread to control server execution
    threading.Thread(target=server_global.cli_threaded, args=(None,)).start()

    # a forever loop until client wants to exit
    while not server_global.stop_switch:
        # establish connection with client
        c, addr = s.accept()
        # lock acquired by client
        # print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])
        # Start a new thread and return its identifier
        threading.Thread(target=rq_server_threaded, args=(c,)).start()
    s.close()


if __name__ == '__main__':
    Main()
