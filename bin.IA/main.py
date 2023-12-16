import speech_recognition as sr
import sounddevice as sd
import tempfile
import os
import httpx
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from threading import Thread


class AssistantApp(BoxLayout):
    def __init__(self, **kwargs):
        super(AssistantApp, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.label = Label(text="Comandos:")
        self.add_widget(self.label)

        self.command_entry = TextInput(multiline=False)
        self.add_widget(self.command_entry)

        self.listen_button = Button(text="Ouvir Comando")
        self.listen_button.bind(on_press=self.listen_command_thread)
        self.add_widget(self.listen_button)

        self.output_label = Label(text="Saída:")
        self.add_widget(self.output_label)

    def speak(self, text):
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
            os.system(f"espeak -w {temp_audio.name}.wav '{text}'")
            audio, _ = sd.read(f"{temp_audio.name}.wav", dtype='int16')
            sd.play(audio, samplerate=44100)
            sd.wait()
            os.remove(f"{temp_audio.name}.wav")

    def listen_command(self):
        try:
            with sr.Microphone() as source:
                print('Escutando...')
                voz = audio.listen(source)
                comando = audio.recognize_google(voz, language='pt-BR')
                return comando.lower()

        except sr.UnknownValueError:
            self.speak("Não entendi o comando.")
            return None

        except sr.RequestError as e:
            self.speak(f"Erro no reconhecimento de fala: {e}")
            return None

    def get_news(self, api_key):
        base_url = 'https://newsapi.org/v2/top-headlines'
        country = 'br'

        params = {'country': country, 'apiKey': api_key}

        try:
            with httpx.Client() as client:
                response = client.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()

            if response.status_code == 200:
                articles = data['articles'][:5]
                news_text = "Últimas notícias: "
                for article in articles:
                    title = article['title']
                    news_text += f"{title}. "

                return news_text
            else:
                return "Não foi possível obter notícias."

        except httpx.HTTPError as e:
            return f"Erro na chamada da API: {e}"

        except Exception as e:
            return f"Erro desconhecido: {e}"

    def listen_command_thread(self, instance):
        Thread(target=self.listen_and_process_command).start()

    def listen_and_process_command(self):
        comando = self.listen_command()
        self.output_label.text = f"Comando reconhecido: {comando}"

        if comando == "abra o navegador":
            self.speak("Abrindo o navegador.")
            # Adicione o código para abrir o navegador aqui
        elif comando == "pesquise por algo":
            self.speak("O que você gostaria de pesquisar?")
            pesquisa = self.listen_command()
            self.speak(f"Pesquisando por {pesquisa}.")
            # Adicione o código para realizar a pesquisa aqui
        elif "clima" in comando:
            self.speak("Desculpe, mas não tenho informações sobre o clima no momento.")
        elif comando == "execute o comando":
            self.speak("Qual comando você gostaria de executar?")
            comando_executar = self.listen_command()
            os.system(comando_executar)
            self.speak("Comando executado.")
        elif comando == "controle as luzes":
            self.speak("Você gostaria de ligar ou desligar as luzes?")
            controle_luzes = self.listen_command()
            if "ligar" in controle_luzes:
                self.speak("Ligando as luzes.")
                # Adicione o código para ligar as luzes aqui
            elif "desligar" in controle_luzes:
                self.speak("Desligando as luzes.")
                # Adicione o código para desligar as luzes aqui
            else:
                self.speak("Comando não reconhecido.")
        elif comando == "leia as notícias":
            api_key = 'f7649d1e20104773b16b0dadb199cbad'  # Substitua pela sua chave de API do News API
            noticias = self.get_news(api_key)
            self.speak(noticias)
        else:
            self.speak("Comando não reconhecido.")


class AssistantAppApp(App):
    def build(self):
        return AssistantApp()


if __name__ == '__main__':
    audio = sr.Recognizer()
    AssistantAppApp().run()
