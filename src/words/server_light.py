import socket
import threading
from _thread import start_new_thread
# import threading
import pickle
from cw import can_write, getCanonicForm
import server_global
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




with open('data/cword_base.dmp', "rb") as f:
    idx = pickle.load(f)

def rq_server_threaded(c):
    global idx
    while not server_global.stop_switch:
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
        canon_sentence = getCanonicForm(words_request)
        print("request for '%s' %s " % (words_request, canon_sentence))
        if mode_options & 1 == 0:

            ################# Accents filters
            def test1(canon_sentence, word):
                return True
            def test2(canon_sentence, word):
                return can_write(canon_sentence, word)
            accents_test = test1
            if keep_accents:
                accents_test = test2
            #################

            rs = idx.searchAnagram(data.decode('utf8'), keep_accents=keep_accents)
            print("%d" % len(rs))
            # idx.searchAnagram returns GNode list
            # here we generate a simple words list
            my_results = []
            for x in rs:
                for w in x.data:
                    # filtering accents if needed
                    # shouldn't it be done directly
                    # in GNode.searchAnagram ??
                    if(accents_test(canon_sentence, getCanonicForm(w, True))):
                        my_results.append(w)
            
            data = pickle.dumps(my_results)
            # on send data length
            c.send(len(data).to_bytes(4, byteorder='big'))
            # send data
            c.send(data)
        else:
            # request for contrepeterie,
            # unimplemented in light version
            pass
    # connection closed
    c.close()


def Main():
    # global port
    # global host
    # global stop_switch
    # host = ""

    
    connected = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while connected is False:
        try:
            s.bind((server_global.host, server_global.port))
        except OSError:
            server_global.port += 1
        else:
            connected = True
    print("socket bound to port", server_global.port)
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
        # start_new_thread(rq_server_threaded, (c,))
        threading.Thread(target=rq_server_threaded,
        args=(c,)).start()
    s.close()


if __name__ == '__main__':
    Main()
