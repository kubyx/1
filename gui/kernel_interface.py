import os
import subprocess
import threading
import queue
import time
from typing import Optional, Callable, List, Tuple
import logging

# Loglama ayarı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KernelInterface:
    """
    Kernel ile etkileşimi sağlayan sınıf.
    Güvenli şekilde komut çalıştırma, süreç yönetimi ve gerçek zamanlı çıktı yakalama desteği.
    """
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.output_queue: queue.Queue = queue.Queue()
        self.error_queue: queue.Queue = queue.Queue()
        self.is_running: bool = False

    def execute_command(self, command: str, timeout: Optional[int] = None) -> Tuple[bool, str, str]:
        """
        Tek bir komutu çalıştırır ve sonucunu döndürür.
        
        Args:
            command: Çalıştırılacak komut.
            timeout: Süre sınırı (saniye).
            
        Returns:
            (başarı_durumu, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            success = (result.returncode == 0)
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            error_msg = f"Komut zaman aşımına uğradı: {command}"
            logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Komut çalıştırma hatası: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg

    def start_interactive_session(self, shell: str = "/bin/bash"):
        """
        Etkileşimli bir kabuk oturumu başlatır.
        """
        try:
            self.process = subprocess.Popen(
                [shell],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.is_running = True
            
            # stdout ve stderr'i dinlemek için thread'ler başlat
            threading.Thread(target=self._capture_output, args=(self.process.stdout, self.output_queue), daemon=True).start()
            threading.Thread(target=self._capture_output, args=(self.process.stderr, self.error_queue), daemon=True).start()
            
            logger.info(f"Etkileşimli oturum başlatıldı: {shell}")
            
        except Exception as e:
            logger.error(f"Oturum başlatma hatası: {str(e)}")
            self.is_running = False

    def _capture_output(self, stream, queue: queue.Queue):
        """
        Akışı (stdout/stderr) dinler ve kuyruğa kaydeder.
        """
        while self.is_running:
            try:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    time.sleep(0.1)
            except:
                break

    def send_command(self, command: str) -> Optional[str]:
        """
        Etkileşimli oturuma komut gönderir.
        """
        if not self.is_running or not self.process:
            logger.warning("Oturum başlatılmamış.")
            return None

        try:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
            return command
        except Exception as e:
            logger.error(f"Komut gönderme hatası: {str(e)}")
            return None

    def get_output(self) -> List[str]:
        """
        Tüm yakalanan çıktıları döndürür.
        """
        outputs = []
        while not self.output_queue.empty():
            try:
                outputs.append(self.output_queue.get_nowait())
            except queue.Empty:
                break
        return outputs

    def get_errors(self) -> List[str]:
        """
        Tüm hataları döndürür.
        """
        errors = []
        while not self.error_queue.empty():
            try:
                errors.append(self.error_queue.get_nowait())
            except queue.Empty:
                break
        return errors

    def stop_session(self):
        """
        Oturumu sonlandırır.
        """
        if self.is_running and self.process:
            self.process.terminate()
            self.process.wait()
            self.is_running = False
            logger.info("Oturum sonlandırıldı.")

    def __del__(self):
        self.stop_session()

# Örnek kullanım
if __name__ == "__main__":
    kernel = KernelInterface()
    
    # Tek komut çalıştırma
    success, stdout, stderr = kernel.execute_command("ls -la", timeout=10)
    if success:
        print("Çıktı:", stdout)
    else:
        print("Hata:", stderr)
    
    # Etkileşimli oturum
    kernel.start_interactive_session()
    kernel.send_command("echo 'Merhaba Dünya'")
    time.sleep(0.5)
    print("Çıktılar:", kernel.get_output())
    kernel.stop_session()
