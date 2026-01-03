"""
Desktop Action Executor
Executes desktop commands on Windows and macOS.
"""

import subprocess
import os
import sys
import platform
from pathlib import Path
import json


class ActionExecutor:
    def __init__(self, config_path=None):
        """
        Initialize Action Executor.
        
        Args:
            config_path: Path to intents configuration file
        """
        # Load intents configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "intents.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.allowed_actions = set(self.config['allowed_actions'])
        
        # Map actions to execution methods
        self.action_map = {
            'volume_up': self._volume_up,
            'volume_down': self._volume_down,
            'mute': self._mute,
            'unmute': self._unmute,
            'brightness_up': self._brightness_up,
            'brightness_down': self._brightness_down,
            'wifi_on': self._wifi_on,
            'wifi_off': self._wifi_off,
            'bluetooth_on': self._bluetooth_on,
            'bluetooth_off': self._bluetooth_off,
            'open_settings': self._open_settings,
            'open_browser': self._open_browser,
            'open_file_explorer': self._open_file_explorer,
            'take_screenshot': self._take_screenshot,
            'open_camera': self._open_camera,
            'open_app': self._open_app,
            'get_time': self._get_time,
            'get_date': self._get_date,
            'get_battery': self._get_battery,
            'play_music': self._play_music,
            'pause_music': self._pause_music,
            'next_track': self._next_track,
            'previous_track': self._previous_track,
            'open_spotify': self._open_spotify,
            'play_spotify_music': self._play_spotify_music,
            'open_calculator': self._open_calculator,
            'open_notes': self._open_notes,
            'open_mail': self._open_mail,
            'open_terminal': self._open_terminal,
            'open_messages': self._open_messages,
            'search_google': self._search_google,
            'open_youtube': self._open_youtube,
            'lock_screen': self._lock_screen,
            'sleep_mode': self._sleep_mode,
            'restart_computer': self._restart_computer,
            'shutdown_computer': self._shutdown_computer,
            'show_desktop': self._show_desktop,
            'hide_all_windows': self._hide_all_windows,
            'open_spotlight': self._open_spotlight,
            'open_mission_control': self._open_mission_control,
            'do_not_disturb': self._do_not_disturb,
            'empty_trash': self._empty_trash,
            'get_disk_space': self._get_disk_space,
            'get_wifi_info': self._get_wifi_info,
            'open_siri': self._open_siri,
            'zoom_in': self._zoom_in,
            'zoom_out': self._zoom_out,
        }
    
    def execute(self, action, transcribed_text=None):
        """
        Execute an action.
        
        Args:
            action: Action name (e.g., 'volume_up')
            transcribed_text: Original transcribed text (for context-aware actions)
            
        Returns:
            dict: Result with 'success' and 'message' keys
        """
        if action not in self.allowed_actions:
            return {
                'success': False,
                'message': f"Action '{action}' is not allowed"
            }
        
        if action not in self.action_map:
            return {
                'success': False,
                'message': f"Action '{action}' is not implemented"
            }
        
        try:
            # Pass transcribed_text to actions that need it
            if action in ['search_google', 'open_youtube', 'play_spotify_music'] and transcribed_text:
                result = self.action_map[action](transcribed_text)
            else:
                result = self.action_map[action]()
            return {
                'success': True,
                'message': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error executing action: {str(e)}"
            }
    
    # macOS-specific implementations
    
    def _is_windows(self):
        """Check if running on Windows."""
        return platform.system() == 'Windows'
    
    def _is_macos(self):
        """Check if running on macOS."""
        return platform.system() == 'Darwin'
    
    def _run_applescript(self, script):
        """Run an AppleScript command (macOS only)."""
        if not self._is_macos():
            return False
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def _run_powershell(self, command):
        """Run a PowerShell command (Windows only)."""
        if not self._is_windows():
            return False
        try:
            result = subprocess.run(
                ['powershell', '-Command', command],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _volume_up(self):
        """Increase system volume."""
        if self._is_windows():
            # Windows: Use nircmd or PowerShell with audio COM object
            try:
                # Try using keyboard simulation via PowerShell
                ps_cmd = '''
                $wshell = New-Object -ComObject wscript.shell
                $wshell.SendKeys([char]175)
                '''
                success = self._run_powershell(ps_cmd)
                if not success:
                    # Fallback: use nircmd if available, or volume key
                    ps_cmd = '''
                    Add-Type -TypeDefinition @"
                    using System;
                    using System.Runtime.InteropServices;
                    public class Audio {
                        [DllImport("user32.dll")]
                        public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
                        public const byte VK_VOLUME_UP = 0xAF;
                        public static void VolumeUp() {
                            keybd_event(VK_VOLUME_UP, 0, 0, UIntPtr.Zero);
                            keybd_event(VK_VOLUME_UP, 0, 2, UIntPtr.Zero);
                        }
                    }
"@
                    [Audio]::VolumeUp()
                    [Audio]::VolumeUp()
                    [Audio]::VolumeUp()
                    '''
                    self._run_powershell(ps_cmd)
                return "Ses yukseltildi"
            except Exception:
                return "Ses yukseltilemedi"
        else:
            script = 'set volume output volume ((output volume of (get volume settings)) + 10)'
            success = self._run_applescript(script)
            return "Ses yukseltildi" if success else "Ses yukseltilemedi"
    
    def _volume_down(self):
        """Decrease system volume."""
        if self._is_windows():
            try:
                ps_cmd = '''
                Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class Audio {
                    [DllImport("user32.dll")]
                    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
                    public const byte VK_VOLUME_DOWN = 0xAE;
                    public static void VolumeDown() {
                        keybd_event(VK_VOLUME_DOWN, 0, 0, UIntPtr.Zero);
                        keybd_event(VK_VOLUME_DOWN, 0, 2, UIntPtr.Zero);
                    }
                }
"@
                [Audio]::VolumeDown()
                [Audio]::VolumeDown()
                [Audio]::VolumeDown()
                '''
                self._run_powershell(ps_cmd)
                return "Ses azaltildi"
            except Exception:
                return "Ses azaltilamadi"
        else:
            script = 'set volume output volume ((output volume of (get volume settings)) - 10)'
            success = self._run_applescript(script)
            return "Ses azaltildi" if success else "Ses azaltilamadi"
    
    def _mute(self):
        """Mute system volume."""
        if self._is_windows():
            try:
                ps_cmd = '''
                Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class Audio {
                    [DllImport("user32.dll")]
                    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
                    public const byte VK_VOLUME_MUTE = 0xAD;
                    public static void Mute() {
                        keybd_event(VK_VOLUME_MUTE, 0, 0, UIntPtr.Zero);
                        keybd_event(VK_VOLUME_MUTE, 0, 2, UIntPtr.Zero);
                    }
                }
"@
                [Audio]::Mute()
                '''
                self._run_powershell(ps_cmd)
                return "Ses kapatildi"
            except Exception:
                return "Ses kapatilamadi"
        else:
            script = 'set volume with output muted'
            success = self._run_applescript(script)
            return "Ses kapatildi" if success else "Ses kapatilamadi"
    
    def _unmute(self):
        """Unmute system volume."""
        if self._is_windows():
            # On Windows, mute toggle works as unmute too
            return self._mute()  # Toggle mute
        else:
            script = 'set volume without output muted'
            success = self._run_applescript(script)
            return "Ses acildi" if success else "Ses acilamadi"
    
    
    def _brightness_up(self):
        """Increase screen brightness."""
        if self._is_windows():
            try:
                # Windows: Use WMI to control brightness
                ps_cmd = '''
                $brightness = (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness
                $newBrightness = [math]::Min(100, $brightness + 10)
                (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, $newBrightness)
                '''
                self._run_powershell(ps_cmd)
                return "Parlaklik artirildi"
            except Exception:
                return "Parlaklik artirilamadi"
        else:
            try:
                out = subprocess.check_output(['brightness', '-l'], text=True)
                import re
                m = re.search(r'brightness\\s*:?\\s*([0-9]*\\.?[0-9]+)', out)
                if m:
                    cur = float(m.group(1))
                    new = min(1.0, cur + 0.1)
                else:
                    new = 0.7
                subprocess.run(['brightness', str(new)], check=True)
                return f"Parlaklik artirildi ({new:.2f})"
            except (subprocess.CalledProcessError, FileNotFoundError):
                script = 'tell application "System Events" to key code 144'
                self._run_applescript(script)
                return "Parlaklik artirildi"
    
    def _brightness_down(self):
        """Decrease screen brightness."""
        if self._is_windows():
            try:
                ps_cmd = '''
                $brightness = (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness
                $newBrightness = [math]::Max(0, $brightness - 10)
                (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, $newBrightness)
                '''
                self._run_powershell(ps_cmd)
                return "Parlaklik azaltildi"
            except Exception:
                return "Parlaklik azaltilamadi"
        else:
            try:
                out = subprocess.check_output(['brightness', '-l'], text=True)
                import re
                m = re.search(r'brightness\\s*:?\\s*([0-9]*\\.?[0-9]+)', out)
                if m:
                    cur = float(m.group(1))
                    new = max(0.0, cur - 0.1)
                else:
                    new = 0.3
                subprocess.run(['brightness', str(new)], check=True)
                return f"Parlaklik azaltildi ({new:.2f})"
            except (subprocess.CalledProcessError, FileNotFoundError):
                script = 'tell application "System Events" to key code 145'
                self._run_applescript(script)
                return "Parlaklik azaltildi"
    
    def _wifi_on(self):
        """Turn WiFi on."""
        if self._is_windows():
            try:
                subprocess.run(['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'enabled'], check=True)
                return "Wi-Fi acildi"
            except Exception:
                return "Wi-Fi acilamadi"
        else:
            script = 'do shell script "networksetup -setairportpower en0 on"'
            success = self._run_applescript(script)
            return "Wi-Fi acildi" if success else "Wi-Fi acilamadi"
    
    def _wifi_off(self):
        """Turn WiFi off."""
        if self._is_windows():
            try:
                subprocess.run(['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'disabled'], check=True)
                return "Wi-Fi kapatildi"
            except Exception:
                return "Wi-Fi kapatilamadi"
        else:
            script = 'do shell script "networksetup -setairportpower en0 off"'
            success = self._run_applescript(script)
            return "Wi-Fi kapatildi" if success else "Wi-Fi kapatilamadi"
    
    def _bluetooth_on(self):
        """Turn Bluetooth on."""
        if self._is_windows():
            try:
                ps_cmd = '''
                Add-Type -AssemblyName System.Runtime.WindowsRuntime
                $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
                Function Await($WinRtTask, $ResultType) {
                    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
                    $netTask = $asTask.Invoke($null, @($WinRtTask))
                    $netTask.Wait(-1) | Out-Null
                    $netTask.Result
                }
                [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
                [Windows.Devices.Radios.RadioState,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
                Await ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
                $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
                $bluetooth = $radios | Where-Object { $_.Kind -eq 'Bluetooth' }
                Await ($bluetooth.SetStateAsync('On')) ([Windows.Devices.Radios.RadioAccessStatus])
                '''
                self._run_powershell(ps_cmd)
                return "Bluetooth acildi"
            except Exception:
                return "Bluetooth acilamadi"
        else:
            try:
                subprocess.run(['blueutil', '--power', '1'], check=True)
                return "Bluetooth acildi"
            except (subprocess.CalledProcessError, FileNotFoundError):
                return "Bluetooth acilamadi"
    
    def _bluetooth_off(self):
        """Turn Bluetooth off."""
        if self._is_windows():
            return "Bluetooth kapatma islemi Windows'ta desteklenmiyor"
        else:
            try:
                subprocess.run(['blueutil', '--power', '0'], check=True)
                return "Bluetooth kapatildi"
            except (subprocess.CalledProcessError, FileNotFoundError):
                return "Bluetooth kapatilamadi"
    
    def _open_settings(self):
        """Open System Settings/Preferences."""
        if self._is_windows():
            try:
                subprocess.Popen(['start', 'ms-settings:'], shell=True)
                return "Ayarlar acildi"
            except Exception:
                return "Ayarlar acilamadi"
        else:
            script = 'tell application "System Settings" to activate'
            success = self._run_applescript(script)
            if not success:
                script = 'tell application "System Preferences" to activate'
                success = self._run_applescript(script)
            return "Ayarlar acildi" if success else "Ayarlar acilamadi"
    
    def _open_browser(self):
        """Open default web browser."""
        if self._is_windows():
            try:
                os.startfile('https://google.com')
                return "Tarayici acildi"
            except Exception:
                return "Tarayici acilamadi"
        else:
            try:
                browsers = [
                    ('Google Chrome', 'Google Chrome'),
                    ('Safari', 'Safari'),
                    ('Firefox', 'Firefox'),
                ]
                for app_name, display_name in browsers:
                    script = f'tell application "{app_name}" to activate'
                    if self._run_applescript(script):
                        return f"{display_name} acildi"
                subprocess.run(['open', 'https://google.com'], check=True)
                return "Tarayici acildi"
            except Exception:
                return "Tarayici acilamadi"
    
    def _open_file_explorer(self):
        """Open File Explorer / Finder."""
        if self._is_windows():
            try:
                subprocess.Popen(['explorer.exe'])
                return "Dosya Gezgini acildi"
            except Exception:
                return "Dosya Gezgini acilamadi"
        else:
            script = 'tell application "Finder" to activate'
            success = self._run_applescript(script)
            return "Finder acildi" if success else "Finder acilamadi"
    
    def _take_screenshot(self):
        """Take a screenshot."""
        from datetime import datetime
        if self._is_windows():
            try:
                # Use Snipping Tool or native screenshot
                fname = Path.home() / "Desktop" / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                ps_cmd = f'''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Screen]::PrimaryScreen | Out-Null
                Add-Type -AssemblyName System.Drawing
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen
                $bitmap = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphics.CopyFromScreen($screen.Bounds.Location, [System.Drawing.Point]::Empty, $screen.Bounds.Size)
                $bitmap.Save("{str(fname)}")
                $graphics.Dispose()
                $bitmap.Dispose()
                '''
                self._run_powershell(ps_cmd)
                return f"Ekran goruntusu alindi: {str(fname)}"
            except Exception as e:
                return f"Ekran goruntusu alinamadi: {str(e)}"
        else:
            try:
                fname = Path.home() / f"Desktop/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                subprocess.run(['screencapture', str(fname)], check=True)
                return f"Ekran goruntusu alindi: {str(fname)}"
            except Exception:
                return "Ekran goruntusu alinamadi"
    
    def _open_camera(self):
        """Open Camera app."""
        if self._is_windows():
            try:
                subprocess.Popen(['start', 'microsoft.windows.camera:'], shell=True)
                return "Kamera acildi"
            except Exception:
                return "Kamera acilamadi"
        else:
            script = 'tell application "Photo Booth" to activate'
            success = self._run_applescript(script)
            if success:
                return "Kamera acildi (Photo Booth)"
            script = 'tell application "FaceTime" to activate'
            success = self._run_applescript(script)
            return "Kamera acildi (FaceTime)" if success else "Kamera acilamadi"
    
    def _open_app(self):
        """Open common applications inferred from intent keywords via `open_app` intent."""
        # Attempt to open a few known apps; if not, prompt user to open default
        try:
            # Try common apps using AppleScript first, then fallback to `open -a`
            apps = ["Google Chrome", "Visual Studio Code", "Code", "Safari", "Firefox", "Spotify"]
            for app in apps:
                script = f'tell application "{app}" to activate'
                if self._run_applescript(script):
                    return f"{app} açıldı"

            # Fallback: try `open -a` for each
            for app in apps:
                try:
                    subprocess.run(['open', '-a', app], check=True)
                    return f"{app} açıldı (open -a)"
                except Exception:
                    continue

            # Final fallback: open Finder
            subprocess.run(['open', '-a', 'Finder'])
            return "Uygulama açıldı"
        except Exception:
            return "Uygulama açılamadı"

    def _close_app(self):
        """Close common applications (tries to quit Chrome/VSCode/Spotify)."""
        try:
            apps = ["Google Chrome", "Visual Studio Code", "Spotify"]
            for app in apps:
                script = f'tell application "{app}" to quit'
                self._run_applescript(script)
            return "Uygulamalar kapatıldı"
        except Exception:
            return "Uygulamalar kapatılamadı"

    def _get_time(self):
        """Return current system time string."""
        try:
            from datetime import datetime
            now = datetime.now()
            saat = now.strftime('%H:%M')
            msg = f'Saat {saat}'
            try:
                subprocess.run(['say', msg], check=False)
            except Exception:
                pass
            return msg
        except Exception:
            return 'Saat bilgisi alınamadı'

    def _get_date(self):
        """Return current system date string."""
        try:
            from datetime import datetime
            now = datetime.now()
            tarih = now.strftime('%d %B %Y')
            # Türkçe ay isimleri
            ay_isimleri = {
                'January': 'Ocak', 'February': 'Şubat', 'March': 'Mart',
                'April': 'Nisan', 'May': 'Mayıs', 'June': 'Haziran',
                'July': 'Temmuz', 'August': 'Ağustos', 'September': 'Eylül',
                'October': 'Ekim', 'November': 'Kasım', 'December': 'Aralık'
            }
            for eng, tr in ay_isimleri.items():
                tarih = tarih.replace(eng, tr)
            msg = f'Bugün {tarih}'
            try:
                subprocess.run(['say', msg], check=False)
            except Exception:
                pass
            return msg
        except Exception:
            return 'Tarih bilgisi alınamadı'

    def _get_battery(self):
        """Return battery percentage on macOS using pmset."""
        try:
            out = subprocess.check_output(['pmset', '-g', 'batt']).decode()
            # Extract percentage
            import re
            m = re.search(r"(\d+)%", out)
            if m:
                msg = f'Pil seviyesi: {m.group(1)}%'
                try:
                    subprocess.run(['say', msg], check=False)
                except Exception:
                    pass
                return msg
            return 'Pil bilgisi alınamadı'
        except Exception:
            return 'Pil bilgisi alınamadı'

    # Music controls
    def _play_music(self):
        """Play/resume music (iTunes/Music app)."""
        script = 'tell application "Music" to play'
        success = self._run_applescript(script)
        return "Müzik çalınıyor" if success else "Müzik çalınamadı"

    def _pause_music(self):
        """Pause music."""
        script = 'tell application "Music" to pause'
        success = self._run_applescript(script)
        return "Müzik duraklatıldı" if success else "Müzik duraklatılamadı"

    def _next_track(self):
        """Skip to next track."""
        script = 'tell application "Music" to next track'
        success = self._run_applescript(script)
        return "Sonraki şarkı" if success else "Sonraki şarkıya geçilemedi"

    def _previous_track(self):
        """Go to previous track."""
        script = 'tell application "Music" to previous track'
        success = self._run_applescript(script)
        return "Önceki şarkı" if success else "Önceki şarkıya geçilemedi"

    # App launchers
    def _open_spotify(self):
        """Open Spotify."""
        script = 'tell application "Spotify" to activate'
        success = self._run_applescript(script)
        return "Spotify açıldı" if success else "Spotify açılamadı"

    def _play_spotify_music(self, transcribed_text=None):
        """Open Spotify and search for specific music genre/type."""
        try:
            import urllib.parse
            import time
            
            # First, open Spotify
            script = 'tell application "Spotify" to activate'
            self._run_applescript(script)
            time.sleep(1)  # Wait for Spotify to open
            
            # Extract music type/genre from transcribed text
            if transcribed_text:
                text_lower = transcribed_text.lower()
                # Remove common trigger words
                remove_words = ['spotify', 'spotifydan', "spotify'dan", 'müzik', 'çal', 'oynat', 
                               'bana', 'aç', 'dan', 'den', 'playlist', 'listesi']
                
                words = text_lower.split()
                query_words = [w for w in words if w not in remove_words]
                query = ' '.join(query_words).strip()
                
                if query:
                    # Use Spotify search URL
                    encoded_query = urllib.parse.quote(query)
                    spotify_url = f'spotify:search:{encoded_query}'
                    
                    # Try to open Spotify search
                    try:
                        subprocess.run(['open', spotify_url], check=True)
                        return f"Spotify'da '{query}' aranıyor ve çalınıyor"
                    except Exception:
                        # Fallback: use web search
                        web_url = f'https://open.spotify.com/search/{encoded_query}'
                        subprocess.run(['open', web_url], check=True)
                        return f"Spotify'da '{query}' aranıyor"
            
            # Fallback: just open Spotify
            return "Spotify açıldı"
        except Exception as e:
            return f"Spotify müzik çalınamadı: {str(e)}"

    def _open_calculator(self):
        """Open Calculator app."""
        if self._is_windows():
            try:
                subprocess.Popen(['calc.exe'])
                return "Hesap makinesi acildi"
            except Exception:
                return "Hesap makinesi acilamadi"
        else:
            script = 'tell application "Calculator" to activate'
            success = self._run_applescript(script)
            return "Hesap makinesi acildi" if success else "Hesap makinesi acilamadi"

    def _open_notes(self):
        """Open Notes app."""
        script = 'tell application "Notes" to activate'
        success = self._run_applescript(script)
        return "Notlar açıldı" if success else "Notlar açılamadı"

    def _open_mail(self):
        """Open Mail app."""
        script = 'tell application "Mail" to activate'
        success = self._run_applescript(script)
        return "Mail açıldı" if success else "Mail açılamadı"

    def _open_terminal(self):
        """Open Terminal app."""
        script = 'tell application "Terminal" to activate'
        success = self._run_applescript(script)
        return "Terminal açıldı" if success else "Terminal açılamadı"

    def _open_messages(self):
        """Open Messages app."""
        script = 'tell application "Messages" to activate'
        success = self._run_applescript(script)
        return "Mesajlar açıldı" if success else "Mesajlar açılamadı"

    # Web actions
    def _search_google(self, transcribed_text=None):
        """Search on Google with extracted query."""
        try:
            import urllib.parse
            import re
            
            # Extract search query from transcribed text
            if transcribed_text:
                text_lower = transcribed_text.lower()
                
                # Try to extract query after trigger words using patterns
                patterns = [
                    r'(?:internette|google\'?da?)\s+(.+?)(?:\s+ara)?$',
                    r'(?:ara|arama\s+yap)\s+(.+?)$',
                    r'(.+?)\s+(?:ara|arama\s+yap|bul)$',
                ]
                
                query = None
                for pattern in patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        query = match.group(1).strip()
                        break
                
                # If no pattern matched, remove only trigger words at start/end
                if not query:
                    # Remove trigger words only if they're at the beginning or end
                    query = text_lower
                    start_words = ['google', 'googleda', "google'da", 'internette', 'arama yap', 'ara', 'bul']
                    for word in start_words:
                        if query.startswith(word + ' '):
                            query = query[len(word)+1:]
                        if query.endswith(' ' + word):
                            query = query[:-len(word)-1]
                    
                    # Clean up "ara" only if it's the last word
                    if query.endswith(' ara'):
                        query = query[:-4]
                    
                    query = query.strip()
                
                if query and len(query) > 2:
                    # URL encode the query
                    encoded_query = urllib.parse.quote(query)
                    url = f'https://www.google.com/search?q={encoded_query}'
                    subprocess.run(['open', url], check=True)
                    return f"Google'da '{query}' aranıyor"
            
            # Fallback: just open Google
            subprocess.run(['open', 'https://www.google.com'], check=True)
            return "Google açıldı"
        except Exception as e:
            return f"Google açılamadı: {str(e)}"

    def _open_youtube(self, transcribed_text=None):
        """Open YouTube with optional search query."""
        try:
            import urllib.parse
            import re
            
            # Extract search query from transcribed text
            if transcribed_text:
                text_lower = transcribed_text.lower()
                
                # Try to extract query after trigger words using patterns
                patterns = [
                    r'(?:youtube\'?da?|videoda)\s+(.+?)(?:\s+(?:ara|izle))?$',
                    r'(?:ara|izle)\s+(.+?)$',
                    r'(.+?)\s+(?:ara|izle|video)$',
                ]
                
                query = None
                for pattern in patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        query = match.group(1).strip()
                        break
                
                # If no pattern matched, remove only trigger words at start/end
                if not query:
                    query = text_lower
                    start_words = ['youtube', 'youtubeda', "youtube'da", 'video', 'ara', 'izle']
                    for word in start_words:
                        if query.startswith(word + ' '):
                            query = query[len(word)+1:]
                        if query.endswith(' ' + word):
                            query = query[:-len(word)-1]
                    
                    # Clean up trailing words
                    for end_word in ['ara', 'izle', 'video']:
                        if query.endswith(' ' + end_word):
                            query = query[:-len(end_word)-1]
                    
                    query = query.strip()
                
                if query and len(query) > 2:
                    # URL encode the query
                    encoded_query = urllib.parse.quote(query)
                    url = f'https://www.youtube.com/results?search_query={encoded_query}'
                    subprocess.run(['open', url], check=True)
                    return f"YouTube'da '{query}' aranıyor"
            
            # Fallback: just open YouTube
            subprocess.run(['open', 'https://www.youtube.com'], check=True)
            return "YouTube açıldı"
        except Exception as e:
            return f"YouTube açılamadı: {str(e)}"

    # System actions
    def _lock_screen(self):
        """Lock the screen."""
        script = 'tell application "System Events" to keystroke "q" using {command down, control down}'
        success = self._run_applescript(script)
        return "Ekran kilitlendi" if success else "Ekran kilitlenemedi"

    def _sleep_mode(self):
        """Put computer to sleep."""
        script = 'tell application "System Events" to sleep'
        success = self._run_applescript(script)
        return "Uyku moduna geçiliyor" if success else "Uyku moduna geçilemedi"

    def _restart_computer(self):
        """Restart the computer (with confirmation)."""
        script = 'tell application "System Events" to restart'
        success = self._run_applescript(script)
        return "Bilgisayar yeniden başlatılıyor" if success else "Yeniden başlatılamadı"

    def _shutdown_computer(self):
        """Shutdown the computer (with confirmation)."""
        script = 'tell application "System Events" to shut down'
        success = self._run_applescript(script)
        return "Bilgisayar kapatılıyor" if success else "Kapatılamadı"

    # Desktop management
    def _show_desktop(self):
        """Show desktop (minimize all windows)."""
        script = 'tell application "System Events" to keystroke "F11" using {command down}'
        success = self._run_applescript(script)
        return "Masaüstü gösteriliyor" if success else "Masaüstü gösterilemedi"

    def _hide_all_windows(self):
        """Hide all windows."""
        script = 'tell application "System Events" to keystroke "h" using {command down, option down}'
        success = self._run_applescript(script)
        return "Tüm pencereler gizlendi" if success else "Pencereler gizlenemedi"

    def _open_spotlight(self):
        """Open Spotlight search."""
        script = 'tell application "System Events" to keystroke " " using command down'
        success = self._run_applescript(script)
        return "Spotlight açıldı" if success else "Spotlight açılamadı"

    def _open_mission_control(self):
        """Open Mission Control."""
        script = 'tell application "System Events" to keystroke "" using {control down, arrow up}'
        success = self._run_applescript(script)
        return "Mission Control açıldı" if success else "Mission Control açılamadı"

    def _do_not_disturb(self):
        """Toggle Do Not Disturb mode."""
        script = '''tell application "System Events"
            tell process "ControlCenter"
                click menu bar item "Control Center" of menu bar 1
                delay 0.5
                click checkbox "Do Not Disturb" of group 1 of window "Control Center"
            end tell
        end tell'''
        success = self._run_applescript(script)
        return "Rahatsız Etmeyin modu değiştirildi" if success else "Mod değiştirilemedi"

    def _empty_trash(self):
        """Empty the Trash."""
        script = 'tell application "Finder" to empty trash'
        success = self._run_applescript(script)
        return "Çöp kutusu boşaltıldı" if success else "Çöp kutusu boşaltılamadı"

    # System info
    def _get_disk_space(self):
        """Get available disk space."""
        try:
            out = subprocess.check_output(['df', '-h', '/']).decode()
            lines = out.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    total = parts[1]
                    available = parts[3]
                    msg = f'Toplam: {total}, Boş: {available}'
                    return msg
            return 'Disk bilgisi alınamadı'
        except Exception:
            return 'Disk bilgisi alınamadı'

    def _get_wifi_info(self):
        """Get WiFi connection info."""
        try:
            out = subprocess.check_output(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I']).decode()
            import re
            ssid = re.search(r'\sSSID: (.+)', out)
            if ssid:
                msg = f'Bağlı ağ: {ssid.group(1)}'
                return msg
            return 'WiFi bağlı değil'
        except Exception:
            return 'WiFi bilgisi alınamadı'

    def _open_siri(self):
        """Open Siri."""
        script = 'tell application "System Events" to keystroke " " using {command down, space}'
        success = self._run_applescript(script)
        return "Siri açıldı" if success else "Siri açılamadı"

    # Accessibility
    def _zoom_in(self):
        """Zoom in (accessibility zoom)."""
        script = 'tell application "System Events" to keystroke "=" using {command down, option down}'
        success = self._run_applescript(script)
        return "Yakınlaştırıldı" if success else "Yakınlaştırılamadı"

    def _zoom_out(self):
        """Zoom out (accessibility zoom)."""
        script = 'tell application "System Events" to keystroke "-" using {command down, option down}'
        success = self._run_applescript(script)
        return "Uzaklaştırıldı" if success else "Uzaklaştırılamadı"


if __name__ == "__main__":
    # Test the executor
    print("🧪 Testing Action Executor...\n")
    
    executor = ActionExecutor()
    
    print(f"Loaded {len(executor.allowed_actions)} allowed actions:")
    for action in sorted(executor.allowed_actions):
        print(f"  - {action}")
    
    print("\n✅ Action executor is ready!")
