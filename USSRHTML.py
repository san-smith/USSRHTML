'''
USSRHTML - это компилятор для языка гипертекстовой разметки (ЯГТР), написанный на python.

Компилятор принимает код на языке ЯГТР и выдает файл с кодом на HTML.

ЯГТР - это фантазия на тему того, что было бы, если бы интернет придумали в СССР. 
Особенность данного языка - все вводимые команды должны быть доступны на стандартной ЙЦУКЕН клавиатуре, 
т.е. для ввода команд не нужно переключаться на английскую раскладку. Кроме того, вместо двойных тегов 
типа <body>...</body> используются команды вида \тело(...), что упрощает набор текста.
'''
# импортируем sys для возможности получения файла с исходным текстом в качестве аргумента
import sys
import datetime

#==============================================================================
def parser(inpStr):
    """
    Функция разбиения строки на токены
    
    Функция принимает на вход строку, возвращает список токенов, полученных
    из этой строки. Границами токенов могут служить: \, (, ), %, команды,
    символл конца строки и др.
    """
    i = 0
    inpStr += ' '   # Добавим в конец строки для удобства
    tokenList = []  # Список токенов
    s = ''          # Накапливает текущие символы в токен
    while i < len(inpStr)-1:
        if inpStr[i] == '\\':        
#           Если после \ идет \, (, ), %, то добавляем сам символ      
            if inpStr[i+1] in r'\())%':
                s += inpStr[i+1]
                i += 2  # И начинаем новую итерацию
                continue
                
            else:
#               Если перед \ что-то было, добавляем в список токенов 
                if s != '':
                    tokenList.append(s)
                    s = inpStr[i]
                else:
                    s += inpStr[i]
        
#       Если текущий символ (, то        
        elif inpStr[i] == '(':
#           Если в s уже что-то накоплено
            if s != '':
                tokenList.append(s) # Считаем это новым токеном
                s = ''              # и обнуляем s
            tokenList.append(inpStr[i]) # ( добавляем в любом случае
                
        elif inpStr[i] == ')':
            if s != '':
                tokenList.append(s)
                s = ''
            tokenList.append(inpStr[i])
            
        elif inpStr[i] == '%':
            if s != '':
                tokenList.append(s)
                s = ''
            tokenList.append(inpStr[i])
         
#       Если текущий символ конец строки, то добавляем его отдельным токеном
#       Нужно, чтобы правильно работать с комментариями
        elif inpStr[i] == '\n':
            if s != '':
                tokenList.append(s)
                s = ''
            tokenList.append(inpStr[i])
            
        elif (inpStr[i] == ':') and (inpStr[i+1] == ':'):
            if s != '':
                tokenList.append(s)
                s = ''
            tokenList.append(inpStr[i:i+2])
            i += 1
            
        else:
            s += inpStr[i]
            
        i += 1
        

        
    return tokenList
#==============================================================================

#==============================================================================
def attributesParser(inpAtrStr):
    """
    Функция-заглушка. Принимает строку со списком атрибутов,
    возвращает список токенов-атрибутов.    
    """
    atrList = []
    
    atrList.append(inpAtrStr)
    
    return atrList
#==============================================================================

#==============================================================================
def attributesCompiler(atrList):
    """
    Функция-заглушка. Принимает список атрибутов на ЯГТР,
    возвращает строку атрибутов на HTML.    
    """
    
    outAtrStr = ' ' + ''.join(atrList)
    
    return outAtrStr
#==============================================================================

#==============================================================================    
def compiler(STATE, token, statement, outpStr, atrStr):
    """
    Функция получения HTML кода из потока токенов

    Входные параметры: 
        STATE - текущее состояние, 
        token - текущий токен, 
        statement - стек состояний, 
        outpStr - текущее значение выходной строки
    
    Выходные параметры:
        STATE - новое состояние, 
        outpStr - новое значение выходной строки
    """
#    if (STATE != 'COMMENT') and token in '%()\n':
#        if STATE != '<html>':
#            outpStr += token
#        else:
#            STATE = 'COMMENT'
#        return STATE, outpStr

