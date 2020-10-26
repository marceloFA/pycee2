''' This module contains the logic of accessing stackoverflow,
 retrieving the adequate questions for the compiler error 
 and then choosing the best answer for the error'''
 
import re
import requests
from keyword import kwlist
from operator import itemgetter

from bs4 import BeautifulSoup
from difflib import get_close_matches
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.parsers.plaintext import PlaintextParser

from utils import SINGLE_SPACE_CHAR, COMMA_CHAR
from utils import DEFAULT_HTML_PARSER, BASE_URL, BUILTINS, ANSWER_URL


def get_answers(query, traceback, offending_line):
    ''' This coordinate the answer aquisition process.
        1- First use the query to check stackexchange API for related questions
        2- then get these questions answers body
        3- lastly, summarize the answer and make it ready to output to the user.
    '''
    question_ids, accepted_answer_ids = get_questions(query)
    answers_bodies = get_answers_bodies(accepted_answer_ids)
    
    answers = []
    for body in answers_bodies:
        code_position = identify_code(body)
        tester = replace_code( body, code_position, traceback, offending_line)
        answer_body = remove_tags(tester)
        answers.append(answer_body)
    
    return answers


def get_questions(query):
    ''' This will ask stackexchange API for questions and
        return a list of questions urls and 
        their respective accepted answer urls sorted by vote count.'''
    
    response = requests.get(query)
    response_json = response.json()
    question_ids = [question['question_id'] for question in response_json['items']]
    
    accepted_answer_ids = []
    for question in response_json['items']:
        if 'accepted_answer_id' in question:
            field = str(question['accepted_answer_id'])
            accepted_answer_ids.append(field)
        else:
            # TODO: if question has no accepted answer, get most voted answer then
            pass

    return question_ids, accepted_answer_ids


def get_answers_bodies(accepted_answer_ids):

    answers_bodies = []
    for id in accepted_answer_ids:
            answer_response = requests.get(ANSWER_URL.replace('id', id))
            answer_body = answer_response.json()['items'][0]['body']
            answers_bodies.append(answer_body)
    
    return answers_bodies


############# Summary related code

def parse_summarizer(answer_body):
    summary = None
    if len(answer_body.split('\n')) <= 4:
        summary=answer_body
    else:
        tmpSummary=get_summary(answer_body)
        summary=[]
        tmpTest=answer_body.replace(". ", '\n')
        for line in tmpSummary:
            for sec in tmpTest.split('\n'):
                if ((sec.lstrip() != '') and (sec.lstrip() in str(line))):
                    if ("*pre*" in str(line)):
                        sec=sec.replace("*pre*", EMPTY_STRING)
                        exists=False
                        for i in summary:
                            if (sec == i):
                                exists=True
                        if (exists == False):
                            sec=sec.replace("&gt;",">")
                            sec=sec.replace("&lt;COMMA_CHAR<")
                            summary.append(sec)
                    else:
                        exists=False

                        for i in summary:
                            if str(line) == i:
                                exists=True

                        if not exists:
                            new_line=str(line)
                            new_line=new_line.replace("&gt;",">")
                            new_line=new_line.replace("&lt;","<")
                            summary.append(new_line)
        summary='\n'.join(summary)+'\n'
    
    return summary


def get_summary(sentences):
    ''' convert sentences to single string -> not good for code '''

    parser=PlaintextParser.from_string(sentences, Tokenizer("english"))
    # get length of answer(s)
    #numSentences=len(parser.document.sentences)
    length=4  # halve length and round up
    # summarise text
    summariser=LuhnSummarizer()

    return summariser(parser.document, length)


############# Answer related code

def identify_code(text):
    ''' retrieve code from the answer body '''

    startTag="<code>"
    endTag="</code>"
    pos=[]  # list to hold code positions

    if startTag in text:
        for i, c in enumerate(text):
            if c == '<':
                if startTag == text[i:i+len(startTag)]:
                    pos.append([])
                    pos[len(pos)-1].append(i+len(startTag))
                    if (text[i-5:i] == "<pre>"):
                        pos[len(pos)-1].append(1)
                    else:
                        pos[len(pos)-1].append(0)
                if endTag == text[i:i+len(endTag)]:
                    pos[len(pos)-1].append(i)

        for i in range(0, len(pos)):
            tmp=pos[i][2]
            pos[i][2]=pos[i][1]
            pos[i][1]=tmp
    return pos


def remove_tags(text):
    ''' docstring later on '''

    text=text.replace("<pre>","*pre*")
    text=text.replace("</pre>","*pre*")
    cleaner=re.compile('<.*?>')
    cleanText=re.sub(cleaner, '', text)
    return cleanText


