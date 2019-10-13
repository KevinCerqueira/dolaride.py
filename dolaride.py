# Dolaride.py
# Author: @Goomez (github.com/Goomez)
# Copyright: Copyright (c) 2019 @Goomez. All rights reserved.
# License: GNU General Public License v3.0
# Version: 1.0.7
# Last Update: 26/09/19

from scrapdoll import ScrapDoll
from datetime import datetime
import time
import tweepy
import os
import sys

class DolaRide():

    TEST = True

    #Web scraping
    scrapDoll = ScrapDoll()

    #Valor do dolar no inicio do dia
    dolarInit = 0.0
    dolarComecoDia = 0.0
    dia = datetime.now()
    txtArq = str(dia.strftime('%d%m%Y')) + '.log'

    #Trava para controlar eventos
    TRAVA = 0

    #Tempo de intervalo de sicronização do script (em segundos)
    TIME = 600 #Por padrão é 600s (10 min)

    #Horario que o script irá parar
    HRFECHA = 1800 #Por padrão é 1800 (18:00 pm)

    #Variaveis de dados de autenticação do twitter
    NUM_API_KEY = None
    NUM_API_SECREAT_KEY = None
    NUM_ACCESS_TOKEN = None
    NUM_ACCESS_TOKEN_SECRET = None

    #Ler o arquivo com os dados para fazer a conexao com o bot
    def readAuth(self):
        arq = None
        try:
            arq = open("auth_code.txt", 'r')
            arq.readline()
            self.NUM_API_KEY = str(arq.readline())
            arq.readline()
            self.NUM_API_SECREAT_KEY = str(arq.readline())
            arq.readline()
            self.NUM_ACCESS_TOKEN = str(arq.readline())
            arq.readline()
            self.NUM_ACCESS_TOKEN_SECRET = str(arq.readline())    
        except:
            print("\nERRO: Não foi possivel ler o arquivo com os dados do BOT")
            self.exitScript()
                


    #Inicia as variáveis necessárias para rodar o programa
    def iniVars(self):
        arq = None
        try:
            arq = open(self.txtArq, 'r')
            self.dolarComecoDia = float(arq.readline())
            self.dolarInit = float(arq.readline())
            arq.close()
        except:
            self.dolarInit = self.scrapDoll.getValDol()
            self.dolarComecoDia = self.dolarInit
            self.arqLog()
        return True
        
    #Mantem o arquivo de log do programa atualizado
    def arqLog(self):
        try:
            arq = open(self.txtArq, 'w')
            arq.write(str(self.dolarComecoDia))
            arq.write('\n')
            arq.write(str(self.dolarInit))
            arq.close()
            return True
        except: 
            print('\nERRO: Não foi possivel editar ou criar o arquivo de log')
        
    #Verifica se esta no horario de começar o script (a partir das 9:00 am)
    def horaDeAbrir(self):
        while(1):
            hora = int(self.dataHora(2))
            if(hora > 910):
                self.TRAVA = 2
                return True
            elif(hora >= 850 and hora <= 910):
                return True
            else:
                time.sleep(60)
    
    #Faz a conexão com o BOT do twitter
    def authTwitter(self):
        self.readAuth()
        api_key = self.NUM_API_KEY
        api_secret_key = self.NUM_API_SECREAT_KEY
        access_token = self.NUM_ACCESS_TOKEN
        access_token_secret = self.NUM_ACCESS_TOKEN_SECRET
        try:
            auth = tweepy.OAuthHandler(api_key, api_secret_key)
            auth.set_access_token(access_token, access_token_secret)
            return tweepy.API(auth)
        except: 
            print('\nERRO: Não foi possivel conectar ao Twitter')
            self.exitScript()

    #Publica os posts no twitter
    def spanMsg(self):
        self.iniVars()
        if(self.TEST): api = self.authTwitter()
        else: pass
        
        while(1):
            msg = self.dollAtuali()
            if(self.TRAVA == 1):
                self.TRAVA = 2
                print(msg)
                try: api.update_status(msg)
                except: pass
            else:
                if(msg != None):
                    self.arqLog()
                    msg = msg + ' - '+ self.dataHora(0)
                    print(msg)
                    try: api.update_status(msg)
                    except: pass

            if(int(self.dataHora(2)) >= self.HRFECHA):
                msg = self.fimDoDia()
                print(msg)
                try: api.update_status(msg)
                except: pass
                self.exitScript()
            time.sleep(self.TIME)

    #Retorna a msg se o dolar subiu ou caiu, caso mantenha seu valor, retorna vazio
    def dollAtuali(self):

        if(self.TRAVA == 0):
            self.TRAVA = 1
            msg = '🌞 Início do dia {}, \n> Valor atual do dólar: R${}.'.format(self.dataHora(4), self.dolarComecoDia)
            return msg
        
        doll = self.scrapDoll.getValDol()
        if(self.dolarInit < doll):
            msg = '🙁 Dólar subiu: R$%.2f -> R$%.2f (+%.2f)' % (self.dolarInit, doll, doll - self.dolarInit)
            self.dolarInit = doll
            return msg
        elif(self.dolarInit > doll):
            msg = '🙂 Dólar caiu: R$%.2f -> R$%.2f (-%.2f)' % (self.dolarInit, doll, self.dolarInit - doll)
            self.dolarInit = doll
            return msg
        else: return None#'\n~ Dolar manteve: R${} -> R${} (~0.00)'.format(self.dolarInit, doll)

    #Retona o horário e data do dia atual
    def dataHora(self, opc):
        dh = datetime.now()
        if(opc == 0): return dh.strftime('%H:%M')
        elif(opc == 1): return dh.strftime('%d/%m/%Y')
        elif(opc == 2): return dh.strftime('%H%M')
        elif(opc == 3): return dh.strftime('%d%m%Y')
        elif(opc == 4): return dh.strftime('%d/%m')

    #Retorna a mensagem de final de dia, com o valor que o dolar fechou no dia
    def fimDoDia(self):
        msg = '\n🌜 Fim do dia {}, \n> Valor do dólar: R${} '.format(self.dataHora(4), self.dolarInit)
        if(self.dolarComecoDia < self.dolarInit):
            return msg + '(subiu +%.2f comparado a ontem).' % (self.dolarInit - self.dolarComecoDia)
        elif(self.dolarComecoDia > self.dolarInit):
            return msg + '(caiu -%.2f comparado a ontem).' % (self.dolarComecoDia - self.dolarInit)
        else: 
            return msg + '(manteve seu valor comparado a ontem)'

    #Verificação para finalizção do script
    def exitScript(self):
        input('\n\t   __SCRIPT FINALIZADO__\n>> Aperte qualquer tecla para fechar o script <<\n')
        sys.exit()
    
    #Setup para testes do script
    def setupTest(self):
        self.readAuth()
        print("\nKEY: " + self.NUM_API_KEY)
        print("\nSECREAT-KEY: " + self.NUM_API_SECREAT_KEY)
        print("\nTOKEN: " + self.NUM_ACCESS_TOKEN)
        print("\nTOKEN-SECRET: " + self.NUM_ACCESS_TOKEN_SECRET)
        self.TIME = 30
        self.HRFECHA = int(self.dataHora(2))+2
        self.TEST = False
        print('\n\n   >> SETUP DE TESTE <<')
        return True

    #interface inicial do script
    def interface(self):
        msgCopy = 'Dolaride.py [version 1.0.6]\nCopyright (c) 2019 @Goomez. All rights reserved.'
        print(msgCopy)
        while(1):
            try:
                psw = int(input('\n>>:'))
                if(psw == 1337): break
            except: pass
        os.system('cls')
        print(msgCopy)
        print('\n\n- Hello sir, como vai?\n')
        try:
            choose = int(input('- Para começar, escolha o tempo de sicronização:\n\t1. 5min\n\t2. 10min\n\t3. 15min\n\t4. 30min\n>>: '))
            if(choose == 1): self.TIME = 300
            elif(choose == 2): self.TIME = 600
            elif(choose == 3): self.TIME = 900
            elif(choose == 4): self.TIME = 1800
            elif(choose == 137): self.setupTest()
            elif(choose > 137): self.TIME = choose
        except: 
            print('\n + Nem uma opção escolhida. Valor padrão: 10min')
        
        if(self.TEST):
            self.horaDeAbrir()
            print('\n\t ...Created by @Goomez...\n\t__INICIALIZANDO O SCRIPT__')
            print('\n- SICRONIZACAO A CADA {}s ({}min) -'.format(self.TIME, self.TIME/60))
        else: pass
        self.spanMsg()

#Main do script
if __name__ == '__main__':
    dolarride = DolaRide()
    dolarride.interface()
    sys.exit()
