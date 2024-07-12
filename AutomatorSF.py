from asyncio import exceptions
from operator import contains
from tkinter.tix import Select
from selenium import webdriver
from selenium import common
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
import time
import pyautogui
import glob
import os
import autoit
import json
import p20BotTelegram as teleg
from pathlib import Path
import pyperclip
from flask import Flask, jsonify
import pygetwindow as gw
from selenium.webdriver.chrome.options import Options

pyautogui.PAUSE = 1
dirbase = r'C:\Orquestrador\65Automacao'

# Creating Instance
option = Options()
# Working with the 'add_argument' Method to modify Driver Default Notification
option.add_argument('--disable-notifications')
# Passing Driver path alongside with Driver modified Options
navegador = webdriver.Chrome(executable_path= "C:\\Orquestrador\\AutomatorSalesForce\\chromedriver.exe", chrome_options= option)
wait = WebDriverWait(navegador, 20)
navegador.implicitly_wait(20)
url= 'https://oinovafibra.my.salesforce.com'
navegador.get(url)
navegador.maximize_window()
sessao_original=navegador.current_window_handle


#-----------------------------------------------------------------------------------------------------------
def ler_json(arq_json):
	with open(arq_json, 'r', encoding='utf8') as f:
		return json.load(f)

#-----------------------------------------------------------------------------------------------------------
def ler_ids():
	auth_jsn = ler_json('auth.json')
	dados_auth = auth_jsn['result']
	ids=[]

	for id in dados_auth:
		ids.append(str(id['chatid']))

	return ids

#-----------------------------------------------------------------------------------------------------------
def verificaSessao():
  sessao=False
  try:
    sessao = navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/header/div[2]/span/div[2]/ul/li[9]/span/button/div/span[1]/div/span').is_displayed()
  except common.exceptions.NoSuchElementException as errotela:
    sessao = False
    pass

  if sessao:
    return True
  else:
    return False

