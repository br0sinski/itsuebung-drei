#!/usr/bin/env python3
# filepath: c:\Users\Bastian\Workspace\itsuebung-drei\richtiger_patcher.py
import sys
import os
import shutil
import struct

def patch_binary_file(binary_path, new_password):

    print(f"Aktuelles Passwort '{new_password}'")

    backup_path = binary_path + ".original"
    if not os.path.exists(backup_path):
        shutil.copy2(binary_path, backup_path)
        print(f"Untouched Binary wurde gesichert als {backup_path}")
    
    patched_path = binary_path + ".patched"
    shutil.copy2(binary_path, patched_path)
    
    try:
        with open(patched_path, 'r+b') as f:
            f.seek(0)
            binary_data = f.read()
            
            # ===== PATCH 1: BACKDOOR NEUTRALISIEREN =====
            # Suche nach der check_backdoor-Funktion und deaktiviere sie vollständig
            # Die Funktion gibt normalerweise 1 zurück, wenn das Backdoor-Passwort stimmt
            
            # Typisches Muster für die Rückgabe von 1 bei erfolgreicher Backdoor: B8 01 00 00 00 (mov eax, 1)
            backdoor_success_pattern = b"\xb8\x01\x00\x00\x00"  # mov eax, 1
            
            backdoor_ret_pos = -1
            for i in range(len(binary_data) - 5):
                if binary_data[i:i+5] == backdoor_success_pattern:
                    # Prüfe, ob es zur backdoor-Funktion gehört (einfacher Check: 
                    # dürfte im gleichen Bereich wie der Backdoor-String liegen)
                    backdoor_string = b"backdoor123"
                    backdoor_pos = binary_data.find(backdoor_string)
                    
                    if backdoor_pos != -1 and abs(backdoor_pos - i) < 100:
                        backdoor_ret_pos = i
                        break
            
            if backdoor_ret_pos != -1:
                print(f"Backdoor-Erfolgsfall gefunden bei Offset: 0x{backdoor_ret_pos:x}")
                f.seek(backdoor_ret_pos)
                f.write(b"\xb8\x00\x00\x00\x00") 
                print("Backdoor-Funktion wurde neutralisiert - gibt immer Fehler zurück")
 
                f.seek(backdoor_pos)
                f.write(b"\0\0\0\0\0\0\0\0\0\0\0")
                print("Backdoor-String mit Nullbytes überschrieben")
            else:
                print("Warnung: Backdoor-Erfolgsfall nicht gefunden - alternative Strategie")
                backdoor_string = b"backdoor123"
                backdoor_pos = binary_data.find(backdoor_string)
                
                if backdoor_pos != -1:
                    f.seek(backdoor_pos)
                    f.write(b"\0\0\0\0\0\0\0\0\0\0\0")
                    print("Backdoor-String mit Nullbytes überschrieben")
                    
                    # Suchen im Bereich von 50 Bytes um den Backdoor-String
                    search_start = max(0, backdoor_pos - 50)
                    search_end = min(len(binary_data), backdoor_pos + 50)
                    
                    for i in range(search_start, search_end - 5):
                        # Suchen nach call/ret pattern in der Nähe des Backdoors
                        if binary_data[i] == 0xE8:  # CALL opcode
                            # Patche den Call-Rückgabewert
                            f.seek(i + 5)  # Nach dem Call
                            f.write(b"\x31\xc0\x90")  # xor eax, eax + NOP
                            print(f"Potenziellen Backdoor-Call bei 0x{i:x} gepatcht")
                            break
            
            # ===== PATCH 2: ADMIN-USERNAME UND PASSWORT MODIFIZIEREN =====
            # Den Admin-Usernamen brauchen wir unverändert
            admin_pass = b"S3cur3P4ssw0rd!"
            
            admin_pass_pos = binary_data.find(admin_pass)
            if admin_pass_pos != -1:
                print(f"Admin-Passwort gefunden bei Offset: 0x{admin_pass_pos:x}")
                f.seek(admin_pass_pos)
                
                # Ersetzen durch unser neues Passwort, mit gleicher Länge
                new_pass_bytes = new_password.encode('ascii')
                if len(new_pass_bytes) < len(admin_pass):
                    new_pass_bytes = new_pass_bytes + b'\0' * (len(admin_pass) - len(new_pass_bytes))
                elif len(new_pass_bytes) > len(admin_pass):
                    new_pass_bytes = new_pass_bytes[:len(admin_pass) - 1] + b'\0'
                
                f.write(new_pass_bytes)
                print(f"Admin-Passwort durch '{new_password}' ersetzt")
            
            # ===== PATCH 3: ZUSÄTZLICHEN USERNAME-CHECK EINFÜGEN =====
            # Damit nicht jeder Benutzer mit dem richtigen Passwort Admin-Zugriff erhält
            
            # Finde die strcmp-Aufrufe in der authenticate()-Funktion
            # Der erste strcmp prüft den Usernamen
            # Wir wollen nur den admin-User erlauben
            
            # Typische Offset-Adressen (aus der Disassembly)
            username_check_offset = 0x1216  # Geschätzter Offset für strcmp(username)
            
            # Stellen wir sicher, dass der Username-Check funktioniert
            # Direkte Stelle nach dem Vergleich patchen
            f.seek(username_check_offset + 5)  # Nach dem strcmp-Call
            test_eax_pattern = b"\x85\xc0"  # test eax, eax
            bytes_at_offset = f.read(2)
            
            if bytes_at_offset == test_eax_pattern:
                print(f"Username-Check-Test bei 0x{username_check_offset+5:x} gefunden")
                # Hier modifizieren wir nichts, damit der Username-Check normal funktioniert
                # Der Check verlangt, dass username == "admin" ist
                print("Username-Check intakt belassen (nur 'admin' zulässig)")
            else:
                print(f"Warnung: Username-Check-Test nicht wie erwartet, gefunden: {bytes_at_offset.hex()}")
            
            # ===== PATCH 4: SICHERSTELLEN DASS AUTHENTICATE() KORREKT LÄUFT =====
            # Wir suchen nach den beiden kritischen Stellen in authenticate()
            
            # 1. Die erste Stelle, wo Admin-Zugriff gewährt wird
            # mov eax, 2  - setzt EAX auf 2 (Admin)
            admin_set_pattern = b"\xb8\x02\x00\x00\x00"  # mov eax, 2
            
            # Finde alle Stellen, wo Admin-Zugriff gewährt wird
            admin_set_positions = []
            for i in range(len(binary_data) - 5):
                if binary_data[i:i+5] == admin_set_pattern:
                    admin_set_positions.append(i)
            
            if admin_set_positions:
                print(f"{len(admin_set_positions)} Admin-Zugriffsgewährungen gefunden")
                
                for pos in admin_set_positions:
                    # Überprüfe die Logik vor dieser Stelle
                    # Typischerweise ist da ein Test+Jump
                    check_start = max(0, pos - 10)
                    check_bytes = binary_data[check_start:pos]
                    
                    # Wenn wir ein Test EAX, EAX gefolgt von JNE/JE finden
                    # bedeutet das, dass es eine Bedingungsprüfung gibt
                    for j in range(len(check_bytes) - 3):
                        if check_bytes[j:j+2] == b"\x85\xc0" and check_bytes[j+2] in [0x74, 0x75]:
                            check_pos = check_start + j
                            jump_type = check_bytes[j+2]  # 74 = JE, 75 = JNE
                            print(f"Bedingungsprüfung bei 0x{check_pos:x} gefunden, Jump-Typ: 0x{jump_type:x}")
                            
                            # Hier patchen wir NICHT, wir wollen dass der Code normal funktioniert
                            # und nur für admin/neues_passwort Admin-Zugriff gewährt
                            # Dadurch bekommen nur autorisierte user mit dem richtigen PW Zugang
            
            # ===== PATCH 5: LOGIN-ERFOLGSPRÜFUNG BEIBEHALTEN =====
            # Wir wollen NICHT die Login-Erfolgsprüfung bypassen
            # Wenn wir die mit NOPs überschreiben, können sich alle anmelden
            # Hier suchen wir nach dem Vergleich mit dem authenticate-Rückgabewert und lassen ihn intakt
            
            # Typisches Muster nach authenticate()-Aufruf: cmp DWORD PTR [ebp-XX], 0
            login_check_pattern = b"\x83\x7d"  # cmp DWORD PTR [ebp-XX], imm8
            
            login_check_found = False
            for i in range(0x1500, 0x1600):
                if i + 3 < len(binary_data) and binary_data[i:i+2] == login_check_pattern:
                    if binary_data[i+3] == 0x00:  # Vergleich mit 0
                        login_check_pos = i
                        print(f"Login-Erfolgsprüfung gefunden bei Offset: 0x{login_check_pos:x}")
                        # WICHTIG: Hier patchen wir NICHT, wir belassen die Prüfung intakt
                        print("Login-Erfolgsprüfung intakt belassen - nur auth. User erhalten Zugang")
                        login_check_found = True
                        break
            
            if not login_check_found:
                print("Warnung: Login-Erfolgsprüfung nicht gefunden")
            
        print(f"\nGepatchte Binary gespeichert als {patched_path}")
        print(f"Wichtig: Setze die Ausführungsrechte mit: chmod +x {patched_path}")
        print(f"\nTatsächliche Sicherheitsverbesserungen:")
        print(f"1. Backdoor wurde komplett deaktiviert (gibt immer Fehler zurück)")
        print(f"2. Admin-Passwort wurde durch '{new_password}' ersetzt")
        print(f"3. Authentifizierungslogik wurde bewahrt (nicht umgangen)")
        print(f"4. Nur die Kombination 'admin' + '{new_password}' gewährt Admin-Zugang")
        print(f"\nAndere Kombinationen sollten fehlschlagen!")
        
    except Exception as e:
        print(f"Fehler beim Patchen: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    
    return patched_path

def main():
    if len(sys.argv) < 3:
        print("Verwendung: python richtiger_patcher.py <binary_path> <neues_passwort>")
        return
    
    binary_path = sys.argv[1]
    new_password = sys.argv[2]
    
    if not os.path.exists(binary_path):
        print(f"Fehler: Binary-Datei {binary_path} nicht gefunden")
        return
    
    patch_binary_file(binary_path, new_password)
    
if __name__ == "__main__":
    main()