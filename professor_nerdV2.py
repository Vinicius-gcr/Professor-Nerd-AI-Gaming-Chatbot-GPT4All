from gpt4all import GPT4All
from deep_translator import GoogleTranslator, MyMemoryTranslator, LingueeTranslator, PonsTranslator
from pathlib import Path
import sys
import os


def ler_base_conhecimento(arquivo_base):
    if not os.path.exists(arquivo_base):
        print(f"Erro: arquivo de base não encontrado: {arquivo_base}")
        sys.exit(1)

    try:
        with open(arquivo_base, "r", encoding="utf-8") as ficheiro:
            conteudo = ficheiro.read()

            if not conteudo.strip():
                print("Não foi possível ler o arquivo. A base está vazia.")
                sys.exit(1)

            print("Base carregada")
            return conteudo

    except Exception as erro:
        print(f"Base não lida: {erro}")
        sys.exit(1)


Conhecimento = "base_professor_nerd.txt"
texto_da_base = ler_base_conhecimento(Conhecimento)

print("Bot iniciando")


def traducao():
    print("Modo tradução")
    while True:
        texto = input("\nDigite o texto para traduzir (Digite sair para voltar ao chat): ")

        if texto.lower() == "sair":
            print("Mudando para o chat")
            break

        idioma_destino = input("Para qual idioma você quer traduzir? Ex: english, es, fr, pt: ")

        try:
            traducao = GoogleTranslator(source="auto", target=idioma_destino).translate(texto)
            print(f"Tradução: {traducao}")

        except Exception as erro:
            print(f"Erro na tradução: {erro}")


def detectar_idioma(texto):
    texto = texto.lower()

    palavras_ingles = ["hello", "hi", "game", "recommend", "play", "thanks", "bye"]
    palavras_espanhol = ["hola", "juego", "recomienda", "quiero", "gracias", "adios", "adiós"]

    if any(palavra in texto for palavra in palavras_ingles):
        return "en"

    if any(palavra in texto for palavra in palavras_espanhol):
        return "es"

    return "pt"


def traduzir_texto(texto, origem="auto", destino="pt"):
    try:
        return GoogleTranslator(source=origem, target=destino).translate(texto)
    except Exception:
        return texto


def resposta_pronta(pergunta):
    texto = pergunta.lower().strip()

    if texto in ["oi", "olá", "ola", "opa", "eai", "fala", "hello", "hi", "hola"]:
        return "Olá! Eu sou o Professor Nerd, um chatbot sobre jogos digitais. Posso recomendar jogos, explicar gêneros e comparar títulos."

    if texto in ["ajuda", "help", "me ajuda", "o que você faz", "o que voce faz"]:
        return "Eu posso falar sobre FPS, RPG, MOBA, Battle Royale, jogos casuais, competitivos, gratuitos e pagos."

    if texto in ["tchau", "até", "ate", "bye", "adios", "adiós"]:
        return "Valeu! Até a próxima e bons jogos!"

    return None


modelo = Path("models/mistral-7b-instruct-v0.1.Q4_K_M.gguf").resolve()


def chat():
    print("                               Bem vindo ao Professor Nerd                              ")
    print("                     Chatbot sobre jogos usando LLM                     ")
    print("                     Digite 'sair' para encerrar                   ")

    nome_usuario = input("\nPor favor, digite o seu nome: ").strip()

    if not nome_usuario:
        nome_usuario = "Usuário"

    if not modelo.exists():
        print("\nModelo não encontrado.")
        print(f"Coloque o arquivo do modelo em: {modelo}")
        print("Nome esperado: mistral-7b-instruct-v0.1.Q4_K_M.gguf")
        sys.exit(1)

    try:
        Ia = GPT4All(
            model_name=modelo.name,
            model_path=str(modelo.parent),
            allow_download=False,
            device="cpu"
        )
    except Exception as erro:
        print(f"Erro na inicialização da IA: {erro}")
        sys.exit(1)

    while True:
        pergunta = input(f"\n{nome_usuario}: ")

        if pergunta.strip().lower() == "modo tradução":
            traducao()
            continue

        if pergunta.strip().lower() == "sair":
            print("Chat encerrado. Foi bom conversar com você.")
            break

        idioma_usuario = detectar_idioma(pergunta)

        pronta = resposta_pronta(pergunta)

        if pronta:
            resposta_pt = pronta
        else:
            pergunta_pt = traduzir_texto(pergunta, origem="auto", destino="pt")

            prompt_base = (
                "Você é o Professor Nerd, um chatbot temático sobre jogos digitais.\n"
                "Use as informações da base para responder.\n"
                "Responda em português do Brasil, de forma clara, simples e objetiva.\n"
                "Não escreva falas inventadas como 'Usuário:' ou 'Bot:'.\n"
                "Não continue a conversa sozinho.\n"
                "Se a pergunta fugir do tema jogos, avise educadamente e volte para jogos.\n"
                "Faça uma pergunta curta no final.\n\n"
                f"Informações da base:\n{texto_da_base[:4000]}\n\n"
            )

            prompt = f"{prompt_base}Pergunta: {pergunta_pt}\nResposta:"

            try:
                resposta_pt = Ia.generate(
                    prompt=prompt,
                    max_tokens=180,
                    temp=0.4,
                    top_p=0.9
                )

                for parada in ["Usuário:", "Usuario:", "Bot:", "Pergunta:", "\nVocê:"]:
                    if parada in resposta_pt:
                        resposta_pt = resposta_pt.split(parada)[0]

                resposta_pt = resposta_pt.strip()

                if not resposta_pt:
                    resposta_pt = "Não entendi muito bem. Você pode perguntar sobre FPS, RPG, Valorant, Minecraft, GTA, LoL ou Fortnite."

            except Exception as erro:
                resposta_pt = "Desculpa, tive um problema para responder. Tente perguntar de outro jeito."

        if idioma_usuario != "pt":
            resposta_final = traduzir_texto(resposta_pt, origem="pt", destino=idioma_usuario)
        else:
            resposta_final = resposta_pt

        print("Professor Nerd:", resposta_final)


chat()