###############################################################################    
#   Начальное состояние    

    if STATE == '<html>':
        if token == '\\голова':
            statement.append(STATE)
            STATE = '<head>'
            outpStr += STATE+'\n'
            
        elif token == '\\тело':
            statement.append(STATE)
            STATE = '<body'
            outpStr += STATE
            
        elif token == '%':
            statement.append(STATE)
            STATE = 'COMMENT'
            
        else:
            STATE = 'ERROR'
            

############################################################################### 
#   Неполный   '<body>' 
#   Если уже было "\тело", но не было "(", попадаем в это состояние.
#   Это необходимо, чтобы была возможность вставки аргументов в тег   

    if STATE == '<body':
        if token == '(':
            STATE = '<body>'
            outpStr += '>\n'
            return STATE, outpStr, atrStr
            
        elif token == '::':
            statement.append(STATE)
            STATE = 'ATTRIBUTES'
            atrStr = ''
#            
#        elif token == '%':
#            statement.append(STATE)
#            STATE = 'COMMENT'
#            
############################################################################### 
#   '<body>' == "\тело(" - тело документа
            
    elif STATE == '<body>':
        if token == ')':
            outpStr += '</body>\n</html>'
            STATE = 'END'
            return STATE, outpStr, atrStr
        
        elif token == '\\пар':
            statement.append(STATE)
            STATE = '<p'
            outpStr += STATE
            
            
            
        else:
            outpStr += token

###############################################################################
#   Неполный  '<p>'
           
    elif STATE == '<p':
        if token == '(':
            STATE = '<p>'
            outpStr += '>'
            return STATE, outpStr, atrStr
        
        elif token == '::':
            statement.append(STATE)
            STATE = 'ATTRIBUTES'
            atrStr = ''
###############################################################################
#   '<p>' == '\пар(' - параграф/абзац

    elif STATE == '<p>':
        if token == ')':
            outpStr += '</p>\n'
            STATE = statement.pop()
            return STATE, outpStr, atrStr  
        
        else:
            outpStr += token

###############################################################################  
#   Комментарий. Действует от % до конца строки
          
    elif STATE == 'COMMENT':
        if token == '\n':
            if len(statement) != 0:
                STATE = statement.pop()
            else:
                STATE = '<html>'

############################################################################### 
    elif STATE == 'ATTRIBUTES':
        if token == '::':
            STATE = statement.pop()
            atrList = attributesParser(atrStr)
            atrStr = attributesCompiler(atrList)
            outpStr += atrStr
            atrStr = ''
        
        else:
            atrStr += token
###############################################################################           
    return STATE, outpStr, atrStr
#==============================================================================

# Начало программы

# Начало компиляции
startTime = datetime.datetime.now()
print(startTime.strftime("%d.%m.%Y %H:%M:%S"), 'Начало компиляции')

# Флаг учпешного завершения процесса
processSucessfull = False

# Проверяем наличие аргумента
if len(sys.argv) > 1:
    # Считываем файл по указанному пути
    try:
        fileName = sys.argv[1]        
        f = open(fileName)
        lines = f.readlines()
        text = ''.join(lines)
        f.close()
    except IOError:
        print('Невозможно открыть файл! Проверьте правильность пути.')
        exit()
        
else:
    print('Ошибка! Путь к файлу не указан!')
    exit()


# Стек состояний
statement = []
STATE = '<html>'

inpStr = text
outpStr = '<html>\n'
tokenList = parser(inpStr)
atrStr = ''

#print(tokenList)

for token in tokenList:

    STATE, outpStr, atrStr = compiler(STATE, token, statement, outpStr, atrStr)
    if STATE == 'ERROR':
        print('Ошибка! Компиляция завершена аварийно')
        break
    elif STATE == 'END':
        break

if STATE != 'END':
    print('Ошибка! Неожиданный конец файла.')
    exit()

#print(outpStr)

#if processSucessfull == False:
#    print('Ошибка! Неожиданный конец файла.')
    #exit()
    
# Создаем файл с тем же имененем и расширением .html
k = fileName.rfind('.')
if k != -1:
    fout = open(fileName[:k] + '.html', 'w')
else:
    fout = open(fileName + '.html', 'w')
# Записываем в файл 
fout.write(outpStr)
fout.close()

endTime = datetime.datetime.now()
deltaTime = endTime - startTime
print('Процесс успешно завершен через ', deltaTime)


