def translate_range(value, from_min, from_max,to_min,to_max):
    # Figure out how 'wide' each range is
    leftSpan = from_max - from_min
    rightSpan = to_max - to_min
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - from_min) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return int(to_min + (valueScaled * rightSpan))

def generate_graphviz(node, fname="data/test_graph.txt", depth=4):
    fifo = [(node,'')]
    file = open(fname, "w")
    file.write("graph G {\n")
    file.write("\t\toverlap = false;\n")
    max_children=19
    max_words=15
    while len(fifo) > 0:
        c_node,path = fifo.pop()

        
        nb_children=len(c_node.children)
        nb_words=0
        if c_node.data is not None:
            nb_words = len(c_node.data)
        # if c_node.data is not None and len(c_node.data)>max_words:
        #     max_words = len(c_node.data)
        # if c_node.children is not None and len(c_node.children)>max_children:
        #     max_children = len(c_node.children)
        g_node_color = translate_range(nb_children,0,max_children,0,255) * 65536 +\
                        translate_range(nb_words,0,max_words,0,255)
        g_node_name = path
        if path=='':
            g_node_name = "root"
        # declare node
        ftd_color=hex(g_node_color)[2:]
        while len(ftd_color)<6:
            ftd_color+="0"
        file.write(f'\t\t"{g_node_name}" [color="#{ftd_color}"]\n')
        #declare transitions
        if depth!=-1 and len(path)<depth-1:
            file.write(f'\t\t"{g_node_name}" -- ')
            file.write('{')
            for c in c_node.children:
                child = c_node.children[c]
                file.write(f'{child.cw}; ')
            file.write('}')
            file.write("\n")

            next = [c for c in c_node.children]
            next.sort(reverse=True)
            for c in next:
                # print(f"path = {path}{c}")
                fifo.append((c_node.children[c],path+c))
    print(f"{max_children} {max_words}")
    file.write("}\n")
    file.close()
    return
graph_file="data/test_graph.txt"
# twopi -Tpng -O -Gsize=20,20 -Gdpi=1000 test_graph.txt
# s = Source.from_file(graph_file)
# s.view()

######################################################################################################
# LES GRAPHES N'ONT PAS DONNE GRAND CHOSE CAR ILS SONT BIEN TROP COMPLEXES ET GRAPHVIZ PLANTE
######################################################################################################