import json
import subprocess
from pathlib import Path

URL = (
    "https://cdn.live.br1.jmvstream.com/"
    "w/LVW-15748/LVW15748_Yed7yzLuRC/playlist.m3u8"
)

ARQUIVO = Path.home() / "Desktop" / "analise_conjunta.json"

comando = [
    "ffprobe",
    "-v", "error",
    "-rw_timeout", "20000000",
    "-read_intervals", "%+30",
    "-show_streams",
    "-show_packets",
    "-show_entries",
    (
        "stream=index,codec_type,codec_name,start_time,time_base:"
        "packet=stream_index,pts_time,dts_time,duration_time"
    ),
    "-of", "json",
    URL
]

print("Conectando à transmissão...")
print("Analisando áudio e vídeo na mesma captura.")
print("Aguarde...\n")

try:
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90
    )

    if resultado.returncode != 0:
        print("O FFprobe retornou um erro:")
        print(resultado.stderr or "Erro sem detalhes.")
    else:
        dados = json.loads(resultado.stdout)

        ARQUIVO.write_text(
            json.dumps(dados, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        print("Análise concluída!")
        print(f"Arquivo salvo em:\n{ARQUIVO}")
        print(f"\nTrilhas encontradas: {len(dados.get('streams', []))}")
        print(f"Pacotes capturados: {len(dados.get('packets', []))}")

        for trilha in dados.get("streams", []):
            print(
                f"Trilha {trilha.get('index')}: "
                f"{trilha.get('codec_type')} - "
                f"{trilha.get('codec_name')}"
            )

except FileNotFoundError:
    print("ERRO: o ffprobe não foi encontrado.")
    print("Verifique se o comando ffprobe -version funciona no CMD.")

except subprocess.TimeoutExpired:
    print("A análise ultrapassou 90 segundos e foi interrompida.")

except json.JSONDecodeError:
    print("O FFprobe não retornou um JSON válido.")

except Exception as erro:
    print(f"Erro inesperado: {erro}")