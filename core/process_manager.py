"""
İşlem Yönetimi - Sistem process'lerini yönetir
"""
import psutil
import subprocess
import logging
from datetime import datetime

class ProcessManager:
    def __init__(self):
        self.process_cache = {}
        self.process_history = []
        
    def get_running_processes(self, detailed=False):
        """Çalışan process'leri getir"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'status', 'create_time', 'username']):
                try:
                    process_info = proc.info
                    if detailed:
                        process_info.update({
                            'exe': proc.exe(),
                            'cwd': proc.cwd(),
                            'cmdline': proc.cmdline(),
                            'num_threads': proc.num_threads(),
                            'io_counters': proc.io_counters()._asdict() if proc.io_counters() else None
                        })
                    
                    processes.append(process_info)
                    self.process_cache[proc.info['pid']] = process_info
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logging.error(f"Process listeleme hatası: {e}")
            
        return processes
    
    def get_process_details(self, pid):
        """Belirli bir process'in detaylarını getir"""
        try:
            if pid in self.process_cache:
                return self.process_cache[pid]
                
            proc = psutil.Process(pid)
            details = {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'create_time': datetime.fromtimestamp(proc.create_time()),
                'exe': proc.exe(),
                'cwd': proc.cwd(),
                'cmdline': proc.cmdline(),
                'num_threads': proc.num_threads(),
                'username': proc.username(),
                'io_counters': proc.io_counters()._asdict() if proc.io_counters() else None,
                'connections': [conn._asdict() for conn in proc.connections()] if proc.connections() else []
            }
            
            self.process_cache[pid] = details
            return details
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Process detay hatası: {e}")
            return None
    
    def terminate_process(self, pid):
        """Process'i sonlandır"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            
            self.process_history.append({
                'action': 'terminate',
                'pid': pid,
                'name': proc.name(),
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
            
            logging.info(f"Process sonlandırıldı: {pid} - {proc.name()}")
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Process sonlandırma hatası: {e}")
            
            self.process_history.append({
                'action': 'terminate',
                'pid': pid,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })
            
            return False
    
    def kill_process(self, pid):
        """Process'i zorla sonlandır"""
        try:
            proc = psutil.Process(pid)
            proc.kill()
            
            self.process_history.append({
                'action': 'kill',
                'pid': pid,
                'name': proc.name(),
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
            
            logging.info(f"Process kill edildi: {pid} - {proc.name()}")
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Process kill hatası: {e}")
            
            self.process_history.append({
                'action': 'kill',
                'pid': pid,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })
            
            return False
    
    def start_process(self, command, args=None):
        """Yeni process başlat"""
        try:
            if args:
                full_command = [command] + args
                process = subprocess.Popen(full_command)
            else:
                process = subprocess.Popen(command, shell=True)
            
            self.process_history.append({
                'action': 'start',
                'command': command,
                'args': args,
                'pid': process.pid,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
            
            logging.info(f"Process başlatıldı: {command} - PID: {process.pid}")
            return process.pid
            
        except Exception as e:
            logging.error(f"Process başlatma hatası: {e}")
            
            self.process_history.append({
                'action': 'start',
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            })
            
            return None
    
    def get_process_tree(self):
        """Process tree yapısını getir"""
        tree = {}
        try:
            for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                try:
                    pid = proc.info['pid']
                    ppid = proc.info['ppid']
                    name = proc.info['name']
                    
                    if ppid not in tree:
                        tree[ppid] = []
                    tree[ppid].append({'pid': pid, 'name': name})
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logging.error(f"Process tree hatası: {e}")
            
        return tree
    
    def get_resource_usage(self):
        """Process kaynak kullanım istatistiklerini getir"""
        stats = {
            'top_cpu': [],
            'top_memory': [],
            'total_processes': 0,
            'zombie_processes': 0
        }
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        stats['zombie_processes'] += 1
                except:
                    continue
            
            stats['total_processes'] = len(processes)
            
            # CPU kullanımına göre sırala
            stats['top_cpu'] = sorted(
                [p for p in processes if p['cpu_percent'] is not None],
                key=lambda x: x['cpu_percent'],
                reverse=True
            )[:10]
            
            # Memory kullanımına göre sırala
            stats['top_memory'] = sorted(
                [p for p in processes if p['memory_percent'] is not None],
                key=lambda x: x['memory_percent'],
                reverse=True
            )[:10]
            
        except Exception as e:
            logging.error(f"Kaynak kullanım istatistiği hatası: {e}")
            
        return stats
