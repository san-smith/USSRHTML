# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 13:11:50 2016

@author: Smith
"""

from PyQt5.QtCore import QFile, QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, QMenu,
        QMessageBox, QTextEdit)
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
        self.currentText = None

    def about(self):
        QMessageBox.about(self, "О программе Редактор ЯГТР",
                "<p>Программа Редактор ЯГТР предназначена для создания " \
                "и редактирования файлов на языке ЯГТР. " \
                "ЯГТР - язык гипертекстовой разметки. " \
                "Исходники редактора и компилятора можно найти на " \
                "<a href=\"https://github.com/san-smith/USSRHTML\">GitHub</a></p>")

    def newFile(self):
#        self.editor.clear()
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
        
#    def question(self):
#        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", 
#                                     QMessageBox.Yes | QMessageBox.No | 
#                                     QMessageBox.Cancel, QMessageBox.No)
#        if reply == QMessageBox.Yes:
#            self.saveFile()
#        elif reply == QMessageBox.Cancel:
#            return
#        else:
#            pass 

    def compileFile(self):
        #os.system('python.exe ../../USSRHTML.py ./helloworld.ygtr')
        text = self.editor.toPlainText()
        if self.currentText != text:
            self.saved = False
            
        if self.saved:
            os.system('python.exe ./USSRHTML.py ' + self.path)
            
            try:
                k = self.path.rfind('.')
                logFile = open(self.path[:k] + '.log', 'r')
                text = logFile.readlines()
                QMessageBox.about(self, "Компиляция", str(text))
            except:
                QMessageBox.about(self, "Компиляция", "Ошибка! Невозможно открыть лог.")
        else:
            QMessageBox.about(self, "Компиляция", "Файл не сохранен!")

    def setupEditor(self):
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.editor = QTextEdit()
        self.editor.setFont(font)

        self.highlighter = Highlighter(self.editor.document())

    def setupFileMenu(self):
        fileMenu = QMenu("Файл", self)
        self.menuBar().addMenu(fileMenu)

        fileMenu.addAction("Новый", self.newFile, "Ctrl+N")
        fileMenu.addAction("Открыть", self.openFile, "Ctrl+O")
        fileMenu.addAction("Сохранить", self.saveFile, "Ctrl+S")
        fileMenu.addAction("Сохранить как ...", self.saveFileAs)
        fileMenu.addAction("Выход", QApplication.instance().quit, "Ctrl+Q")

    def setupRunMenu(self):
        runMenu = QMenu("Запуск", self)
        self.menuBar().addMenu(runMenu)
        
        runMenu.addAction("Компилировать", self.compileFile, "F5")
        
    def setupHelpMenu(self):
        helpMenu = QMenu("Помощь", self)
        self.menuBar().addMenu(helpMenu)

        helpMenu.addAction("О программе", self.about)
        helpMenu.addAction("О &Qt", QApplication.instance().aboutQt)


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
                "\\\\под\\b", "\\\\над\\b", "\\\\таблица\\b", "\\\\стлб\\b",
                "\\\\стр\\b", "\\\\стр\\b", "\\\\пдч\\b", "\\\\зч\\b"]

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]

        commandFormat = QTextCharFormat()
        commandFormat.setFontWeight(QFont.Bold)
        commandFormat.setForeground(Qt.darkMagenta)
        self.highlightingRules.append((QRegExp("\\\\"),
                commandFormat))
        self.highlightingRules.append((QRegExp("\\("),
                commandFormat))
        self.highlightingRules.append((QRegExp("\\)"),
                commandFormat))

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(Qt.red)
        self.highlightingRules.append((QRegExp("%[^\n]*"),
                singleLineCommentFormat))

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(Qt.red)

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(Qt.darkGreen)
        self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))

        attributeFormat = QTextCharFormat()
#        functionFormat.setFontItalic(True)
        attributeFormat.setForeground(Qt.blue)
        self.highlightingRules.append((QRegExp("::"),# #(QRegExp("((::)+[а-яА-Яa-zA-Z=/\"]+(::))"), #"\\b[A-Za-z0-9_]+(?=\\()"
                attributeFormat))

        self.commentStartExpression = QRegExp("/\\*")
        self.commentEndExpression = QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                    self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                    startIndex + commentLength);


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())