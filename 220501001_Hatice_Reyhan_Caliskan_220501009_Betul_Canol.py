import csv, time, sys
import tkinter as tk
from tkinter import messagebox, simpledialog
from collections import defaultdict
import threading


class TIR:
    def __init__(self):
        self.yuk_bilgisi = {}
        self.plate = None
        self.country = None
        self.arrival = None
    
    def yuk_ekle(self, arrival, plate, ulke, ton20, ton30, yuk_miktar, maliyet):
        self.yuk_bilgisi = {
            'arrival' : arrival,
            'plate' : plate,
            'ülke': ulke,
            '20_ton_konteyner': ton20,
            '30_ton_konteyner': ton30,
            'yük_miktarı': yuk_miktar,
            'maliyet': maliyet
        }
        self.plate = plate

class Gemi:
    def __init__(self):
        self.yuk_bilgisi = []
        self.plate = None
        self.country = None
        self.arrival = None
        self.capacity = None

    def yuk_ekle(self, arrival, plate, capacity, ulke):
        yuk = {
            'arrival': arrival,
            'plate': plate,
            'yuk_miktarı': capacity,
            'ulke': ulke
        }
        self.yuk_bilgisi.append(yuk)
        self.arrival = arrival
        self.plate = plate
        self.capacity = capacity

tirler = {}
gemiler = {}

with open('olaylar.csv', newline = '', encoding = 'latin-1') as csvfile:
    tir_reader = csv.reader(csvfile)
    next(tir_reader)
    for row in tir_reader:
        arrival, plate, country, tonnage20, tonnage30, load_amount, cost = row
        tir = TIR()
        tir.yuk_ekle(
            int(arrival),
            plate,
            country,
            int(tonnage20),
            int(tonnage30),
            int(load_amount),
            int(cost)
        )
        tirler[plate] = tir

with open('gemiler.csv', newline = '', encoding = 'latin-1') as csvfile:
    gemi_reader = csv.reader(csvfile)
    next(gemi_reader)
    for row in gemi_reader:
        arrival, plate, capacity, country = row
        gemi = Gemi()
        gemi.yuk_ekle(
            int(arrival), 
            int(plate), 
            int(capacity), 
            str(country)
        )
        gemiler[plate] = gemi


class Liman:
    def __init__(self):
        self.istif_alani_kapasitesi = 750
        self.istif_alani_1 = []
        self.istif_alani_2 = []

    def start_liman_operations(self, tirler, gemiler, output_text):
        self.tirlari_indir_ve_istif_alanina_yerlestir(tirler, output_text)
        self.vinç_islemi(gemiler, output_text)

    def istif_alani_dolu_mu(self):
        istif_alani_1_toplam = sum(int(yuk['yük_miktarı']) for yuk in self.istif_alani_1)
        istif_alani_2_toplam = sum(int(yuk['yük_miktarı']) for yuk in self.istif_alani_2)
        return istif_alani_1_toplam >= self.istif_alani_kapasitesi or istif_alani_2_toplam >= self.istif_alani_kapasitesi

    def update_output_text(self, output_text, message): 
        output_text.config(state = tk.NORMAL)
        output_text.insert(tk.END, message)
        output_text.see(tk.END)
        output_text.config(state = tk.DISABLED)

    def tirlari_indir_ve_istif_alanina_yerlestir(self, tirler, output_text):
        sirali_tirler_gelis_sirasi = sorted(tirler.values(), key = lambda x: x.yuk_bilgisi['arrival'])
        sirali_tirler = sorted(sirali_tirler_gelis_sirasi, key = lambda x: int(x.plate.split('_')[-1]))

        if self.istif_alani_dolu_mu():
            output_text.insert(tk.END, "\nİstif alanları dolu, tırlar bekliyor\n.\n")
            output_text.see(tk.END)
            time.sleep(3)
            return

        for tir in sirali_tirler:
            if sum(int(x['yük_miktarı']) for x in self.istif_alani_1) < self.istif_alani_kapasitesi / 2:
                message = f"{tir.plate} yükü 1. istif alanına yerleştirildi.\n\n"
                self.istif_alani_1.append(tir.yuk_bilgisi)
                output_text.after(1000, self.update_output_text, output_text, message)
                time.sleep(0.3)
            elif sum(int(x['yük_miktarı']) for x in self.istif_alani_2) < self.istif_alani_kapasitesi / 2:
                message = f"{tir.plate} yükü 2. istif alanına yerleştirildi.\n\n"
                self.istif_alani_2.append(tir.yuk_bilgisi)
                output_text.after(1000, self.update_output_text, output_text, message)
                time.sleep(0.3)
            else:
                message = "\nİstif alanları dolu, tırlar bekliyor.\n\n"
                output_text.after(3000, self.update_output_text, output_text, message)
                time.sleep(3)
                break

    def sirali_gemileri_getir(self, gemiler):
        sirali_gemiler = sorted(gemiler.values(), key = lambda x: (x.arrival, int(x.plate)))
        return sirali_gemiler

    def vinç_islemi(self, gemiler, output_text):
        vinci_kullanilan = 0
        gemi_kapasite_yuzde = 0.95

        sirali_gemiler = self.sirali_gemileri_getir(gemiler)

        for gemi in sirali_gemiler:
            yuklenen_miktar = sum(yuk['yuk_miktarı'] for yuk in gemi.yuk_bilgisi)
            kapasite = gemi.capacity

            if yuklenen_miktar >= gemi_kapasite_yuzde * kapasite:
                message = f"{gemi.plate} limandan ayrılıyor.\n\n"
                output_text.after(1000, self.update_output_text, output_text, message)

            else:
                while not self.istif_alani_dolu_mu() and vinci_kullanilan < 20:
                    vinci_kullanilan += 1
                    message = f"{vinci_kullanilan}. vinç işlemi gerçekleştirildi.\n\n"
                    output_text.after(1000, self.update_output_text, output_text, message)
                    time.sleep(1)

                if yuklenen_miktar >= gemi_kapasite_yuzde * kapasite:
                    message = f"{gemi.plate} gemisi tamamen yüklendi.\n\n"
                    output_text.after(1000, self.update_output_text, output_text, message)
                else:
                    message = "Gemilerin kapasitesi %95 dolmadığından dolayı ayrılamadı veya yükleme yapılamadı.\n\n"
                    output_text.after(1000, self.update_output_text, output_text, message)




