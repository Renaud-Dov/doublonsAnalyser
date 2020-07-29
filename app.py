#!/usr/bin/env python3
import random
import sys
import threading
import os
import json
from time import sleep
import tkinter as tk
from tkinter import messagebox,filedialog
from tkinter.ttk import Progressbar,Notebook
from subprocess import check_call
from hashlib import md5
from PIL import Image, ImageTk


verrou = threading.Lock()
filesList={}

root=tk.Tk()
root.configure(bg='#809c7c')#'#963592''#809c7c'
root.title('Analyseur de doublons')
root.geometry('1920x1080')

canvas=tk.Canvas(root,bd=0,bg='#809c7c',highlightthickness=0)
Frame1=tk.Frame(root,bg='#809c7c')

imgList=[0]*20

frame=[tk.Frame(Frame1)]*10
listeDoublon=[]
nDoublons=int()
def showExplorer(path):
    if sys.platform == 'darwin':
        check_call(['open', '--', path])
    elif sys.platform == 'linux':
        check_call(['nautilus', '--', path])
    elif sys.platform == 'linux2':
        check_call(['xdg-open', '--', path])
    elif sys.platform == 'win32':
        check_call(['explorer', path])

def resultat(path,list):
    global listeDoublon
    listeDoublon[0].remove(path)
    for i in listeDoublon[0]:
        os.rename(i,os.path.dirname(i)+'/RENAME_'+os.path.basename(i))
    del listeDoublon[0]
    ADD_bar_progress()
    affichage()
#####################################
def format_bytes(path):
    size=os.path.getsize(path)
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G'}
    while size > power:
        size /= power
        n += 1
    return str(round(size,1))+' '+power_labels[n]+'B'
def ValueScrool(event):
    scroll.yview("scroll",event.delta,"units")
    print('event=',event)
#####################################
def Afficher(num,path):
    global imgList,frame

    imgList[num]=Image.open(path)
    width, height = imgList[num].size
    w=width
    h=height
    if width>=800:
        width=600
        height=400
    elif height>=800:
        width=600
        height=400

    imgList[num]=ImageTk.PhotoImage(imgList[num].resize((width, height)))

    tk.Label(frame[num],text=path,bg='white').pack()
    imgLabel=tk.Label(frame[num],image=imgList[num],cursor="hand1")
    imgLabel.pack()

    tk.Label(frame[num],text='{}, {}x{}'.format(format_bytes(path),w,h),bg='white').pack()
    imgLabel.bind("<Button-1>",lambda e:resultat(path,listeDoublon[0]))
    imgLabel.bind("<Button-3>",lambda e:showExplorer(path))
def next_element():
    global listeDoublon
    listeDoublon.append(listeDoublon[0])
    del listeDoublon[0]
    affichage()
def affichage():
    global listeDoublon,frame,imgList
    for i in frame:
        i.destroy()
    frame=[]
    # imgList=[]
    if len(listeDoublon)!=0:
        nbLabel.configure(text='Il y a {} images doublons'.format(len(listeDoublon[0])))
        for num in range(len(listeDoublon[0])):
            frame.append(tk.Frame(Frame1,relief='raised',bd=2,bg='white'))
            if num>=6:row=3
            elif num>=4:row=2
            elif num>=2:row=1
            else:row=0
            # print(num,listeDoublon[0][num],"row=",num%2,"column=",num)

            frame[num].grid(row=row,column=num%2,ipady=5,ipadx=5,padx=5,pady=5)
            Afficher(num,listeDoublon[0][num])
        canvas.update()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto('0')
    else:
        messagebox.showinfo('Terminé','Il ne reste plus aucun doublon')
        jsonWrite('doublons2.json',listeDoublon)
        quit()

def quitter():
    a=messagebox.askyesnocancel('Quitter','Voulez vous sauvegarder la base de données avant de fermer ?')
    if a==True:
        jsonWrite('doublons.json',listeDoublon)
        quit()
    elif a==False:
        quit()

def jsonWrite(path,data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)
def jsonRead(path):
    with open(path, 'r') as outfile:
        return json.load(outfile)


class limit(int):
    def __init__(self, limite=10):
        self._limite=limite

    def get_limite(self):
        return self._limite
    def inc(self):
        self._limite+=1
    def dec(self):
        self._limite-=1

limite=limit(16)

class ShowImage(threading.Thread):

    def __init__(self, path):
        threading.Thread.__init__(self)
        self.path = path

    def run(self):
        self.img=Image.open(self.path)

        width, height = self.img.size
        # print(width,height)
        if width>=600:
            width=375
            height=225
        elif height>=400:
            width=100
            height=200

        # return ImageTk.PhotoImage(img.resize((width, height),Image.ANTIALIAS))
        self.img=ImageTk.PhotoImage(self.img.resize((width, height),Image.ANTIALIAS))
        with verrou:
            imgList.append(self.img)


class CalcMd5(threading.Thread):

    def __init__(self, path,limite):
        threading.Thread.__init__(self)
        self.path = path

    def run(self):

        self.file=md5(open(self.path,'rb').read()).hexdigest()

        with verrou:
            filesList[self.path]=self.file
            limite.inc()
class TopLevel():
    def __init__(self,main):
        self.value=''

        self.window=tk.Toplevel(main)
        self.window.geometry('500x175')
        self.window.title('Choix lecture data')
        tk.Label(self.window,text="Voulez vous scanner le disque\nou lire les métadonnées du fichier ?",font=("Calibri",20,"bold")).pack(pady=10,padx=5,anchor='n')
        frame=tk.Frame(self.window)
        frame.pack(side=tk.BOTTOM,pady=25,padx=15)

        tk.Button(self.window,command=lambda:self.modifValue('scan'),text='Scanner Disque',font=("Calibri",15,"bold"),relief='ridge',borderwidth=5,bg='white',width=12,cursor="hand1").pack(side=tk.RIGHT)
        tk.Button(self.window,command=lambda:self.modifValue('read'),text='Lire fichier',font=("Calibri",15,"bold"),relief='ridge',borderwidth=5,bg='white',width=12,cursor="hand1").pack(side=tk.RIGHT,padx=15)
    def returnValue(self):
        self.window.destroy()
        return self.value

    def modifValue(self,valeur):
        self.value=valeur

