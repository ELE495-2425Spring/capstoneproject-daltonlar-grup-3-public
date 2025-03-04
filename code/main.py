import RPi.GPIO as GPIO
from rtlsdr import RtlSdr
import numpy as np
import time
from datetime import datetime
import json
import os
import sys
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.patches import Wedge

class SignalFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("433 MHz Sinyal Takip Arayüzü")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")
        
        self.tracker = None
        self.tracking_thread = None
        self.is_running = False
        self.spectrum_data = np.zeros(1024)
        self.measurement_data = []

        self.setup_gui()
        
    def setup_gui(self):
        # Ana çerçeveler
        self.control_frame = tk.Frame(self.root, bg="#34495e", padx=10, pady=10)
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.graph_frame = tk.Frame(self.root, bg="#2c3e50", padx=10, pady=10)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Kontrol düğmeleri
        self.start_button = ttk.Button(self.control_frame, text="Başlat", command=self.start_tracking)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(self.control_frame, text="Durdur", command=self.stop_tracking, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.exit_button = ttk.Button(self.control_frame, text="Çıkış", command=self.exit_application)
        self.exit_button.pack(side=tk.RIGHT, padx=5)
        
        # Üst grafik çerçevesi (Sinyal spektrumu)
        self.spectrum_frame = tk.Frame(self.graph_frame, bg="#2c3e50")
        self.spectrum_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Alt grafik çerçevesi (Pusula ve RSSI seviyesi)
        self.direction_frame = tk.Frame(self.graph_frame, bg="#2c3e50")
        self.direction_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sinyal spektrumu grafiği
        self.spectrum_fig = Figure(figsize=(5, 3), dpi=100, facecolor="#2c3e50")
        self.spectrum_ax = self.spectrum_fig.add_subplot(111)
        self.spectrum_ax.set_facecolor("#34495e")
        self.spectrum_ax.set_title("Sinyal Spektrumu", color="white")
        self.spectrum_ax.set_xlabel("Frekans (MHz)", color="white")
        self.spectrum_ax.set_ylabel("Güç (dB)", color="white")
        self.spectrum_ax.tick_params(colors="white")
        self.spectrum_line, = self.spectrum_ax.plot([], [], lw=2, color="#3498db")
        
        self.spectrum_canvas = FigureCanvasTkAgg(self.spectrum_fig, self.spectrum_frame)
        self.spectrum_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Pusula ve RSSI göstergesi
        self.direction_fig = Figure(figsize=(5, 4), dpi=100, facecolor="#2c3e50")
        self.direction_ax = self.direction_fig.add_subplot(111, polar=True)
        self.direction_ax.set_facecolor("#34495e")
        self.direction_ax.set_title("Sinyal Yönü", color="white")
        self.direction_ax.set_theta_zero_location("N")
        self.direction_ax.set_theta_direction(-1)
        self.direction_ax.set_rlabel_position(0)
        self.direction_ax.set_rticks([])
        self.direction_ax.tick_params(colors="white")
        
        # Pusula noktaları
        self.direction_ax.set_xticks(np.pi/180. * np.array([0, 90, 180, 270]))
        self.direction_ax.set_xticklabels(['K', 'D', 'G', 'B'])
        
        # RSSI gösterimi için ok yerine basit bir çizgi kullanıyoruz
        theta = 0  # Başlangıç açısı
        r = 0.8    # Yarıçap
        self.arrow_line, = self.direction_ax.plot([0, theta], [0, r], 
                               color='green', linewidth=3, marker='o', 
                               markersize=10, markerfacecolor='green')
        
        # RSSI değeri metin gösterimi
        self.rssi_text = self.direction_ax.text(
            0, 0.5, "RSSI: N/A", ha='center', va='center', 
            color="white", fontweight='bold'
        )
        
        self.direction_canvas = FigureCanvasTkAgg(self.direction_fig, self.direction_frame)
        self.direction_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Durum çubuğu
        self.status_bar = tk.Label(self.root, text="Hazır", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#34495e", fg="white")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Animasyon nesneleri
        self.spectrum_ani = None
        self.direction_ani = None
    
    def init_signal_finder(self):
        try:
            self.tracker = SignalFinder()
            # Ölçüm verilerini kaydetmek için geri çağırma fonksiyonu ekle
            self.tracker.callback = self.update_data
            self.update_status("RTL-SDR başlatıldı")
            return True
        except Exception as e:
            messagebox.showerror("Hata", f"RTL-SDR başlatılamadı: {str(e)}")
            self.update_status(f"Hata: {str(e)}")
            return False
    
    def update_data(self, angle, power, spectrum=None):
        measurement = {
            'angle': angle,
            'power': power,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.measurement_data.append(measurement)
        
        # Pusula grafiğini güncelle - yeni yöntem
        if hasattr(self, 'arrow_line'):
            theta = np.deg2rad(angle)
            r = 0.8  # Sabit yarıçap
            
            # Ok çizgisini güncelle
            self.arrow_line.set_data([0, theta], [0, r])
            
            # RSSI metin göstergesini güncelle
            self.rssi_text.set_text(f"RSSI: {power:.2f} dB\nYön: {angle}°")
        
        # Spektrum verisini güncelle (eğer sağlanmışsa)
        if spectrum is not None:
            self.spectrum_data = spectrum
    
    def update_spectrum(self, frame):
        """Spektrum grafiğini güncelleme fonksiyonu"""
        if not self.is_running:
            return self.spectrum_line,
        
        # Örnek frekans aralığı (MHz)
        freq = np.linspace(431, 435, len(self.spectrum_data))
        
        self.spectrum_line.set_data(freq, self.spectrum_data)
        self.spectrum_ax.relim()
        self.spectrum_ax.autoscale_view()
        
        return self.spectrum_line,
    
    def update_direction(self, frame):
        """Yön göstergesini güncelleme fonksiyonu"""
        # Animasyon fonksiyonu - pusula grafiği zaten update_data'da güncelleniyor
        return self.arrow_line, self.rssi_text
    
    def start_animations(self):
        """Grafik animasyonlarını başlat"""
        self.spectrum_ani = animation.FuncAnimation(
            self.spectrum_fig, self.update_spectrum, interval=500, blit=True
        )
        
        self.direction_ani = animation.FuncAnimation(
            self.direction_fig, self.update_direction, interval=500, blit=True
        )
    
    def start_tracking(self):
        """Takip işlemini başlat"""
        if self.init_signal_finder():
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Grafik animasyonlarını başlat
            self.start_animations()
            
            # Takip işlemini ayrı bir iş parçacığında başlat
            self.tracking_thread = threading.Thread(target=self.tracking_loop)
            self.tracking_thread.daemon = True
            self.tracking_thread.start()
            
            self.update_status("Takip başladı")
    
    def tracking_loop(self):
        """Sürekli takip döngüsü"""
        try:
            self.tracker.iterative_tracking()
        except Exception as e:
            self.update_status(f"Takip hatası: {str(e)}")
            messagebox.showerror("Hata", f"Takip sırasında hata: {str(e)}")
            self.stop_tracking()
    
    def stop_tracking(self):
        """Takip işlemini durdur"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if self.tracker:
            try:
                # Sadece motorları durdur ama tracker'ı kapatma
                self.tracker.stop_motors()
            except Exception as e:
                print(f"Motorları durdururken hata: {str(e)}")
        
        self.update_status("Takip durduruldu")
    
    def update_status(self, message):
        """Durum çubuğunu güncelle"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def exit_application(self):
        """Uygulamadan çık"""
        if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istediğinizden emin misiniz?"):
            self.stop_tracking()
            # Eğer tracker hala aktifse, tam temizleme yap
            if self.tracker:
                try:
                    self.tracker.cleanup()
                except Exception as e:
                    print(f"Cleanup hatası: {str(e)}")
            self.root.quit()
            self.root.destroy()
            sys.exit(0)

class SignalFinder:
    def __init__(self):
        # RTL-SDR ve GPIO ayarları
        self.IN1 = 17  # Sol motor ileri
        self.IN2 = 27  # Sol motor geri
        self.IN3 = 22  # Sag motor ileri
        self.IN4 = 23  # Sag motor geri
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        
        self.sdr = RtlSdr()
        self.sdr.sample_rate = 2.4e6
        self.sdr.center_freq = 433e6
        self.sdr.gain = 8.7  # Sabit kazanc degeri

        self.measurements = []
        self.current_angle = 0  # Başlangıç açı
        
        # Takip durumu
        self.running = True
        
        # GUI callback fonksiyonu
        self.callback = None
    
    def stop_motors(self):
        GPIO.output([self.IN1, self.IN2, self.IN3, self.IN4], GPIO.LOW)

    def turn_angle1(self, angle):
        duration = abs(angle) * (5.1775 / 360)
        
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
     
        time.sleep(duration)
        self.stop_motors()
        self.current_angle = (self.current_angle + angle) % 360
        
    def turn_angle2(self, angle):
        duration = abs(angle) * (3.27 / 360)
        
        if angle > 0:  
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
        elif angle < 0:
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
        else:
            return

        time.sleep(duration)
        self.stop_motors()
        self.current_angle = (self.current_angle + angle) % 360

    def measure_signal(self, samples_count=256*1024, average_count=3):
        powers = []
        spectrum_data = np.zeros(1024)
        
        for i in range(average_count):
            samples = self.sdr.read_samples(samples_count)
            power = 10 * np.log10(np.mean(np.abs(samples) ** 2) + 1e-9)
            powers.append(power)
            
            if i == 0:  # Yalnızca ilk örneklemede spektrum hesapla
                fft_data = np.abs(np.fft.fftshift(np.fft.fft(samples[:1024])))
                spectrum_data = 10 * np.log10(fft_data + 1e-9)
            
            time.sleep(0.05)
            
        avg_power = np.mean(powers)
        
        # GUI güncellemesi için callback
        if self.callback:
            self.callback(self.current_angle, avg_power, spectrum_data)
            
        return avg_power, spectrum_data

    def scan_360_degrees(self, step_angle=15):
        max_power = float('-inf')
        best_angle = 0
        self.current_angle = 0
        
        for i in range((360 // step_angle)):
            # Takip durdurulduğunda taramadan çık
            if not hasattr(self, 'running') or not self.running:
                break
                
            self.turn_angle1(step_angle)
            time.sleep(0.5)
            power, spectrum = self.measure_signal()
            
            if power > max_power:
                max_power = power
                best_angle = self.current_angle
            
            print(f"Açı: {self.current_angle}° | RSSI: {power:.2f} dB")
            self.measurements.append({
                'angle': self.current_angle,
                'power': power,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return best_angle, max_power

    def go_to_angle(self, target_angle):
        diff = (target_angle - self.current_angle) % 360
        if diff > 180:
            diff -= 360

        start_time = time.time()
        self.turn_angle2(diff)
        end_time = time.time()
        
        turning_duration = end_time - start_time
        print(f"Dönüş işlemi {turning_duration:.2f} saniye sürdü.")

    def move_forward(self, duration=2):
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        time.sleep(duration)
        self.stop_motors()

    def calculate_duration(self, max_power):
        match True:
            case _ if max_power >= -5:
                return 0
            case _ if -7 < max_power <= -5:
                return 1.4
            case _ if -9 < max_power <= -7:
                return 2.8
            case _ if -12 < max_power <= -9:
                return 4.2
            case _ if max_power <= -12:
                return 4.2

    def iterative_tracking(self):
        self.running = True  # Takip başladı
        max_power = float('-inf')
        
        while max_power < -9 and self.running:  # Durdurma koşulunu kontrol et
            print("\n=== 360° TARAMA BAŞLIYOR ===")
            best_angle, max_power = self.scan_360_degrees(step_angle=15)
            
            # Takip durdurulduğunda işlemi durdur
            if not self.running:
                break
                
            print(f"\n EN GÜÇLÜ SİNYAL: {best_angle}° | Güçlü: {max_power:.2f} dB")
            
            print("\n Güçlü sinyale tekrar yönleniyorum...")
            self.go_to_angle(best_angle)
            time.sleep(1)
            
            # Takip durdurulduğunda işlemi durdur
            if not self.running:
                break
                
            duration = self.calculate_duration(max_power)
            print(f"\n İleri Hareket Ediyorum... (duration: {duration} saniye)")
            self.move_forward(duration=duration)
            time.sleep(1)

    def cleanup(self):
        self.running = False  # Takibi durdur
        self.stop_motors()
        GPIO.cleanup()
        self.sdr.close()

def main():
    root = tk.Tk()
    app = SignalFinderGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_application)
    root.mainloop()

if __name__ == "__main__":
    main()