#-----------------------------------------------------------------------------------------------------------
def loginSalesForce():

  # Definindo variáveis
  #_____________________________________
  ids = ler_ids()
  dados=ler_json('User.json')
  loginUser=dados['usuario']
  senhaUser=dados['senha']
  pa=dados['pa']
  #_____________________________________

  jsonCap = dirbase+'\Captcha.json'
  fileObj = Path(jsonCap)
  if fileObj.is_file():
    os.remove(fileObj)
  
  fotoCap = dirbase+'\Captcha.png'
  fileObj = Path(fotoCap)
  if fileObj.is_file():
    os.remove(fileObj)
  
  #Envio de mensagem telegram
  for id in ids:
    msg='Iniciando login SalesForce - Máquina '+pa
    teleg.send_msg(id, msg)

  # Inicializaçao do navegador
  # url= 'https://oinovafibra.my.salesforce.com'
  # navegador.get(url)
  # navegador.maximize_window()
  # sessao=navegador.session_id
  # time.sleep(4)

  # Verificando elemento da tela de login para saber se estou ou nao nela.
  sucessoLogin = navegador.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/img').is_displayed()

  # Enquanto eu estiver na tela de login continuo tentando logar
  while sucessoLogin:
    # time.sleep(3)
    navegador.find_element(By.XPATH,'/html/body/div[1]/div/form/div[2]/div[1]/input').send_keys(loginUser) #Digita Login
    # time.sleep(1)
    navegador.find_element(By.XPATH,'/html/body/div[1]/div/form/div[2]/div[2]/input').send_keys(senhaUser) #Digita Senha
    # time.sleep(1)
    try:
      statusCaptcha=navegador.find_element(By.XPATH,'/html/body/div[1]/div/form/div[2]/div[3]/div[1]/img').is_displayed() #Captura imagem do captcha
    except common.exceptions.NoSuchElementException as errotela:
      statusCaptcha = False
      pass

    if statusCaptcha:
      navegador.find_element(By.XPATH,'/html/body/div[1]/div/form/div[2]/div[3]/div[1]/img').screenshot('Captcha.png') #Captura imagem do captcha
      time.sleep(1)
    
      # Envia Captcha para usuários
      for id in ids:
        teleg.send_captcha(id, pa, 'Captcha.png')

      # Quando o arquivo json com a senha do captcha cair no disco eu continuo
      while True: 
        time.sleep(3)
        fileName = dirbase+'\Captcha.json'
        fileObj = Path(fileName)
        if fileObj.is_file():
          break
        else:
          continue
    
      # Leitura de senha captcha
      dados=ler_json(dirbase+'\Captcha.json')
      saida_captcha=dados['captcha']

      navegador.find_element(By.XPATH,'/html/body/div[1]/div/form/div[2]/div[4]/input').send_keys(saida_captcha) #Digita captcha
      # time.sleep(2)

    navegador.find_element(By.XPATH,'/html/body/div[1]/div/form/div[2]/button').click() #Clicar em continuar para logar
    # time.sleep(15)

    # Verificaçao para saber se ainda estou na tela de login
    try:
      sucessoLogin = navegador.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/img').is_displayed()
    except:
      sucessoLogin = False
      break

    if sucessoLogin:
      for id in ids:
        msg='Captcha incorreto, iniciando captura novamente❌ - Máquina '+pa
        teleg.send_msg(id, msg)

        jsonCap = dirbase+'\Captcha.json'
        fileObj = Path(jsonCap)
        if fileObj.is_file():
          os.remove(fileObj)
        
        fotoCap = dirbase+'\Captcha.png'
        fileObj = Path(fotoCap)
        if fileObj.is_file():
          os.remove(fileObj)

  for id in ids:
    msg='Login efetuado com sucesso✅ - Máquina '+pa
    teleg.send_msg(id, msg)
  
  jsonCap = dirbase+'\Captcha.json'
  fileObj = Path(jsonCap)
  if fileObj.is_file():
    os.remove(fileObj)
  
  fotoCap = dirbase+'\Captcha.png'
  fileObj = Path(fotoCap)
  if fileObj.is_file():
    os.remove(fileObj)

  if sucessoLogin:
    return True
  else:
    return False

  # time.sleep(15)
  # navegador.find_element_by_xpath('/html/body/div[4]/div[1]/section/header/div[2]/div[2]/div/button').click()

