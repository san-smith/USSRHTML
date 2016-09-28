# -*- coding: utf-8 -*-
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
def parser(inpStr, log=False, path=""):
    """
    Функция разбиения строки на токены
    
    Функция принимает на вход строку, возвращает список токенов, полученных
    из этой строки. Границами токенов могут служить: \, (, ), %, команды,
    символ конца строки и др.
    """
    i = 0
    inpStr += ' '   # Добавим в конец строки для удобства
    tokenList = []  # Список токенов
    s = ''          # Накапливает текущие символы в токен
    while i < len(inpStr)-1:
        if inpStr[i] == '\\':        
#           Если после \ идет \, (, ), %, то добавляем сам символ      
            if inpStr[i+1] in r'\()<>%':
                s += inpStr[i+1]
                i += 2  # И начинаем новую итерацию
                tokenList.append(s)
                s = ''
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
            
        elif (inpStr[i] == '<'):
            s += '&lt;'

        elif (inpStr[i] == '>'):
            s += '&gt;'
            
        else:
            s += inpStr[i]
            
        i += 1
    
    # Если необходимо, запишем список токенов в файл    
    if log == True:
        f = open(path + 'tokenList.txt', 'w') # открываем для записи (writing)
        f.write(str(tokenList)) # записываем текст в файл
        f.close() # закрываем файл
        
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
        atrStr - текущее значение строки атрибутов
    
    Выходные параметры:
        STATE - новое состояние, 
        outpStr - новое значение выходной строки
        atrStr - новое значение строки атрибутов 
    """
    

 
###############################################################################
    """ Отдельно проверим состояние Комментария - если текущее состояние COMMENT,
    то при любом токене выходная строка не изменится.
    Однако, если текущий токен равен переносу строки '\n', то,
    если стек состояний не пуст, то восстанавливаем последнее состояние,
    иначе - текущим состоянием станет '<html>' """ 

    if STATE == 'COMMENT':
        if token == '\n':
            if len(statement) != 0:
                STATE = statement.pop()
            else:
                STATE = '<html>'
                
        return STATE, outpStr, atrStr

###############################################################################      
    elif STATE == 'ATTRIBUTES':
        """ В этом состоянии идет проверка атрибутов тегов.
        Вход в состояние с помощью токена '::',
        Выход из состояния - с помощью повторного токена '::'.""" 
        if token == '::':
            STATE = statement.pop()
            atrList = attributesParser(atrStr)
            atrStr = attributesCompiler(atrList)
            outpStr += atrStr
            atrStr = ''
        
        else:
            atrStr += token
        return STATE, outpStr, atrStr
            
###############################################################################
    if token == '%':
        """ Считаем комментарием все токены от '%' до конца строки"""
        statement.append(STATE)
        STATE = 'COMMENT'

############################################################################### 
    elif token == '::':
        """ Если текущее состояние неполный тег (напр. '<body'), 
        переходим в состояние ATTRIBUTES, чтобы добавить атрибуты тега.
        В противном случае - просто добавляем токен в выходную строку."""
        
        if STATE in NOT_FULL_TAGS:
            statement.append(STATE)
            STATE = 'ATTRIBUTES'
            atrStr = ''
        else:
            outpStr += token
            
###############################################################################
    elif token == '(':
        """ Если текущее состояние неполный тег (напр. '<body'),
        то дописываем закрывающуюся угловую скобку"""
        if STATE in NOT_FULL_TAGS:
            STATE += '>'
            outpStr += '>'
        return STATE, outpStr, atrStr
        
###############################################################################    
    elif token == ')':
        """ Если текущее состояние '<body>' - дописываем конец файла и 
        закрываем его."""
        if STATE == '<body>':
            outpStr += '</body>\n</html>'
            STATE = 'END'
   
        else:
            if STATE in FULL_TAGS:
                """ Если текущее состояние полный тег (напр. <p>), 
                то закрываем его парным тегом (напр. </p>)"""
                outpStr += FULL_TAGS[STATE]
                STATE = statement.pop()
            
            else:
                print(STATE)                
                STATE = 'ERROR'
                print('Отсутствует завершающий тег.')
                
        return STATE, outpStr, atrStr  
        
###############################################################################    
    elif token == '\\голова':
        if STATE == '<html>':
            statement.append(STATE)
            STATE = '<head>'
            outpStr += STATE
        else:
            STATE = 'ERROR'
            
    elif token in HEAD_COMMAND.keys():
        if STATE == '<head>':
            statement.append(STATE)
            STATE = HEAD_COMMAND[token]
            outpStr += STATE
        else:
            STATE = 'ERROR'
        
    elif token == '\\тело':
        if STATE == '<html>':
            statement.append(STATE)
            STATE = '<body'
            outpStr += STATE
        else:
            STATE = 'ERROR'
        
    elif token in BODY_COMMAND.keys():
        statement.append(STATE)
        STATE = BODY_COMMAND[token]
        outpStr += STATE

            
    else:
        outpStr += token    

###############################################################################        
    return STATE, outpStr, atrStr
##==============================================================================

# Начало программы

# Проверяем наличие аргумента
if len(sys.argv) > 1:
    # Считываем файл по указанному пути
    try:
        fileName = sys.argv[1]        
        f = open(fileName, encoding='utf-8-sig')
        lines = f.readlines()
        text = ''.join(lines)
        f.close()
        
        # Создаем файл с тем же имененем и расширением .log
        k = fileName.rfind('.')
        if k != -1:
            outFile = open(fileName[:k] + '.log', 'w')
        else:
            fout = open(fileName + '.log', 'w')

    except IOError:
        print('Невозможно открыть файл! Проверьте правильность пути.', file = outFile)
        exit()
        
else:
    print('Ошибка! Путь к файлу не указан!')
    exit()

# Начало компиляции

startTime = datetime.datetime.now()
print(startTime.strftime("%d.%m.%Y %H:%M:%S"), 'Начало компиляции', file = outFile)

# Флаг учпешного завершения процесса
processSucessfull = False

# Список неполных тегов
NOT_FULL_TAGS = [
            '<head', 
            
            # a
            '<a',
            '<address',
            '<aside',
            '<article',
            '<abbr',
            '<audio',
            
            # b
            '<body',
            '<b',
            '<br',
            # c
            '<code',
            '<cite',
            '<canvas',
            
            # d
            '<div',
            
            # e
            
            
            # f
            '<footer',
            '<form',
            
            # g
            
            
            # h
            '<h1',
            '<h2',
            '<h3',
            '<h4',
            '<h5',
            '<h6',
            '<header',
            
            # i
            '<i',
            '<img',
            '<input',
            
            # j
            
            
            # k
            
            
            # l
            '<li',
            '<link',
            
            # m            
            '<meta',
            
            # n
            '<nav',
            
            # o            
            '<ol',
            
            # p
            '<p',
            '<pre',
            
            # q
            
            
            # r
            
            
            # s
            '<s',
            '<sub',
            '<sup',
            '<style',
            '<script',
            '<section',
            
            # t
            '<table',
            '<td',
            '<tr',
            '<title',
            
            # u
            '<u',
            '<ul',
            
            # v
            '<video',
            
            # w
            
            
            #x
       
                  ' ']   
# Словарь парных тегов
FULL_TAGS = {
            '<html>' : '</html>',
            
            # a
            '<a>' : '</a>',
            '<address>' : '</address>',
            '<aside>' : '</aside>',
            '<article>' : '</article>',
            '<abbr>' : '</abbr>',
            '<audio>' : '</audio>',
            
            # b
            '<body>' : '</body>', 
            '<b>' : '</b>',
            '<br>' : '',
            
            # c 
            '<code>' : '</code>',
            '<cite>' : '</cite>',
            '<canvas>' : '</canvas>',
            
            # d 
            '<div>' : '</div>',
            
            # e
            
            
            # f
            '<footer>' : '</footer>',
            '<form>' : '</form>',
            
            # g
            
            
            # h
            '<h1>' : '</h1>',
            '<h2>' : '</h2>',
            '<h3>' : '</h3>',
            '<h4>' : '</h4>',
            '<h5>' : '</h5>',
            '<h6>' : '</h6>',
            '<head>' : '</head>',
            '<header>' : '</header>',
            
            # i
            '<i>' : '</i>',
            '<img>' : '',
            '<input>' : '',
            
            # j
            
            
            # k
            
            
            # l
            '<li>' : '</li>',
            '<link>' : '',
            
            # m
            '<meta>' : '',
            
            # n
            '<nav>' : '</nav>',
            
            # o
            '<ol>' : '</ol>',
            
            # p
            '<p>' : '</p>',
            '<pre>' : '</pre>',
            
            # q
            
            
            # r
            
            
            # s
            '<s>' : '</s>',
            '<sub>' : '</sub>',
            '<sup>' : '</sup>',
            '<style>' : '</style>',
            '<script>' : '</script>',
            '<section>' : '</section>',
            
            # t
            '<table>' : '</table>',
            '<td>' : '</td>',
            '<tr>' : '</tr>',
            '<title>' : '</title>',
            
            # u
            '<u>' : '</u>', 
            '<ul>' : '</ul>',
            
            # v
            '<video>' : '</video>',
            
            # w
            
            
            # x
            
            
            ' ' : ' '
            }
            
HEAD_COMMAND = {
                '\\стиль' : '<style',
                '\\мета' : '<meta',
                '\\титул' : '<title',
                '\\скрипт' : '<script'
                }
                
BODY_COMMAND = {
                '\\абзац' : '<p',
                '\\а' : '<p',
                '\\ж' : '<b',
                '\\к' : '<i',
                '\\пдч' : '<u',
                '\\зч' : '<s',
                '\\с' : '<a',
                '\\cсылка' : '<a',
                '\\под' : '<sub',
                '\\над' : '<sup',
                '\\зг1' : '<h1',
                '\\зг2' : '<h2',
                '\\зг3' : '<h3',
                '\\зг4' : '<h4',
                '\\зг5' : '<h5',
                '\\зг6' : '<h6',
                '\\блок' : '<div',
                '\\рис' : '<img',
                '\\мсп' : '<ul',
                '\\нсп' : '<ol',
                '\\эл' : '<li',
                '\\связка' : '<link',
                '\\адрес' : '<address',
                '\\таблица' : '<table',
                '\\табл' : '<table',
                '\\строка' : '<tr',
                '\\стр' : '<tr',
                '\\столбец' : '<td',
                '\\стлб' : '<td',
                '\\нс' : '<br',
                '\\пре' : '<pre',
                '\\код' : '<code',
                '\\цитата' : '<cite',
                '\\заголовок' : '<header',
                '\\нав' : '<nav',
                '\\секция' : '<section',
                '\\ремарка' : '<aside',
                '\\подвал' : '<footer',
                '\\статья' : '<article',
                '\\аббр' : '<abbr',
                '\\форма' : '<form',
                '\\ввод' : '<input',
                '\\холст' : '<canvas',
                '\\видео' : '<video',
                '\\аудио' : '<audio'
                }

# Стек состояний
statement = []
STATE = '<html>'

inpStr = text
outpStr = '<!DOCTYPE html>\n<html>\n'
k = fileName.rfind('/')
if k != -1:
    path = fileName[:k] + '/'
else:
    path = ''
#    k = fileName.rfind('\\')
#    path = fileName[:k] + '/'
    
tokenList = parser(inpStr, log=False, path=path)
atrStr = ''

for token in tokenList:

    STATE, outpStr, atrStr = compiler(STATE, token, statement, outpStr, atrStr)
    if STATE == 'ERROR':
        print('Ошибка! Компиляция завершена аварийно', file = outFile)
        break
    elif STATE == 'END':
        break

if STATE != 'END':
    print('Ошибка! Неожиданный конец файла.', file = outFile)
    exit()

    
# Создаем файл с тем же имененем и расширением .html
k = fileName.rfind('.')
if k != -1:
    fout = open(fileName[:k] + '.html', 'w', encoding='utf-8-sig')
else:
    fout = open(fileName + '.html', 'w', encoding='utf-8-sig')
# Записываем в файл 
fout.write(outpStr)
fout.close()

endTime = datetime.datetime.now()
deltaTime = endTime - startTime
print('Процесс успешно завершен через ', deltaTime, file = outFile)


