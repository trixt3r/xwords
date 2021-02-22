
# Import socket module
import socket
# import threading
import pickle

# just a test client

anagram = "marie"
host = '127.0.0.1'
port = 12346


def exec_anagramm_request(sentence, keep_accents=False, exact_word=False):
    global host
    global port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    mode_options = 0
    if keep_accents:
        mode_options |= 2
    if exact_word:
        mode_options |= 4

    s.send(bytes([mode_options]))
    s.send(sentence.encode("utf8"))
    data_len = 0

    # message received from server
    raw_data = s.recv(1024)
    data_len = int.from_bytes(raw_data[:4], "big")
    raw_data = raw_data[4:]
    print("à lire: %d" % data_len)
    while(len(raw_data) < data_len):
        raw_data += s.recv(1024)
    print("%d lus" % data_len)
    data = pickle.loads(raw_data)
    return data


# mode = 0 : anagramms
# mode = 1 : contrepet
def exec_request(sentence, mode, keep_accents=False, exact_word=False):
    global host
    global port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    mode_options = mode
    if keep_accents:
        mode_options |= 2
    if exact_word:
        mode_options |= 4

    s.send(bytes([mode_options]))
    s.send(sentence.encode("utf8"))
    data_len = 0

    # message received from server
    raw_data = s.recv(1024)
    data_len = int.from_bytes(raw_data[:4], "big")
    raw_data = raw_data[4:]
    print("à lire: %d" % data_len)
    while(len(raw_data) < data_len):
        raw_data += s.recv(1024)
    print("%d lus" % data_len)
    data = pickle.loads(raw_data)
    return data

def Main():
    # local host IP '127.0.0.1'
    global host
    global port
    global anagram
    # Define the port on which you want to connect


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server on local computer
    s.connect((host, port))

    # message you send to server
    # message = "shaurya says geeksforgeeks"
    mode_options = 0
    while True:
        if not anagram == "":

            # message sent to server
            # s.send(anagram.encode('ascii'))
            # send mode anagramm
            s.send(bytes([mode_options]))
            s.send(anagram.encode("utf8"))
            data_len = 0

            # message received from server
            raw_data = s.recv(1024)
            data_len = int.from_bytes(raw_data[:4], "big")
            raw_data = raw_data[4:]
            print("à lire: %d" % data_len)
            while(len(raw_data) < data_len):
                raw_data += s.recv(1024)
            print("%d lus" % data_len)
            # print the received message
            # here it would be a reverse of sent message
            # print('Received from the server :',str(data.decode('ascii')))
            # print('Received from the server :',str(data.decode('utf8')))
            data = pickle.loads(raw_data)
            print(data)
            if mode_options == 0:
                data.group(group_by=["nature"])
                print('Received from the server :')
                for w in data.words:
                    print(w)
            else:
                # résultat recherche contrepeterie

                if isinstance(data, tuple):
                    print("mots trouvés:")
                    for w in data[0]:
                        print("%s (%s)" % (w[0].mot, w[0].api))
                    print("prononciations à préciser:")
                    for w in data[2]:
                        print("%s :" % w[0].mot)
                        for a in set([x.api for x in w]):
                            print("\t%s" % a)
                    print("mots inconnus:")
                    for w in data[1]:
                        print(w)
                else:
                    # pas de mots ambigus/inconnus
                    # le résultat reçu est un ResultSet
                    data.group(group_by=["nature"])
                    print('Received from the server :')
                    for w in data.words:
                        print(w)
                    pass

            # ask user whether he wants to continue
            ans = input('\nDo you want to continue(y/n) :')
            if ans == 'y':
                mode_options = int(input("mode (0 anag, 1 contrep):"))
                anagram = input("\n :")
                continue
            else:
                break
    # close the connection
    s.close()

if __name__ == '__main__':
    Main()