#-----------------------------------------------------------------------------------------------------------
def consultaAgenda(pedido):
  # processo de extraçao de agenda
  e=True
  listacalendar=""
  try:
    navegador.switch_to.window(sessao_original)
    navegador.maximize_window()
    titles=gw.getAllTitles()
    tamanhoTitle=len(titles)
    for op in range(0, tamanhoTitle):
      janela = titles[op]
      if 'All' in janela or 'Lightning' in janela or '| Salesforce' in janela:
        window = gw.getWindowsWithTitle(janela)[0]
        window.activate()
        break
    # time.sleep(20)
    sessao = verificaSessao()
    while True:
      if sessao:
        break
      else:
        url= 'https://oinovafibra.my.salesforce.com'
        navegador.get(url)
        login = loginSalesForce()
        if login == True:
          sessao=True
        else:
          sessao=False
      
    time.sleep(3)
    while True:
      xis = pyautogui.locateOnScreen('xisverde.png')
      print(xis)
      if xis == None:
        break
      else:
        pyautogui.click(x=xis[0] + 2, y=xis[1] + 2, clicks=1, interval=0.5, button='left') # Clica no X de fechar pedido
        time.sleep(3)
    # for h in range(2,4):
    #   try:
    #     xis=navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/div[1]/div/div[1]/div[2]/div/div/ul[2]/li['+str(h)+']/div[2]/button/lightning-primitive-icon/svg/g/path').is_displayed()
    #   except common.exceptions.NoSuchElementException as erroxis:
    #     xis = False
    #     pass
    #   if xis:
    #     navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/div[1]/div/div[1]/div[2]/div/div/ul[2]/li['+str(h)+']/div[2]/button/lightning-primitive-icon/svg/g/path').click()

    statusTela=navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/header/div[2]/span/div[2]/ul/li[9]/span/button/div/span[1]/div/span').is_displayed()
    # teste=navegador.window_handles
    # print(teste)
    
    if statusTela:
      # clickoi = pyautogui.locateOnScreen('logoOi.png')
      # pyautogui.click(x=clickoi[0] + 5, y=clickoi[1] + 5, clicks=1, interval=0.5, button='left') # Clica na logo oi caso campo pesquisa esteja clicado
      pyautogui.press('esc')

      erros=""
      navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/header/div[2]/div[2]/div/button').click() # Clique em pesquisar
      pyautogui.hotkey('ctrl','a')
      pyautogui.press('backspace')
      pyautogui.hotkey('shift','tab')
      pyperclip.copy('Pedidos')
      pyautogui.hotkey('ctrl','v')
      pyautogui.press('enter')
      pyperclip.copy(pedido)
      pyautogui.press('tab')
      pyautogui.hotkey('ctrl','v')


      # time.sleep(2)
      # navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div/div/div[1]/div/div[1]/div/lightning-grouped-combobox/div/div/lightning-base-combobox/div/div[1]/input').send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + 'Pedidos' + Keys.ENTER + Keys.ENTER) # Coloca o tipo de pesquisa como pedido
      
      # navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div/div/div[1]/div/div[1]/lightning-input/div/input').send_keys(pedido)
      time.sleep(2)

      wait = WebDriverWait(navegador, 2)
      navegador.implicitly_wait(2)
      click1=True
      click2=True
      try:                                                  
        statusCaixaPedido = navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div[1]/div/div[1]/div/div[2]/div[1]/div/search_dialog-instant-results-list/div/search_dialog-instant-result-item[1]/div/div[1]/records-highlights-icon/force-record-avatar/span/img').is_displayed()
      except common.exceptions.NoSuchElementException as errocaixapedido:
        statusCaixaPedido = False
        print('Erro não encontrado')
        
      
      if statusCaixaPedido:
        print('Entrei modo 1')
        try:
          navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div[1]/div/div[1]/div/div[2]/div[1]/div/search_dialog-instant-results-list/div/search_dialog-instant-result-item[1]/div/div[1]/records-highlights-icon/force-record-avatar/span/img').click()
        except common.exceptions.NoSuchElementException as errocaixapedido:
          click1 = False
          print('Erro click 1')
      else:
        click1=False

      if click1 == False:    
        try:
          statusCaixaPedido2 = navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div[2]/div/div[1]/div/div[2]/div[1]/div/search_dialog-instant-results-list/div/search_dialog-instant-result-item[1]/div/div[1]/records-highlights-icon/force-record-avatar/span/img').is_displayed()
        except common.exceptions.NoSuchElementException as errocaixapedido:
          statusCaixaPedido2 = False
          print('Erro não encontrado 2')
          
        
        if statusCaixaPedido2:
          print('Entrei modo 2')
          try:
            navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div[2]/div/div[1]/div/div[2]/div[1]/div/search_dialog-instant-results-list/div/search_dialog-instant-result-item[1]/div/div[1]/records-highlights-icon/force-record-avatar/span/img').click()
          except common.exceptions.NoSuchElementException as errocaixapedido:
            click2 = False
            print('Erro click 2')
        else:
          click2=False
      
      if click2 == False:
        print('Entei modo 3')
        clickpedido = pyautogui.locateOnScreen('iconepedido.png')
        pyautogui.click(x=clickpedido[0] + 5, y=clickpedido[1] + 5, clicks=1, interval=0.5, button='left') # Clica pedido
      
      wait = WebDriverWait(navegador, 20)
      navegador.implicitly_wait(20)

      # if statusCaixaPedido:
      #   #Primeira tentativa de clique no pedido
      #   navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div[1]/div/search_dialog-instant-results-list/div/search_dialog-instant-result-item[1]/div/div[1]/records-highlights-icon/force-record-avatar/span/img').click()
      #   try:
      #     pedidonatela = navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/div[1]/div/div[2]/div[2]/section/div/div/section/div/div[2]/div/div/div/div[1]/div/div[3]/div[1]/div/div/section/div/div/article/div[2]/div/div[1]/div/div/div[1]/div[1]/div/div[2]/span/span').is_displayed()
      #   except common.exceptions.NoSuchElementException as erropedido:
      #     pedidonatela = False
      #     pass
      #   if pedidonatela:
      #     numpedido = navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/div[1]/div/div[2]/div[2]/section/div/div/section/div/div[2]/div/div/div/div[1]/div/div[3]/div[1]/div/div/section/div/div/article/div[2]/div/div[1]/div/div/div[1]/div[1]/div/div[2]/span/span').text
      #     if numpedido.contains(pedido):
      #       pass
      #     else:
      #       botaopedido = pyautogui.locateOnScreen('pedido.png')
      #       pyautogui.click(x=botaopedido[0] + 5, y=botaopedido[1] + 5, clicks=1, interval=0.5, button='left') # Clica em Fechar Pendencia
      #   else:
      #     botaopedido = pyautogui.locateOnScreen('pedido.png')
      #     pyautogui.click(x=botaopedido[0] + 5, y=botaopedido[1] + 5, clicks=1, interval=0.5, button='left') # Clica em Fechar Pendencia
      # else:
      #   botaopedido = pyautogui.locateOnScreen('pedido.png')
      #   pyautogui.click(x=botaopedido[0] + 5, y=botaopedido[1] + 5, clicks=1, interval=0.5, button='left') # Clica em Fechar Pendencia

      # time.sleep(3)
      statusPedido = navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/div[1]/div/div[2]/div[2]/section/div/div/section/div/div[2]/div/div/div/div[1]/div/div[1]/div/header/div[2]/ul/li[4]/div/div/div/span').text
      # time.sleep(1)
      if statusPedido == 'Cancelado':
        print('O pedido está cancelado!')
        e=False
      elif statusPedido == 'Pendência Cliente':
        print('O pedido pode ser agendado.')
        time.sleep(2)
        statusAgendamento = navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/div[1]/div/div[2]/div[2]/section/div/div/section/div/div[2]/div/div/div/div[1]/div/div[3]/div[1]/div/div/section/div/div/article/div[2]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/span').text
        if statusAgendamento == '':
          print('clicar em fechar pendência')
          navegador.find_element(By.XPATH,'/html/body').send_keys(Keys.SPACE)
          # time.sleep(2)
          time.sleep(4)
          fecharPendencia = pyautogui.locateOnScreen('fecharPendencia.png')
          print(fecharPendencia)
          pyautogui.click(x=fecharPendencia[0] + 5, y=fecharPendencia[1] + 5, clicks=1, interval=0.5, button='left') # Clica em Fechar Pendencia
          time.sleep(12)
          
          for x in range(1,3):
            try:
              statusConsulta = navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[4]/div/button').is_displayed() # Verifica se botao consulta Slots está na tela
            except common.exceptions.NoSuchElementException as errotela:
              statusConsulta = False
              pass

            if statusConsulta:
              print('Consulta agenda na tela!')
              navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[4]/div/button').click() # Clica se botao consulta Slots está na tela
              
              time.sleep(5)
              try:
                statusTelaAgenda=navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[5]/div[1]/div[1]').is_displayed() # Verifica div do primeiro slot está na tela
              except common.exceptions.NoSuchElementException as errotela:
                statusTelaAgenda = False
              pass
              
              if statusTelaAgenda:
                
                listacalendar=[]
                print('to na tela')
                navegador.implicitly_wait(2)
                for i in range(1,8):
                  diadasemana=''
                  diadomes   =''
                  hora1      =''
                  hora2      =''
                  
                  try:
                    diadasemana=navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[5]/div[1]/div['+str(i)+']/div/div[1]/span').text # Pega texto dia da semana
                    diadomes=navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[5]/div[1]/div['+str(i)+']').get_property('id') # Pega texto dia do mês
                    diadomes=diadomes[10 : ]
                    navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[5]/div[1]/div['+str(i)+']/div/div[1]/span').click() # Clica no botao do dia
                  except common.exceptions.NoSuchElementException as erro:
                    pass
        
                  time.sleep(1)
                  try:
                    slotdisponivel = navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[5]/div[1]/div['+str(i)+']/div/div[1]/span').is_displayed()
                  except common.exceptions.NoSuchElementException as erro:
                    slotdisponivel = False

                  if slotdisponivel:
                    try:
                      hora1=navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[9]/div[1]/div[1]/div/div/span').text
                      hora2=navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[9]/div[1]/div[2]/div/div/span').text
                    except common.exceptions.NoSuchElementException as erro2:
                      pass
                  
                    diccalendar={
                      "data":diadomes,
                      "hora":hora1,
                      "color":"green",
                      "xi":0,
                      "yi":0,
                      "xf":0,
                      "yf":0,
                      "ocr":"",
                      "agendado":0,
                      "status":"",
                      "inicioData":"",
                      "inicioHora":""
                    }
                    listacalendar.append(diccalendar)
                    if hora2!='':
                      diccalendar={
                      "data":diadomes,
                      "hora":hora2,
                      "color":"green",
                      "xi":0,
                      "yi":0,
                      "xf":0,
                      "yf":0,
                      "ocr":"",
                      "agendado":0,
                      "status":"",
                      "inicioData":"",
                      "inicioHora":""
                      }
                      listacalendar.append(diccalendar)
                    
                    print('dia da semana = '+diadasemana)
                    print('dia do mes = '+diadomes)
                    print('hora1 = '+hora1)
                    print('hora2 = '+hora2)
              else:
                erros="Nao foi possivel carregar agenda na tela"
                e=False
                statusErroAgenda=navegador.find_element(By.XPATH,'/html/body/span/div/div[1]/div/div[1]/h2').is_displayed()
                statusFecharAgenda=navegador.find_element(By.XPATH,'/html/body/div[3]/div/div/div[2]/div[3]/button').is_displayed()
                if statusFecharAgenda:
                  navegador.find_element(By.XPATH,'/html/body/div[3]/div/div/div[2]/div[3]/button').click()
                if statusErroAgenda:
                  texto=navegador.find_element(By.XPATH,'/html/body/span/div/div[1]/div/div[1]/h2').text
                  if texto=='Error':
                    erros="Erro na agenda"
                    navegador.find_element(By.XPATH,'/html/body/span/div/div[1]/div/div[3]/button').click()

              break
            else:
              time.sleep(5)
              e=False
              continue    
      else:
        listacalendar=""
        erros='Pedido sem status de Pendencia'
        e=False
    navegador.implicitly_wait(20)
  except:
    erros='Nao foi possivel carregar a agenda'
    print(erros)
    listacalendar=""
    e=False
    pass
  
  if e:
    statusRetorno="Agenda coletada com sucesso"
  else:
    statusRetorno="Erro ao coletar agenda"

  dic={ "Success":True,
        "Data":{
          "Lead":[
            {
              "codigoPedido":pedido,
              "produto":"x",
              "velocidade":"x",
              "endereco":"x",
              "nome":"x",
              "CPF":"x",
              "dataNascimento":"x",
              "sexo":"x",
              "sucesso":e,
              "status":statusRetorno
            }
          ],
          "calendar":"",
          "erro":erros,
          "sistema":"SalesForce"
        },
        "Message":""
      }

  dic["Data"]["calendar"]=listacalendar
  jsondic=json.dumps(dic)
  url= 'https://oinovafibra.my.salesforce.com'
  navegador.get(url)
  return jsondic

