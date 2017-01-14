# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 13:11:50 2016

@author: Smith
"""

from PyQt5.QtCore import QFile, QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, QMenu,
        QMessageBox, QTextEdit, QFontDialog)
import os


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupFileMenu()
        self.setupRunMenu()
        self.setupHelpMenu()
        self.setupEditor()

        self.setCentralWidget(self.editor)
        self.setWindowTitle("Редактор ЯГТР")
        
        self.saved = False
        self.path = None
        self.currentText = ""

    def about(self):
        QMessageBox.about(self, "О программе Редактор ЯГТР",
                "<p>Программа Редактор ЯГТР предназначена для создания " \
                "и редактирования файлов на языке ЯГТР. " \
                "ЯГТР - язык гипертекстовой разметки. " \
                "Исходники редактора и компилятора можно найти на " \
                "<a href=\"https://github.com/san-smith/USSRHTML\">GitHub</a></p>")

    def newFile(self):
        """
        Создание нового файла

        Функция, вызываемая пунктом меню "Файл->Новый".
        Метод сначала проверяет, не был ли изменен текст с момента последнего 
        сохранения. Если текст не изменялся, то очищает область ввода и 
        помечает текущее состояние как новый файл, т.е. считает, что путь
        к файлу не указан и файл не сохранен. Если текст изменился, то 
        предлагает сохранить текущий файл и создает новый.
        """
        text = self.editor.toPlainText()
        if self.currentText != text:
            reply = QMessageBox.question(self, 'Новый файл', "Файл не сохранен. Сохранить?", 
                                         QMessageBox.Yes | QMessageBox.No | 
                                         QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.saveFile()
            elif reply == QMessageBox.Cancel:
                return
            else:
                pass

        self.editor.clear()     
        self.saved = False
        self.path = None
        self.title = "Редактор ЯГТР * Новый файл"
        self.setWindowTitle(self.title)
        self.currentText = None

    def openFile(self, path=None):
        text = self.editor.toPlainText()
        if self.currentText != text:
            reply = QMessageBox.question(self, 'Открыть файл', "Файл не сохранен. Сохранить?", 
                                         QMessageBox.Yes | QMessageBox.No | 
                                         QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.saveFile()
            elif reply == QMessageBox.Cancel:
                return
            else:
                pass
        
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", '',
                    "Файл ЯГТР (*.txt *.ygtr)")

        if path:
            inFile = QFile(path)
            if inFile.open(QFile.ReadOnly | QFile.Text):
                text = inFile.readAll()

                try:
                    # Python v3.
                    text = str(text, encoding='utf-8-sig')
                except TypeError:
                    # Python v2.
                    text = str(text)

                self.editor.setPlainText(text)
                self.title = "Редактор ЯГТР " + path
                self.setWindowTitle(self.title)
                self.currentText = self.editor.toPlainText()
                self.path = path
                self.saved = True
                
    def saveFile(self):
        text = self.editor.toPlainText()
        if self.currentText != text:
            self.saved = False
            
        if self.path == None:
            self.saveFileAs()
        else:
            file = open(self.path, 'w', encoding='utf-8-sig')
            text = self.editor.toPlainText()
            file.write(text)
            file.close()
            self.saved = True
            self.title = "Редактор ЯГТР " + self.path
            self.setWindowTitle(self.title)
            self.currentText = self.editor.toPlainText()
    
    def saveFileAs(self, path=None):
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", '',
                                                  "Файл ЯГТР (*.ygtr *.txt)")
        if path:
            self.path = path
            file = open(self.path, 'w', encoding='utf-8-sig')
            text = self.editor.toPlainText()
            file.write(text)
            file.close()
            self.saved = True
            self.title = "Редактор ЯГТР " + path
            self.setWindowTitle(self.title)
            self.currentText = self.editor.toPlainText()
        

    def compileFile(self):

        text = self.editor.toPlainText()
        if self.currentText != text:
            self.saved = False
            
        if self.saved:
            os.system('python.exe ./USSRHTML.py ' + self.path)
            
            k = self.path.rfind('.')            
            try:
                logFile = open(self.path[:k] + '.log', 'r')
                lines = logFile.readlines()
                text = ''
                for line in lines:
                    text += line + '\n'
                QMessageBox.information(self, "Компиляция", str(text))
            except:
                QMessageBox.critical(self, "Компиляция", "Ошибка! Невозможно "\
                                    "открыть лог.")
        else:
            QMessageBox.information(self, "Компиляция", "Файл не сохранен!")

    def runFile(self):

        text = self.editor.toPlainText()
        if self.currentText != text:
            self.saved = False
            
        if self.saved:
            os.system('python.exe ./USSRHTML.py ' + self.path)
            
            k = self.path.rfind('.')            
            try:
                logFile = open(self.path[:k] + '.log', 'r')
                lines = logFile.readlines()
                text = ''
                for line in lines:
                    text += line + '\n'
                QMessageBox.information(self, "Компиляция", str(text))
            except:
                QMessageBox.critical(self, "Компиляция", "Ошибка! Невозможно "\
                                    "открыть лог.")
            
            fileHTML = self.path[:k] + '.html'
            if os.access(fileHTML, os.F_OK):
                os.system(self.path[:k] + '.html')
            else:
                QMessageBox.critical(self, "Компиляция", "Компиляция завершилась неудачей.")

        else:
            QMessageBox.information(self, "Компиляция", "Файл не сохранен!")


    def setupEditor(self):
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.editor = QTextEdit()
        self.editor.setFont(font)

        self.highlighter = Highlighter(self.editor.document())
        
    def setupFont(self):
        font, ok = QFontDialog.getFont(QFont('Courier', 10))
        if ok:
            self.editor.setFont(font)


    def setupFileMenu(self):
        fileMenu = QMenu("Файл", self)
        self.menuBar().addMenu(fileMenu)

        fileMenu.addAction("Новый", self.newFile, "Ctrl+N")
        fileMenu.addAction("Открыть", self.openFile, "Ctrl+O")
        fileMenu.addAction("Сохранить", self.saveFile, "Ctrl+S")
        fileMenu.addAction("Сохранить как ...", self.saveFileAs)
        fileMenu.addSeparator()
        fileMenu.addAction("Настройки шрифта", self.setupFont)
        fileMenu.addSeparator()
        fileMenu.addAction("Выход", QApplication.instance().quit, "Ctrl+Q")

    def setupRunMenu(self):
        runMenu = QMenu("Запуск", self)
        self.menuBar().addMenu(runMenu)
        
        runMenu.addAction("Компилировать", self.compileFile, "F5")
        runMenu.addAction("Компилировать и запустить", self.runFile, "Ctrl+F5")
        
    def setupHelpMenu(self):
        helpMenu = QMenu("Помощь", self)
        self.menuBar().addMenu(helpMenu)

        helpMenu.addAction("О программе", self.about)
        helpMenu.addAction("О &Qt", QApplication.instance().aboutQt)
        
    def closeEvent(self, e):
        text = self.editor.toPlainText()
        if self.currentText != text:
            reply = QMessageBox.question(self, 'Завершение работы', "Файл не сохранен. Сохранить?", 
                                         QMessageBox.Yes | QMessageBox.No | 
                                         QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.saveFile()
            elif reply == QMessageBox.Cancel:
                e.ignore()
            else:
                pass
                 


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = ["\\\\тело\\b", "\\\\голова\\b", "\\\\ж\\b",
                "\\\\к\\b", "\\\\ссылка\\b", "\\\\с\\b", "\\\\адрес\\b",
                "\\\\код\\b", "\\\\блок\\b", "\\\\зг1\\b", "\\\\зг2\\b",
                "\\\\зг3\\b", "\\\\зг4\\b", "\\\\зг5\\b",
                "\\\\зг6\\b", "\\\\рис\\b", "\\\\эл\\b", "\\\\связка\\b",
                "\\\\карта\\b", "\\\\нсп\\b", "\\\\мсп\\b",
                "\\\\абзац\\b", "\\\\а\\b", "\\\\стиль\\b",
                "\\\\под\\b", "\\\\над\\b", "\\\\таблица\\b", "\\\\табл\\b", 
                "\\\\столбец\\b", "\\\\стлб\\b", "\\\\строка\\b", "\\\\стр\\b",
                "\\\\пдч\\b", "\\\\зч\\b", "\\\\нс\\b", "\\\\пре\\b", 
                "\\\\мета\\b", "\\\\скрипт\\b", "\\\\титул\\b", 
                "\\\\цитата\\b", "\\\\заголовок\\b", "\\\\нав\\b", 
                "\\\\секция\\b", "\\\\ремарка\\b", "\\\\подвал\\b",
                "\\\\статья\\b", "\\\\аббр\\b", "\\\\форма\\b", "\\\\ввод\\b",
                "\\\\холст\\b", "\\\\видео\\b", "\\\\аудио\\b"]

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]

        commandFormat = QTextCharFormat()
        commandFormat.setFontWeight(QFont.Bold)
        commandFormat.setForeground(Qt.darkMagenta)
        commandPatterns = ['\\\\', '\\(', '\\)', '<', '>']
        for pattern in commandPatterns:
            self.highlightingRules.append((QRegExp(pattern),
                commandFormat))

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(Qt.red)
#        Если строка начинается с % или перед % не стоит \
        self.highlightingRules.append((QRegExp("^%[^\n]*|[^\\\\]%[^\n]*"),
                singleLineCommentFormat))

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(Qt.darkGreen)
        self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))

        attributeBorderFormat = QTextCharFormat()
        attributeBorderFormat.setForeground(Qt.blue)
        self.highlightingRules.append((QRegExp("::"),# #(QRegExp("((::)+[а-яА-Яa-zA-Z=/\"]+(::))"), #"\\b[A-Za-z0-9_]+(?=\\()"
                attributeBorderFormat))
        
        attributeFormat = QTextCharFormat()
        attributeFormat.setFontItalic(True)
        attributeFormat.setForeground(Qt.blue)
        attributePatterns = ["\\bstyle\\b", "\\bhref\\b", "\\bsrc\\b", 
                             "\\bborder\\b", "\\bcellpadding\\b",
                             "\\bcellspacing\\b"]
        for pattern in attributePatterns:
            self.highlightingRules.append((QRegExp(pattern), attributeFormat))


    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())