def replace_code(text, pos, message, offending_line):
    ''' docstring later on '''

    newText=text
    noTags=remove_tags(text)
    noTagsLines=noTags.split('\n')
    error_lines=message.split('\n')
    error_type=None
    for line in error_lines:
        if "Error: " in line:
            error_type=line.split(SINGLE_SPACE_CHAR, 1)[0]

    error_header=error_lines[1]
    QAOffendingLine=None  # Syntax Error only
    QAErrorLine=None
    
    # check for compiler text in question/answer
    regex=r'(File|Traceback)(.+)\n(.+)((\n)|(\n( |\t)+\^))\n(Arithmetic|FloatingPoint|Overflow|ZeroDivision|Assertion|Attribute|Buffer|EOF|Import|ModuleNotFound|Lookup|Index|Key|Memory|Name|UnboundLocal|OS|BlockingIO|ChildProcess|Connection|BrokenPipe|ConnectionAborted|ConnectionRefused|ConnectionReset|FileExists|FileNotFound|Interrupted|IsADirectory|NotADirectory|Permission|ProcessLookup|Timeout|Reference|Runtime|NotImplemented|Recursion|Syntax|Indentation|Tab|System|Type|Value|Unicode|UnicodeDecode|UnicodeEncode|UnicodeTranslate)(Error:)(.+)'
    match=re.search(regex, noTags)
    if (match):
        QAErrorLine=match.group(0).split('\n')[1]
        # ALSO CHECK QUESTION?

    # if SyntaxError we may need to handle differently
    if error_type == 'SyntaxError:' and QAErrorLine:
        if error_header != offending_line:
            for i in range(len(pos)):
                previous=None
                if bool(pos[i][2]) and (match.group(0) not in text[pos[i][0]:pos[i][1]]):
                    for line in text[pos[i][0]:pos[i][1]].split('\n'):
                        if line == QAErrorLine:
                            QAOffendingLine=previous
                        previous=line

            # check previous line
            # if previous line of code, swap and exit
            if (QAOffendingLine):
                QAOffendingLine=QAOffendingLine.strip()
            if (error_header):
                error_header=error_header.strip()
            if (QAErrorLine):
                QAErrorLine=QAErrorLine.strip()

            # print(QAOffendingLine)
            # print(error_header)
            # print(QAErrorLine)
            # print(offending_line)

            for i in reversed(pos):
                x=pos.index(i)
                if (QAOffendingLine in text[pos[x][0]:pos[x][1]]):
                    newText=newText[:pos[x][0]] + \
                        error_header + newText[pos[x][1]:]
                elif (QAErrorLine in text[pos[x][0]:pos[x][1]]):
                    newText=newText[:pos[x][0]] + \
                        offending_line + newText[pos[x][1]:]
            return newText
    if (QAErrorLine == None):
        tmpQAErrorLine=get_close_matches(
            offending_line, noTagsLines, 1, 0.4)
        if (tmpQAErrorLine == []):
            return text
        else:
            QAErrorLine=tmpQAErrorLine[0]
    if ((QAErrorLine == None) or (QAErrorLine == '')):
        return text
    # print(QAErrorLine)
    # if exists, check for similar lines
    possibleLines=[]
    if (QAErrorLine == None):
        possibleLines=get_close_matches(
            QAErrorLine, noTagsLines, 3, 0.4)
        # SequenceMatcher(None,line,line2).ratio()
        # print(possibleLines)
    # if exists, substitute variables
    if len(possibleLines) > 0 or QAErrorLine:
        # tokenise similar to before, may have to group
        userVariables=[]
        userBuiltin=[]
        tokens=re.split(
            r'[!@#$%^&*_\-+=\(\)\[\]\{\}\\|~`/?.<>:; ]', error_header)
        for x in reversed(tokens):
            if ((x not in kwlist) and (x not in BUILTINS)):
                userVariables.append(x)
            else:
                userBuiltin.append(x)
        userVariables=list(reversed(userVariables))
        userBuiltin=list(reversed(userBuiltin))
        # split
        QALine=None
        if (QAErrorLine):
            QALine=QAErrorLine
        else:
            QALine=possibleLines[0]
        if (',' in QALine):
            while ((', ' in QALine) or (' ,' in QALine)):
                QALine=QALine.replace(", ", COMMA_CHAR)
                QALine=QALine.replace(" ,", COMMA_CHAR)
        QAVariables=[]
        tokens=re.split(r'[!@#$%^&*_\-+=\(\)\[\]\{\}\\|~`/?.<>:; ]', QALine)
        for x in reversed(tokens):
            if ((x not in kwlist) and (x not in BUILTINS)):
                QAVariables.append(x)
        QAVariables=list(reversed(QAVariables))

        for word in reversed(QAVariables):
            if (word == ''):
                QAVariables.remove(word)

        for word in reversed(userVariables):
            if not word:
                userVariables.remove(word)

        # print(QAVariables)
        # print(userVariables)

        newQALine=QALine
        if len(userVariables) == len(QAVariables):
            for word, i in enumerate(QAVariables):
                newQALine.replace(word, userVariables[i])

    return newText


def remove_code(text, pos, maxLength, removeBlocks):
    ''' currently unused. was this a previous version of  querystackoverflow.identify_code?'''

    newText=text
    for i in range(len(pos)):
        to_remove=text[pos[len(pos)-1-i][0]:pos[len(pos)-1-i][1]]
        if removeBlocks and bool(pos[len(pos)-1-i][2]):
            newText=newText.replace(to_remove, '')
        elif len(to_remove) > maxLength:
            newText=newText.replace(to_remove, '')
    return newText