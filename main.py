import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime
import shutil

# Diretórios
DATA_DIR = Path('data')
BACKUP_DIR = Path('backups')
EXPORT_DIR = Path('exports')

# Criar diretórios, se não existirem
DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

# Função para criar a tabela 'livros'
def criar_tabela():
    conexao = sqlite3.connect(DATA_DIR / 'livraria.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()

# Função para criar backup do banco de dados
def fazer_backup():
    data_backup = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_path = BACKUP_DIR / f'backup_livraria_{data_backup}.db'
    shutil.copy(DATA_DIR / 'livraria.db', backup_path)
    print(f'Backup realizado: {backup_path}')
    limpar_backups_antigos()

# Função para limpar backups antigos
def limpar_backups_antigos():
    backups = sorted(BACKUP_DIR.glob('*.db'))
    for backup in backups[:-5]:  # Mantém apenas os 5 mais recentes
        backup.unlink()
        print(f'Backup removido: {backup}')

# Função para adicionar um novo livro
def adicionar_livro(titulo, autor, ano_publicacao, preco):
    fazer_backup()
    conexao = sqlite3.connect(DATA_DIR / 'livraria.db')
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO livros (titulo, autor, ano_publicacao, preco)
        VALUES (?, ?, ?, ?)
    ''', (titulo, autor, ano_publicacao, preco))
    conexao.commit()
    conexao.close()

# Função para exibir todos os livros
def exibir_livros():
    conexao = sqlite3.connect(DATA_DIR / 'livraria.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    for livro in livros:
        print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}")
    conexao.close()

# Função para atualizar o preço de um livro
def atualizar_preco(titulo, novo_preco):
    fazer_backup()
    conexao = sqlite3.connect(DATA_DIR / 'livraria.db')
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE livros SET preco = ? WHERE titulo = ?
    ''', (novo_preco, titulo))
    conexao.commit()
    conexao.close()

# Função para remover um livro
def remover_livro(titulo):
    fazer_backup()
    conexao = sqlite3.connect(DATA_DIR / 'livraria.db')
    cursor = conexao.cursor()
    cursor.execute('''
        DELETE FROM livros WHERE titulo = ?
    ''', (titulo,))
    conexao.commit()
    conexao.close()

# Função para buscar livros por autor
def buscar_por_autor(autor):
    conexao = sqlite3.connect(DATA_DIR / 'livraria.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM livros WHERE autor = ?', (autor,))
    livros = cursor.fetchall()
    for livro in livros:
        print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}")
    conexao.close()

# Função para exportar dados para CSV
def exportar_para_csv():
    conexao = sqlite3.connect(DATA_DIR / 'livraria.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    with open(EXPORT_DIR / 'livros_exportados.csv', mode='w', newline='') as arquivo_csv:
        writer = csv.writer(arquivo_csv)
        writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        writer.writerows(livros)
    print('Dados exportados para livros_exportados.csv')
    conexao.close()

# Função para importar dados de um arquivo CSV
def importar_de_csv(caminho_csv):
    fazer_backup()
    with open(caminho_csv, mode='r') as arquivo_csv:
        reader = csv.reader(arquivo_csv)
        next(reader)  # Ignora o cabeçalho
        conexao = sqlite3.connect(DATA_DIR / 'livraria.db')
        cursor = conexao.cursor()
        for linha in reader:
            cursor.execute('''
                INSERT INTO livros (titulo, autor, ano_publicacao, preco)
                VALUES (?, ?, ?, ?)
            ''', (linha[1], linha[2], int(linha[3]), float(linha[4])))
        conexao.commit()
        conexao.close()
    print(f'Dados importados de {caminho_csv}')

# Menu principal
def menu():
    criar_tabela()
    while True:
        print("\n1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano_publicacao = int(input("Ano de publicação: "))
            preco = float(input("Preço: "))
            adicionar_livro(titulo, autor, ano_publicacao, preco)
        elif opcao == '2':
            exibir_livros()
        elif opcao == '3':
            titulo = input("Título do livro para atualizar o preço: ")
            novo_preco = float(input("Novo preço: "))
            atualizar_preco(titulo, novo_preco)
        elif opcao == '4':
            titulo = input("Título do livro para remover: ")
            remover_livro(titulo)
        elif opcao == '5':
            autor = input("Autor para buscar: ")
            buscar_por_autor(autor)
        elif opcao == '6':
            exportar_para_csv()
        elif opcao == '7':
            caminho_csv = input("Caminho do arquivo CSV para importar: ")
            importar_de_csv(caminho_csv)
        elif opcao == '8':
            fazer_backup()
        elif opcao == '9':
            break
        else:
            print("Opção inválida!")

# Executar o menu
menu()
