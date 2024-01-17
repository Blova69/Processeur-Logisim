# Change the filename variable to the name of the file you want to compile
fileinput = 'test.txt'
# Change the fileoutput variable to the name of the file you want to create
fileoutput = 'hexa.txt'

ual_list = ['ADD','ADDI','SUB','SUBI','MUL','MULI','AND', 'ANDI', 'OR', 'ORI', 'XOR', 'XORI', 'SL', 'SLI', 'SR', 'SRI']
ctrl_list = ['JMP','JEQU','JNEQ','JSUP','JINF','CALL','RET']
LABELS = {}

def ual(inst) :
    #code UAL
    res = '00'
    #code OP
    if inst[0] == 'ADD' or inst[0] == 'ADDI':
        res += '111'[::-1]
    elif inst[0] == 'SUB' or inst[0] == 'SUBI':
        res += '110'[::-1]
    elif inst[0] == 'AND' or inst[0] == 'ANDI':
        res += '101'[::-1]
    elif inst[0] == 'OR' or inst[0] == 'ORI':
        res += '100'[::-1]
    elif inst[0] == 'XOR' or inst[0] == 'XORI':
        res += '011'[::-1]
    elif inst[0] == 'SL' or inst[0] == 'SLI':
        res += '010'[::-1]
    elif inst[0] == 'SR' or inst[0] == 'SRI':
        res += '001'[::-1]
    elif inst[0] == 'MUL' or inst[0] == 'MULI':
        res += '000'[::-1]
    #bit immédiat
    if inst[0][-1] == 'I' :
        res += '1'
    else :
        res += '0'
    #destination
    res += '{0:03b}'.format(int(inst[1][1:]),'b')[::-1]
    #source 1
    res += '{0:03b}'.format(int(inst[2][1:]),'b')[::-1]
    if 'R' in inst[3] : #source 2
        res += '{0:03b}'.format(int(inst[3][1:]),'b')[::-1]
        res += '0'*17
    else : #si la source 2 n'a pas de R (~ opération immédiate)
        res += '0'*4
        res += '{0:016b}'.format(int(inst[3]),'b')[::-1]
    return res
    
def mem(inst) :
    res = '01'[::-1]#code MEM
    #code OP
    if inst[0] == 'STR' :
        res += '000'[::-1]
        res += '0'#bit Imm
        res += '000'#bit 'dest' dont on a pas besoin
        #l'adresse de la valeur
        res += '{0:03b}'.format(int(inst[2][1:]),'b')[::-1]
        #le registre dont on stocke la valeur
        res += '{0:03b}'.format(int(inst[1][1:]),'b')[::-1]
    elif inst[0] == 'LD' :
        res += '001'[::-1]
        res += '0'#bit Imm
        #le registre où on stocke la valeur
        res += '{0:03b}'.format(int(inst[1][1:]),'b')[::-1]
        #l'adresse de la valeur
        res += '{0:03b}'.format(int(inst[2][1:]),'b')[::-1]
    while (len(res) < 32) :
        res += '0'
    return res

def ctrl(inst) :
    res = '11'#code CTRL (pas retourné parceque = 11 dans tt les cas)
    #code OP
    if inst[0] == 'JMP' :
        res += '000'[::-1]
    elif inst[0] == 'JEQU' :
        res += '001'[::-1]
    elif inst[0] == 'JNEQ' :
        res += '010'[::-1]
    elif inst[0] == 'JSUP' :
        res += '011'[::-1]
    elif inst[0] == 'JINF' :
        res += '100'[::-1]
    elif inst[0] == 'CALL' :
        res += '101'[::-1]
    elif inst[0] == 'RET' :
        res += '110'[::-1]
    res += '0' #bit imm
    res += '000' #bit 'dest' dont on a pas besoin
    if inst[0] in ['RET','CALL','JMP'] :
        res += '0'*6 #on met des 0 à la place de la source 1 et 2:
    else :
        res += '{0:03b}'.format(int(inst[1][1:]),'b')[::-1]
        res += '{0:03b}'.format(int(inst[2][1:]),'b')[::-1]
    res += '0' #bit innutile (pourrait dervir à parité)
    if inst[0] in ['CALL','JMP'] :
        inst[1] = LABELS[inst[1]]
        res += '{0:016b}'.format(int(inst[1]),'b')[::-1]
    elif inst[0] == 'RET' :
        res += '0'*16
    else :
        inst[3] = LABELS[inst[3]]
        res += '{0:016b}'.format(int(inst[3]),'b')[::-1]
    return res

#convertit une ligne d'assembleur en bianaire
def convert_line(str) :
    res = ''
    inst = str.split(' ')
    if inst[0] in ual_list :
        res += ual(inst)
    elif inst[0] == 'STR' or inst[0] == 'LD' :
        res += mem(inst)
    elif inst[0] in ctrl_list :
        res += ctrl(inst)
    return res

#convertit une instruction bianaire en hexa
def to_hex(str) :
    inst = str.split('\n')
    res = ''
    for i in inst :
        res += '{0:08x}'.format(int(i[::-1],2),'x')
    return res

def cleanNLabel(file) :
    res = []
    label = ''
    numLigne=0
    for line in file :
        line.replace('\t',' ')
        #on supprime les commentaires
        if '#' in line :
            line = line[:line.index('#')]
        #on remplace tout les espaces multiples par un seul espace        
        while '  ' in line :
            line = line.replace('  ',' ')

        #on supprime l'espace qui peut rester en début de ligne
        if line[0] == ' ':
            line = line[1:]

        #on supprime les lignes vides
        if line == '\n' or line == '':
            continue
        #on supprime les caractères inutiles en fin de ligne
        while line[-1] == ' ' or line[-1] == '\n':
            line = line[:-1]

        
        #si la ligne se termine par ':' on la garde en mémoire
        if ':' in line :
            index = line.index(':')
            
            label = line[:index].replace(' ','')
            
            LABELS.update({label:numLigne}) #on l'ajoute à la liste des labels
    
            if index == len(line)-1:
                continue
            else :
                line = line[index+1:]
                if line[0] == ' ':
                    line = line[1:]
        #on enregistre la ligne
        res.append(line)
        numLigne+=1

    return res

#convertit l'entrée assembleur en hexa pour la ram
def convert_file(file) :
    file = open(file, 'r')
    res = ''
    numLigne=0
    lignes = cleanNLabel(file) #on enlève les labels et on rend propre
    for line in lignes :
        line = line.replace('\n','')
        res += to_hex(convert_line(line))
        res += ' #' + line + '\n'
        numLigne+=1
    file.close()
    return res


text_file = open(fileoutput, "w")
#write string to file
text_file.write('v2.0 raw\n'+convert_file(fileinput))
#close file
text_file.close()

print(LABELS)