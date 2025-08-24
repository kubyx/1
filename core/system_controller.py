"""
Sistem Kontrol Merkezi - Tüm sistem bileşenlerini yönetir
"""
import os
import sys
import subprocess
import psutil
import json
from pathlib import Path

class SystemController:
    def __init__(self):
        self.system_commands = self.load_system_commands()
        self.running_processes = {}
        
    def load_system_commands(self):
        """Sistem komutlarını yükle"""
        try:
            with open('config/system_commands.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def execute_command(self, command_type, command_name, *args):
        """Sistem komutu çalıştır"""
        try:
            if command_type in self.system_commands:
                if command_name in self.system_commands[command_type]:
                    cmd = self.system_commands[command_type][command_name]
                    if isinstance(cmd, list):
                        cmd = cmd[0]
                    
                    # Argümanları ekle
                    full_cmd = f"{cmd} {' '.join(args)}"
                    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
                    return result
        except Exception as e:
            print(f"Komut çalıştırma hatası: {e}")
        return None
    
    def get_system_info(self):
        """Sistem bilgilerini getir"""
        info = {
            "platform": sys.platform,
            "cpu_cores": psutil.cpu_count(),
            "cpu_usage": psutil.cpu_percent(),
            "memory": dict(psutil.virtual_memory()._asdict()),
            "disks": [],
            "network": [],
            "processes": []
        }
        
        # Disk bilgileri
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info["disks"].append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            except:
                continue
        
        # Ağ bilgileri
        for interface, addrs in psutil.net_if_addrs().items():
            addresses = []
            for addr in addrs:
                addresses.append({
                    "family": addr.family.name,
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })
            info["network"].append({
                "interface": interface,
                "addresses": addresses
            })
        
        return info
    
    def manage_process(self, action, process_name=None, pid=None):
        """İşlem yönetimi"""
        try:
            if action == "list":
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    processes.append(proc.info)
                return processes
            
            elif action == "kill" and pid:
                process = psutil.Process(pid)
                process.terminate()
                return True
                
            elif action == "start" and process_name:
                subprocess.Popen(process_name, shell=True)
                return True
                
        except Exception as e:
            print(f"İşlem yönetimi hatası: {e}")
            return False
    
    def run_windows_tool(self, tool_name):
        """Windows sistem aracı çalıştır"""
        tools = {
            "taskmgr": "taskmgr.exe",
            "regedit": "regedit.exe",
            "msconfig": "msconfig.exe",
            "services": "services.msc",
            "devmgmt": "devmgmt.msc",
            "diskmgmt": "diskmgmt.msc",
            "eventvwr": "eventvwr.msc"
        }
        
        if tool_name in tools:
            subprocess.Popen(tools[tool_name], shell=True)
            return True
        return False
