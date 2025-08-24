"""
Ses Kontrolü - Sesli komut ve metin okuma
"""
import speech_recognition as sr
import pyttsx3
import threading
import logging
import queue

class VoiceControl:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.voice_commands = {
            'sistem durumu': 'system_status',
            'hata tara': 'scan_errors',
            'optimize et': 'optimize_system',
            'yedek al': 'create_backup',
            'programları göster': 'show_programs',
            'kapat': 'shutdown',
            'yardım': 'show_help'
        }
        
    def setup_voice(self):
        """Ses ayarlarını yap"""
        try:
            # TTS ayarları
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.8)
                
            # Ses tanıma ayarları
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            
            return True
            
        except Exception as e:
            logging.error(f"Ses ayarlama hatası: {e}")
            return False
            
    def speak(self, text):
        """Metni seslendir"""
        try:
            def speak_thread():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
            thread = threading.Thread(target=speak_thread)
            thread.daemon = True
            thread.start()
            
            return True
            
        except Exception as e:
            logging.error(f"Metin okuma hatası: {e}")
            return False
            
    def start_listening(self):
        """Sesli komut dinlemeyi başlat"""
        if self.is_listening:
            return False
            
        self.is_listening = True
        
        def listen_thread():
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                
                while self.is_listening:
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        command = self.recognizer.recognize_google(audio, language='tr-TR')
                        self.process_command(command.lower())
                        
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        logging.error(f"Ses tanıma hatası: {e}")
                    except Exception as e:
                        logging.error(f"Dinleme hatası: {e}")
                        
        thread = threading.Thread(target=listen_thread)
        thread.daemon = True
        thread.start()
        
        return True
        
    def stop_listening(self):
        """Sesli komut dinlemeyi durdur"""
        self.is_listening = False
        return True
        
    def process_command(self, command):
        """Sesli komutu işle"""
        logging.info(f"Sesli komut: {command}")
        
        # Komut eşleştirme
        for voice_cmd, action in self.voice_commands.items():
            if voice_cmd in command:
                self.command_queue.put({
                    'action': action,
                    'command': command,
                    'timestamp': 'now'
                })
                self.speak(f"Komut anlaşıldı: {voice_cmd}")
                return True
                
        # Eşleşme yoksa
        self.speak("Komut anlaşılamadı. Lütfen tekrar söyleyin.")
        return False
        
    def get_command(self):
        """Komut kuyruğundan komut al"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
            
    def get_available_commands(self):
        """Mevcut sesli komutları getir"""
        return list(self.voice_commands.keys())