def liman_calistir(tirler, gemiler, output_text = None):
    liman = Liman()
    liman.start_liman_operations(tirler, gemiler, output_text)

def get_truck_info(output_text):
    plate = simpledialog.askstring("Tır Bilgisi", "Tır plakasını giriniz:")
    if plate in tirler:
        truck_info = tirler[plate].yuk_bilgisi
        output_text.config(state = tk.NORMAL)
        output_text.insert(tk.END, f"{plate} Tırına ait elde edilen son bilgiler: {truck_info}\n\n")
        output_text.config(state = tk.DISABLED)
    else:
        output_text.insert(tk.END, f"{plate} plakalı bir tır bulunamadı.\n\n")

def get_ship_info(output_text):
    plate = simpledialog.askstring("Gemi Bilgisi", "Gemi plakasını giriniz:")
    if plate in gemiler:
        ship_info = gemiler[plate].yuk_bilgisi
        output_text.config(state = tk.NORMAL)
        output_text.insert(tk.END, f"{plate} Gemisine ait elde edilen son bilgiler: {ship_info}\n\n")
        output_text.config(state = tk.DISABLED)
    else:
        output_text.insert(tk.END, f"{plate} plakalı bir gemi bulunamadı.\n\n")

def clear_output_text(output_text_widget):
    output_text_widget.config(state = tk.NORMAL)
    output_text_widget.delete(1.0, tk.END)
    output_text_widget.config(state = tk.DISABLED)

def start_program(output_text):
    thread1 = threading.Thread(target = liman_calistir, args = (tirler, gemiler), kwargs = {'output_text': output_text})
    thread1.start()

def main_menu():
    global output_text
    functions = [
        ("Start Otomation", start_program),
        ("Get Truck Info", get_truck_info),
        ("Get Ship Info", get_ship_info),
        ("Clear Output", clear_output_text),
        ("Exit", sys.exit)
    ]

#INTERFACE LOOK
    menu_window = tk.Tk()
    menu_window.title("Liman Otomasyonu")
    menu_window.geometry("800x700")
    menu_window.configure(bg = "light pink")

    button_frame = tk.Frame(menu_window, bg = "#a6a8ea")
    button_frame.pack(side = "left", fill = "both", expand = True)

    output_frame = tk.Frame(menu_window, bg = "#FFFFFF")
    output_frame.pack(side = "right", fill = "both", expand = True, padx = 10)

    output_text = tk.Text(output_frame, height = 20, width = 60, font = ("Arial", 12))
    output_text.pack(side = "right", fill = "both", expand = True)
    output_text.config(state = tk.DISABLED)

    scrollbar = tk.Scrollbar(output_frame, command = output_text.yview)
    scrollbar.pack(side = "right", fill = "y")

    output_text.config(yscrollcommand = scrollbar.set)

    for i, (function_name, function_handler) in enumerate(functions):
        button = tk.Button(button_frame, text = function_name, width = 25, height = 2,
                   command = lambda handler = function_handler: handler(output_text), bg = "light blue")
        button.pack(side = "top", pady = 10, anchor = "n")
        button.pack_configure(anchor = "center")
    
    button_frame.pack_propagate(True)
    button_frame.pack(side = "left", fill = "both", expand = True, padx = 10) 

    menu_window.mainloop()

main_menu()