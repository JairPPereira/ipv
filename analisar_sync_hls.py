import json
import subprocess
import sys
from collections import defaultdict

# ==================================================
# CONFIGURAÇÕES
# ==================================================

URL = (
    "https://cdn.live.br1.jmvstream.com/"
    "w/LVW-15748/LVW15748_Yed7yzLuRC/playlist.m3u8"
)

TEMPO_ANALISE = 20

# ==================================================
# EXECUÇÃO DO FFPROBE
# ==================================================

def executar_ffprobe():
    comando = [
        "ffprobe",
        "-v", "error",
        "-rw_timeout", "15000000",
        "-read_intervals", f"%+{TEMPO_ANALISE}",
        "-show_streams",
        "-show_packets",
        "-show_entries",
        (
            "stream=index,codec_type,codec_name,start_time,"
            "time_base,duration,sample_rate,width,height:"
            "packet=stream_index,pts_time,dts_time,duration_time"
        ),
        "-of", "json",
        URL
    ]

    print("\nConectando à transmissão...")
    print(f"Analisando aproximadamente {TEMPO_ANALISE} segundos.\n")

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
            print("O FFprobe encontrou um erro:")
            print(resultado.stderr or "Erro sem detalhes.")
            return None

        return json.loads(resultado.stdout)

    except FileNotFoundError:
        print("ERRO: ffprobe não foi encontrado.")
        print("Instale o FFmpeg e configure o PATH do Windows.")
        return None

    except subprocess.TimeoutExpired:
        print("A análise demorou demais e foi interrompida.")
        return None

    except json.JSONDecodeError:
        print("Não foi possível interpretar os dados recebidos.")
        return None

    except Exception as erro:
        print(f"Erro inesperado: {erro}")
        return None


# ==================================================
# ANÁLISE DOS RESULTADOS
# ==================================================

def analisar(dados):
    if not dados:
        return

    streams = dados.get("streams", [])
    pacotes = dados.get("packets", [])

    if not streams:
        print("Nenhuma trilha foi identificada.")
        return

    mapa_streams = {}

    print("=" * 65)
    print("INFORMAÇÕES DAS TRILHAS")
    print("=" * 65)

    for stream in streams:
        indice = stream.get("index")
        tipo = stream.get("codec_type", "desconhecido")
        codec = stream.get("codec_name", "desconhecido")

        mapa_streams[indice] = stream

        print(f"\nÍndice: {indice}")
        print(f"Tipo: {tipo}")
        print(f"Codec: {codec}")
        print(f"Início informado: {stream.get('start_time', 'N/A')}")
        print(f"Base temporal: {stream.get('time_base', 'N/A')}")

        if tipo == "video":
            print(
                f"Resolução: {stream.get('width', '?')} x "
                f"{stream.get('height', '?')}"
            )

        if tipo == "audio":
            print(f"Frequência: {stream.get('sample_rate', 'N/A')} Hz")

    tempos = defaultdict(list)

    for pacote in pacotes:
        indice = pacote.get("stream_index")

        if indice not in mapa_streams:
            continue

        stream = mapa_streams[indice]
        tipo = stream.get("codec_type")

        if tipo not in ("audio", "video"):
            continue

        pts = pacote.get("pts_time")

        if pts is None:
            continue

        try:
            tempos[tipo].append(float(pts))
        except (TypeError, ValueError):
            continue

    print("\n" + "=" * 65)
    print("ANÁLISE DOS TIMESTAMPS")
    print("=" * 65)

    for tipo in ("video", "audio"):
        valores = tempos[tipo]

        if not valores:
            print(f"\nNão foram encontrados timestamps de {tipo}.")
            continue

        print(f"\n{tipo.upper()}")
        print(f"Pacotes analisados: {len(valores)}")
        print(f"Primeiro PTS: {valores[0]:.6f} s")
        print(f"Último PTS: {valores[-1]:.6f} s")
        print(f"Intervalo observado: {valores[-1] - valores[0]:.6f} s")

        print("Primeiros 10 timestamps:")

        for valor in valores[:10]:
            print(f"  {valor:.6f} s")

    # --------------------------------------------------
    # Comparação preliminar
    # --------------------------------------------------

    video = tempos["video"]
    audio = tempos["audio"]

    print("\n" + "=" * 65)
    print("COMPARAÇÃO PRELIMINAR")
    print("=" * 65)

    if video and audio:
        primeiro_video = video[0]
        primeiro_audio = audio[0]

        diferenca = primeiro_audio - primeiro_video

        print(f"Primeiro PTS do vídeo: {primeiro_video:.6f} s")
        print(f"Primeiro PTS do áudio: {primeiro_audio:.6f} s")
        print(f"Diferença entre os primeiros PTS: {diferenca:+.6f} s")

        print(
            "\nATENÇÃO: essa diferença isolada não comprova "
            "que o áudio esteja adiantado ou atrasado."
        )
        print(
            "Os timestamps podem ter origens diferentes, e os "
            "primeiros pacotes capturados não são necessariamente "
            "os primeiros quadros e sons que deveriam ser exibidos."
        )
    else:
        print(
            "Não foi possível comparar áudio e vídeo. "
            "Verifique se as duas trilhas foram identificadas."
        )

    print("\nAnálise concluída.")


# ==================================================
# PROGRAMA PRINCIPAL
# ==================================================

if __name__ == "__main__":
    dados = executar_ffprobe()

    if dados is not None:
        analisar(dados)