#-----------------------------------------------------------------------------------------------------------
def agendamento(pedido, data, hora):
  erros=""
  statusMarcacao="NOK"
  try:
    navegador.switch_to.window(sessao_original)
    navegador.maximize_window()
    titles=gw.getAllTitles()
    tamanhoTitle=len(titles)
    for op in range(0, tamanhoTitle):
      janela = titles[op]
      if 'All' in janela or 'Lightning' in janela or '| Salesforce' in janela:
        window = gw.getWindowsWithTitle(janela)[0]
        window.activate()
        break
    
    sessao = verificaSessao()
    while True:
      if sessao:
        break
      else:
        url= 'https://oinovafibra.my.salesforce.com'
        navegador.get(url)
        login = loginSalesForce()
        if login == True:
          sessao=True
        else:
          sessao=False
      
    time.sleep(3)
    while True:
      xis = pyautogui.locateOnScreen('xisverde.png')
      print(xis)
      if xis == None:
        break
      else:
        pyautogui.click(x=xis[0] + 2, y=xis[1] + 2, clicks=1, interval=0.5, button='left') # Clica no X de fechar pedido
        time.sleep(3)
    # processo de agendamento
    statusTela=navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/header/div[2]/span/div[2]/ul/li[9]/span/button/div/span[1]/div/span').is_displayed()
    # teste=navegador.window_handles
    # print(teste)
    
    if statusTela:
      pyautogui.press('esc')
      erros=""
      navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/header/div[2]/div[2]/div/button').click() # Clique em pesquisar
      # time.sleep(2)
      pyautogui.hotkey('ctrl','a')
      pyautogui.press('backspace')
      pyautogui.hotkey('shift','tab')
      pyperclip.copy('Pedidos')
      pyautogui.hotkey('ctrl','v')
      pyautogui.press('enter')
      pyperclip.copy(pedido)
      pyautogui.press('tab')
      pyautogui.hotkey('ctrl','v')

      # navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div/div/div[1]/div/div[1]/div/lightning-grouped-combobox/div/div/lightning-base-combobox/div/div[1]/input').send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + 'Pedidos' + Keys.ENTER + Keys.ENTER) # Coloca o tipo de pesquisa como pedido
      
      #navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div/div/div[1]/div/div[1]/lightning-input/div/input').send_keys(pedido)
      time.sleep(2)

      wait = WebDriverWait(navegador, 2)
      navegador.implicitly_wait(2)
      click1=True
      click2=True
      try:                                                  
        statusCaixaPedido = navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div[1]/div/div[1]/div/div[2]/div[1]/div/search_dialog-instant-results-list/div/search_dialog-instant-result-item[1]/div/div[1]/records-highlights-icon/force-record-avatar/span/img').is_displayed()
      except common.exceptions.NoSuchElementException as errocaixapedido:
        statusCaixaPedido = False
        print('Erro não encontrado')
        
      
      if statusCaixaPedido:
        print('Entrei modo 1')
        try:
          navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div[1]/div/div[1]/div/div[2]/div[1]/div/search_dialog-instant-results-list/div/search_dialog-instant-result-item[1]/div/div[1]/records-highlights-icon/force-record-avatar/span/img').click()
        except common.exceptions.NoSuchElementException as errocaixapedido:
          click1 = False
          print('Erro click 1')
      else:
        click1=False

      if click1 == False:    
        try:
          statusCaixaPedido2 = navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div[2]/div/div[1]/div/div[2]/div[1]/div/search_dialog-instant-results-list/div/search_dialog-instant-result-item[1]/div/div[1]/records-highlights-icon/force-record-avatar/span/img').is_displayed()
        except common.exceptions.NoSuchElementException as errocaixapedido:
          statusCaixaPedido2 = False
          print('Erro não encontrado 2')
          
        
        if statusCaixaPedido2:
          print('Entrei modo 2')
          try:
            navegador.find_element(By.XPATH,'/html/body/div[4]/div[2]/div[2]/div/div[1]/div/div[2]/div[1]/div/search_dialog-instant-results-list/div/search_dialog-instant-result-item[1]/div/div[1]/records-highlights-icon/force-record-avatar/span/img').click()
          except common.exceptions.NoSuchElementException as errocaixapedido:
            click2 = False
            print('Erro click 2')
        else:
          click2=False
      
      if click2 == False:
        print('Entei modo 3')
        clickpedido = pyautogui.locateOnScreen('iconepedido.png')
        pyautogui.click(x=clickpedido[0] + 5, y=clickpedido[1] + 5, clicks=1, interval=0.5, button='left') # Clica pedido
      
      wait = WebDriverWait(navegador, 20)
      navegador.implicitly_wait(20)

      # time.sleep(3)
      statusPedido = navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/div[1]/div/div[2]/div[2]/section/div/div/section/div/div[2]/div/div/div/div[1]/div/div[1]/div/header/div[2]/ul/li[4]/div/div/div/span').text
      # time.sleep(1)
      if statusPedido == 'Cancelado':
        print('O pedido está cancelado!')
      elif statusPedido == 'Pendência Cliente':
        print('O pedido pode ser agendado.')
        time.sleep(2)
        statusAgendamento = navegador.find_element(By.XPATH,'/html/body/div[4]/div[1]/section/div[1]/div/div[2]/div[2]/section/div/div/section/div/div[2]/div/div/div/div[1]/div/div[3]/div[1]/div/div/section/div/div/article/div[2]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/span').text
        statusAgendamento=''
        if statusAgendamento == '':
          print('clicar em fechar pendência')
          navegador.find_element(By.XPATH,'/html/body').send_keys(Keys.SPACE)
          # time.sleep(2)
          time.sleep(4)
          fecharPendencia = pyautogui.locateOnScreen('fecharPendencia.png')
          print(fecharPendencia)
          pyautogui.click(x=fecharPendencia[0] + 5, y=fecharPendencia[1] + 5, clicks=1, interval=0.5, button='left') # Clica em Fechar Pendencia
          time.sleep(12)
          
          for x in range(1,3):
            statusConsulta = navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[4]/div/button').is_displayed() # Verifica se botao consulta Slots está na tela
            
            if statusConsulta:
              print('Consulta agenda na tela!')
              navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[4]/div/button').click() # Clica se botao consulta Slots está na tela
              
              time.sleep(5)
              statusTelaAgenda=navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[5]/div[1]/div[1]').is_displayed() # Verifica div do primeiro slot está na tela
              if statusTelaAgenda:
                try:
                  navegador.find_element(By.XPATH,'//*[@id="slot-data-'+data+'"]/div/div[2]/span').click()
                except common.exceptions.NoSuchElementException as erro1:
                  erros='Slot com a data solicitada nao encontrado'
                  pass
                #  como agendar slot hora
                try:
                  hora1=navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[9]/div[1]/div[1]/div/div/span').text
                  hora2=navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[9]/div[1]/div[2]/div/div/span').text
                except common.exceptions.NoSuchElementException as erro2:
                  erros='Slot com a hora solicitada nao encontrado'
                  pass
                
                if hora==hora1:
                  try:
                    navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[9]/div[1]/div[1]/div/div/span').click() # Clica no slot de horário
                  except common.exceptions.NoSuchElementException as erro3:
                    erros='Slot com a hora solicitada nao encontrado'
                    pass
                else:
                  try:
                    navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[9]/div[1]/div[2]/div/div/span').click() # Clica no slot de horário
                  except common.exceptions.NoSuchElementException as erro4:
                    erros='Slot com a hora solicitada nao encontrado'
                    pass
                
                navegador.find_element(By.XPATH,'/html/body/span/div/span/div/ng-view/div/div/bptree/child[6]/div/section/form/div[1]/div/child/div/div/div[10]/div[1]/div/button').click() # Clica no botão de avançar
                time.sleep(2)
                botaoConfirmar = pyautogui.locateOnScreen('confirmar.png')
                print(botaoConfirmar)
                pyautogui.click(x=botaoConfirmar[0] + 5, y=botaoConfirmar[1] + 5, clicks=1, interval=0.5, button='left') # Clica em Fechar Pendencia
                time.sleep(4)

                dropdown1=navegador.find_element(By.ID,"SL_Motivo")# seleciona motivo
                dd1 = Select(dropdown1)
                dd1.select_by_visible_text("Liberado")

                dropdown2=navegador.find_element(By.ID,"SL_Submotivo")# seleciona submotivo
                dd2 = Select(dropdown2)
                dd2.select_by_visible_text("Com agendamento")

                navegador.find_element(By.XPATH,"/html/body/span/div/span/div/ng-view/div/div/bptree/child[8]/div/section/form/div[1]/div/child[6]/div/ng-form/div[2]/div[1]/textarea").send_keys('Agendamento feito via Robô')
                
                navegador.find_element(By.XPATH,"/html/body/span/div/span/div/ng-view/div/div/bptree/child[8]/div/section/form/div[2]/div/div[2]/div/div[2]/div/div/div/p").click()
                mensagemMarcacao=navegador.find_element(By.XPATH,"/html/body/span/div/span/div/ng-view/div/div/bptree/child[10]/div/section/form/div[1]/div/child/div/ng-form/div/div/div").text
                if mensagemMarcacao=='Ok, Pendência Fechada.':
                  statusMarcacao="OK"
                else:
                  statusMarcacao="NOK"
                
                navegador.find_element(By.XPATH,"/html/body/span/div/span/div/ng-view/div/div/bptree/child[10]/div/section/form/div[2]/div/div[2]/div/div[2]/div/div/div/p").click()

              else:
                erros="Nao foi possivel carregar agenda na tela"
                statusFecharAgenda=navegador.find_element(By.XPATH,'/html/body/div[3]/div/div/div[2]/div[3]/button').is_displayed()
                if statusFecharAgenda:
                  navegador.find_element(By.XPATH,'/html/body/div[3]/div/div/div[2]/div[3]/button').click()

              break
            else:
              time.sleep(5)
              continue      
    
    if erros=="":
      statusMarcacao="OK"
    else:
      statusMarcacao="NOK"
  except:
    print('Erro de marcacao')
    statusMarcacao="NOK"
    
  dic={ "Success": True,
        "Data": {
        "codigoPedido":pedido,
        "status":statusMarcacao,
        "erro":erros
        },
        "Message":""
      }
  jsondic=json.dumps(dic)
  url= 'https://oinovafibra.my.salesforce.com'
  navegador.get(url)
  return jsondic
  
