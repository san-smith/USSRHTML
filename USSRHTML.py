'''
USSRHTML - язык гипертекстовой разметки (ЯГТР), котрый мог быть создан в СССР
'''
# импортируем sys для возможности получения файла с исходным текстом в качестве аргумента
import sys

# Проверяем наличие аргумента
if len(sys.argv) > 1:
    # Считываем файл по указанному пути
    try:
        f = open(sys.argv[1])
        lines = f.readlines()
        print(lines)
        text = ''.join(lines)
        f.close()
    except IOError:
        print('Невозможно открыть файл! Проверьте правильность пути.')
        exit()
        
else:
    print('Ошибка! Путь к файлу не указан!')
    exit()
    
# Разбиваем файл на голову и тело
if text.find('\тело(') == -1:
    print('Ошибка!')
    exit()
else:
    head = text[:text.index('\тело(')]
    body = text[text.index('\тело('):]


# Список возможных команд
commands = ["\тело(", "\ж(", "\к("]

# Стек состояний
statement = []

# Создаем файл с тем же имененем и расширением .html
fout = open(sys.argv[1][:-3] + 'html', 'w')
# Записываем в файл 
fout.write('<html>\n')

i = len("\тело(")

STATE = '<body>'            # Текущее состояние
statement.append(STATE)     # Добавляем текущее состояние в стек состояний
fout.write(STATE + '\n')    # И записываем его в выходной файл

# Начинаем разбор текста
s = ''
while i < len(body):
    # Если текущее состояние <body> 
    if STATE == '<body>':
        if body[i] == '\\':
            # Здесь будет разбор новых команд
            pass
        
        elif (body[i] == ')'):
            # Если текущее состояние <body> и встретили ")", то 
            fout.write(s + '\n')        # записываем предыдущий текст
            fout.write('</body>\n')     # и конец тела документа
            break                       # выходим, т.к. дальше ничего быть не должно
        else:
            s += body[i]    # Если просто буква, то добавляем её к тексту           
    
    i += 1


fout.write('</html>\n')
fout.close()


