import os
import sys
import subprocess
import json


def check_nodejs_version():
    try:
        # Executa o comando 'node -v' para obter a versão do Node.js
        output = subprocess.check_output(['node', '-v'], stderr=subprocess.STDOUT, text=True)
        node_version = output.strip()  # Remove espaços em branco e quebras de linha
        print("Versão do Node.js instalada:", node_version)
        return node_version
    except FileNotFoundError:
        print("Node.js não encontrado. Certifique-se de que está instalado.")
        return None
    except subprocess.CalledProcessError as e:
        print("Erro ao verificar a versão do Node.js:", e.output)
        return None

def check_nodejs_compatibility(min_version):
    node_version = check_nodejs_version()
    if node_version:
        major_version = int(node_version.lstrip('v').split('.')[0])
        if major_version >= min_version:
            print("Versão do Node.js compatível.")
        else:
            print("Versão do Node.js ({}) é incompatível. Versão >= {} é necessária.".format(node_version, min_version))
            exit(1)
    else:
        print("Não é possível verificar a compatibilidade do Node.js. Encerrando o programa.")
        exit(1)


def check_config_file():
    if not os.path.exists('sea-config.json'):
        print("Arquivo 'sea-config.json' não encontrado no diretório.")
        criar_config_file()

def criar_config_file():
    print("Criando arquivo 'sea-config.json'...")
    config = {}
    while True:
        mainValue = input("caminho do seu arquivo.js: ")
        if mainValue != "":
            config['main'] = mainValue
            break
        else:
            print("Campo caminho arquivo.js obrigatório.")
    disable_exp_sea_warning = input("Deseja desativar o aviso experimental do SEA? (y/n) [default: y]: ")
    if(disable_exp_sea_warning == ""):
        disable_exp_sea_warning = 'y'
    config['disableExperimentalSEAWarning'] = disable_exp_sea_warning.lower() == 'y'
    while True:
        fileBlobNameValue = input("Output Filename: ")
        if fileBlobNameValue != "":
            fileBlobNameValue +=".blob"
            config['output'] = fileBlobNameValue
            break
        else:
            print("Campo Output Filename obrigatório.")

    with open('sea-config.json', 'w', encoding='utf-8') as file:
        json.dump(config, file)
    
    print("Arquivo 'sea-config.json' criado com sucesso.")


def buildExeNode(exefile):
    comando = f"node -e \"require('fs').copyFileSync(process.execPath, '{exefile}.exe')\""
    subprocess.run(comando, shell=True)

def createBlob():
    comando = "node --experimental-sea-config sea-config.json"
    subprocess.run(comando, shell=True)

def injectBlobInExe(nome_app, config_file):
    if not os.path.exists(f"{nome_app}.exe"):
        print(f"O arquivo {nome_app}.exe não foi encontrado.")
        sys.exit(1)
    with open(config_file, 'r') as file:
        json_data = json.load(file)
    blob_file = json_data["output"]
    comando = f"npx postject {nome_app}.exe NODE_SEA_BLOB {blob_file} ` --sentinel-fuse NODE_SEA_FUSE_fce680ab2cc467b6e072b8b5df1996b2"
    subprocess.run(comando, shell=True)

def main():
    if len(sys.argv) < 1:
        print("Uso: python pynodecraftexe.py nome_app")
        sys.exit(1)
    
    print("Check Compatibility")
    check_nodejs_compatibility(20)
    print("Check sea-config.json")
    check_config_file()
    fatia = slice(1,2)
    nome_app = sys.argv[fatia][0]
    print("criando Blob.")
    createBlob()
    config_file = "sea-config.json"
    with open(config_file, 'r') as f:
        config = json.load(f)
        if 'main' in config:
            main_script = config['main']
            if not os.path.exists(main_script):
                print(f"Erro: O arquivo especificado '{main_script}' não existe.")
                sys.exit(1)
        else:
            print("Erro: 'main' não encontrado em 'sea-config.json'.")
            sys.exit(1)
    print("Criando o aplicativo '{}.exe'".format(nome_app))
    buildExeNode(nome_app)
    print("Inject blob in .exe")
    injectBlobInExe(nome_app, config_file)



if __name__ == "__main__":
    main()