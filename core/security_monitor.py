"""
Güvenlik İzleme - Sistem güvenlik durumunu izler
"""
import psutil
import logging
import subprocess
from datetime import datetime

class SecurityMonitor:
    def __init__(self):
        self.security_log = []
        self.suspicious_activities = []
        
    def scan_security(self):
        """Güvenlik taraması yap"""
        threats = []
        
        # Şüpheli process'leri kontrol et
        process_threats = self._check_suspicious_processes()
        threats.extend(process_threats)
        
        # Ağ bağlantılarını kontrol et
        network_threats = self._check_network_connections()
        threats.extend(network_threats)
        
        # Port taraması yap
        port_threats = self._check_open_ports()
        threats.extend(port_threats)
        
        self.security_log.extend(threats)
        return threats
        
    def _check_suspicious_processes(self):
        """Şüpheli process'leri kontrol et"""
        threats = []
        suspicious_keywords = [
            'crypto', 'miner', 'bitcoin', 'ether', 'coin', 'hack',
            'keylog', 'rat', 'trojan', 'virus', 'malware', 'spyware'
        ]
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ''
                    
                    for keyword in suspicious_keywords:
                        if keyword in proc_name or keyword in proc_exe:
                            threats.append({
                                'type': 'suspicious_process',
                                'severity': 'high',
                                'message': f'Şüpheli process: {proc.info["name"]}',
                                'pid': proc.info['pid'],
                                'username': proc.info['username'],
                                'timestamp': datetime.now().isoformat()
                            })
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logging.error(f"Şüpheli process kontrol hatası: {e}")
            
        return threats
        
    def _check_network_connections(self):
        """Şüpheli ağ bağlantılarını kontrol et"""
        threats = []
        suspicious_ports = [4444, 5555, 6666, 7777, 8888, 9999, 31337]
        suspicious_ips = []
        
        try:
            for conn in psutil.net_connections():
                try:
                    if conn.status == 'ESTABLISHED' and conn.raddr:
                        # Şüpheli port kontrolü
                        if conn.raddr.port in suspicious_ports:
                            threats.append({
                                'type': 'suspicious_connection',
                                'severity': 'medium',
                                'message': f'Şüpheli port bağlantısı: {conn.raddr.port}',
                                'local_address': conn.laddr,
                                'remote_address': conn.raddr,
                                'timestamp': datetime.now().isoformat()
                            })
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logging.error(f"Ağ bağlantısı kontrol hatası: {e}")
            
        return threats
        
    def _check_open_ports(self):
        """Açık portları kontrol et"""
        threats = []
        try:
            # netstat benzeri tarama
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        port_info = parts[1]
                        if ':' in port_info:
                            port = port_info.split(':')[-1]
                            if port.isdigit() and int(port) > 1024:  # System ports dışındakiler
                                threats.append({
                                    'type': 'open_port',
                                    'severity': 'low',
                                    'message': f'Açık port: {port}',
                                    'port': port,
                                    'timestamp': datetime.now().isoformat()
                                })
                                
        except Exception as e:
            logging.error(f"Port tarama hatası: {e}")
            
        return threats
        
    def get_security_status(self):
        """Güvenlik durum raporu oluştur"""
        status = {
            'total_threats': len(self.security_log),
            'high_severity': len([t for t in self.security_log if t['severity'] == 'high']),
            'medium_severity': len([t for t in self.security_log if t['severity'] == 'medium']),
            'low_severity': len([t for t in self.security_log if t['severity'] == 'low']),
            'last_scan': datetime.now().isoformat(),
            'active_threats': [t for t in self.security_log if not t.get('resolved')]
        }
        
        return status
        
    def resolve_threat(self, threat_index):
        """Tehdidi çöz"""
        if 0 <= threat_index < len(self.security_log):
            self.security_log[threat_index]['resolved'] = True
            self.security_log[threat_index]['resolved_at'] = datetime.now().isoformat()
            return True
        return False