#-----------------------------------------------------------------------------------------------------------
loginSalesForce()
# def Main():
#   ids = ler_ids()
#   dados=ler_json('User.json')
#   pa=dados['pa']

#   jsonCap = r'C:\00Producao\03PAVCRVTahto\SalesForce\00Dev\Captcha.json'
#   fileObj = Path(jsonCap)
#   if fileObj.is_file():
#     os.remove('Captcha.json')
  
#   fotoCap = r'C:\00Producao\03PAVCRVTahto\SalesForce\00Dev\Captcha.png'
#   fileObj = Path(fotoCap)
#   if fileObj.is_file():
#     os.remove('Captcha.png')
  
#   # loginSalesForce()
#   # opa=consultaAgenda('149371')
#   # opa=agendamento('149371', '03/06/2022', '08:00 - 12:00')
#   # print(opa)
#   # if parametro == 'agendamento':
#   #   loginSalesForce()
#   #   retorno=agendamento(pedido, data, hora)
#   # elif parametro == 'consulta':
#   #   loginSalesForce()
#   #   retorno=consultaAgenda(pedido)

#   jsonCap = r'C:\00Producao\03PAVCRVTahto\SalesForce\00Dev\Captcha.json'
#   fileObj = Path(jsonCap)
#   if fileObj.is_file():
#     os.remove('Captcha.json')
  
#   fotoCap = r'C:\00Producao\03PAVCRVTahto\SalesForce\00Dev\Captcha.png'
#   fileObj = Path(fotoCap)
#   if fileObj.is_file():
#     os.remove('Captcha.png')

#   # time.sleep(3)
#   # loginsiebel = pyautogui.locateOnScreen('loginsiebel.png')
#   # if loginsiebel != None:
#   #   for id in ids:
#   #     msg='Siebel 6 iniciado com sucesso - Máquina '+pa+' 👍🏻'
#   #     teleg.send_msg(id, msg) 
#   # else:
#   #   for id in ids:
#   #     msg='Siebel 6 pode nao ter sido iniciado - checar máquina '+pa
#   #     teleg.send_msg(id, msg)

# if __name__ == "__main__":
#   Main()