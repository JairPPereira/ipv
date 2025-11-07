import subprocess

def copiar_config_rede():
    try:
        # Executa o comando ipconfig /all e captura o resultado
        resultado = subprocess.check_output("ipconfig /all", text=True, encoding='utf-8', errors='ignore')
        
        # Salva o resultado em um arquivo de texto
        with open("config_rede.txt", "w", encoding="utf-8") as arquivo:
            arquivo.write(resultado)
        
        print("✅ As configurações foram copiadas e salvas em 'config_rede.txt'.")
        print("Envie o conteúdo desse arquivo aqui para eu gerar a configuração da rede 2.4G.")
    except Exception as e:
        print("❌ Erro ao obter as configurações:", e)

copiar_config_rede()