def debut():
    button.configure(state='normal',command=next_element,text='Revenir sur ces\nimages plus tard')
    quitButton.configure(height=2)
    quitButton.pack(side=tk.LEFT,padx=5)
    canvas.create_window(100,0,window=Frame1,anchor='center')
    canvas.pack(side=tk.TOP)
    # canvas.grid(row=1,column=0)
    # Frame1.pack(side=tk.TOP,ipadx=15)
    nbLabel.pack(side=tk.LEFT)
    progress["maximum"]=len(listeDoublon)
    bar_progress(0)
    bar_progressLabel.configure(text='0 groupement sur {} terminé'.format(nDoublons))
    affichage() 
#################################################################
def checkDoublon():
    global listeDoublon,nDoublons
    l=dict()

    for key, value in filesList.items(): 
        if value in l:
            l[value].append(key)
        else:
            l[value] = [key] 

    for value in l.values():
        if len(value)>=2:
            listeDoublon.append(value)
    nDoublons=len(listeDoublon)
    jsonWrite('doublons.json',listeDoublon)
    debut()
#################################################################
percent=0
def showPourcentage(nFiles,n):
    global percent
    num=round((n/nFiles)*100)
    if percent!=num:
        print('{}%'.format(num))
        bar_progress(num)
        percent=num

def listfiles(racine):

    frameCharging.pack(side=tk.BOTTOM,fill=tk.X)
    # frameCharging.grid(row=2,column=0)
    files = readlist(racine) #on choisit l'emplacement
    fileError=list()
    nFiles=len(files)
    bar_progress(0)
    print("Lancement de l'analyse")
    n=0
    for f in files:
        bar_progressLabel.configure(text=f)
        while limite.get_limite()<1:
            sleep(0.01)
        limite.dec()
        # print(f)
        CalcMd5(f,limite).start()
        n+=1
        showPourcentage(nFiles,n)

    sleep(0.1)

    print('Terminé. {} éléments analysés'.format(len(filesList)))
    print("Fichiers non listés ({}): ".format(len(fileError)),fileError)

    checkDoublon()


def readlist(racine):
    
    dirfiles = [os.path.join(root, name)
                for root, dirs, files in os.walk(racine)
                for name in files
                if name.endswith((".jpg", ".jpeg",".png",".gif",".PNG",".GIF",".JPG",".JPEG"))]
    print('Il y a {} images. \nCalcul des checksum'.format(len(dirfiles)))
    return dirfiles

#####################################
def readData(racine):
    global listeDoublon,nDoublons
    try:
        listeDoublon=jsonRead('doublons.json')
        nDoublons=len(listeDoublon)
        print(len(listeDoublon),'éléments doublons importés')
        frameCharging.pack(side=tk.BOTTOM,fill=tk.X)
        # frameCharging.grid(row=2,column=0)
        debut()
    except FileNotFoundError:
        if messagebox.askokcancel('Erreur',"Fichier non localisé, voulez vous lancer l'analyse ?"):
            listfiles(racine)
        else:
            messagebox.showwarning('Fermeture',"Fermeture de l'application")
            quit()

##########################################################
def start():
    button.configure(state='disabled')
    racine=filedialog.askdirectory(initialdir='../')
    a=messagebox.askyesnocancel('Démarrage','OUI : Analyse du disque\nNON : Sans analyse')
    if a==True:
        listfiles(racine)
    elif a==False:
        readData(racine)
    else:
        button.configure(state='normal')

##########################################################
def bar_progress(value): #barre de chargement
        progress['value'] =value
        root.update_idletasks()
def ADD_bar_progress(): #barre de chargement
        progress['value'] +=1
        root.update_idletasks()
        bar_progressLabel.configure(text='{} groupement sur {} terminé'.format(progress['value'],nDoublons))    
##########################################################

frameButtons=tk.Frame(root,bg='#809c7c')
# frameButtons.grid(row=0,column=0,ipady=15)
frameButtons.pack(ipady=15,anchor='n')

quitButton=tk.Button(frameButtons,text='Quitter',command=quitter,relief='ridge',borderwidth=3,bg='white',font=('Calibri',14,'bold'))
button=tk.Button(frameButtons,text='Démarrer',command=start,relief='ridge',borderwidth=3,bg='white',font=('Calibri',14,'bold'),)
button.pack(side=tk.LEFT)

nbLabel=tk.Label(frameButtons,bg='#809c7c',font=('Calibri',20,'bold'),fg='white')
##########################################################
scroll=tk.Scrollbar(root,command=canvas.yview,width=14)
scroll.pack(fill=tk.Y,side=tk.RIGHT)
# root.bind('<Button-4>',ValueScrool)
# root.bind('<Button-5>',ValueScrool)
canvas['yscrollcommand'] = scroll.set


frameCharging=tk.Frame(root,bg='#809c7c')
progress = Progressbar(frameCharging, orient = tk.HORIZONTAL, length = 100, mode = 'determinate',) 
progress.pack(fill=tk.X,side=tk.BOTTOM)
bar_progressLabel=tk.Label(frameCharging,bg='#809c7c',font=('Calibri',20,'bold'),fg='white')
bar_progressLabel.pack(side=tk.BOTTOM)
##########################################################



root.mainloop()