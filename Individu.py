## Fichier Individu.py
## Creation et suppression d'individus, gestion des interactions avec leur environnement

from Vect2D import *
from math import floor
import numpy as np
import random as rd
import Variables as Var

class individu:
    def __init__(self, choixSortie, pos, dpos, vmoy, r, canvas, color):
        self.pos = pos          # Position de chaque individu
        self.choixSortie = choixSortie
        self.dpos = dpos        # Vitesse de chaque individu
        self.r = r              # Rayon de chaque individu
        self.vmoy = vmoy        # Vitesse moyenne d'un individu
        self.canvas = canvas    # Le Canevas sur lequel on dessine
        self.color = color      # Couleur de chaque individu
        self.id = canvas.create_oval(-1 * r, -1 * r, r, r, fill = color, outline = 'black') #Représentation graphique
        self.canvas.move(self.id, pos.x, pos.y) #On le place à sa position

    def bouge(self):
        '''deplace un individu de dpos'''
        self.canvas.move(self.id, self.dpos.x, self.dpos.y)
        self.pos += self.dpos
        return

# Fonction de gestion du nombre d'individu
def init_indiv(terrain):
    supprime_indiv(terrain)
    for i in range(Var.NIndiv):
        # Afin d'éviter que des individus se retrouve a moitie dans un mur on genere sur un intervalle ou chacun d'eux est pleinement dans une case
        while 1 :
            erreur=False
            x = rd.randint(3*Var.dimCase,(Var.largeur-4)*Var.dimCase)
            y = rd.randint(3*Var.dimCase,(Var.hauteur-4)*Var.dimCase)
            for indiv in Var.LIndiv:
                if abs(indiv.pos.x-x)<=2*indiv.r and abs(indiv.pos.y-y)<=2*indiv.r:
                    erreur=True
            if Var.TCase[floor(y / Var.dimCase), floor(x / Var.dimCase)].type >= 0 and Var.TCase[floor(y / Var.dimCase),ceil(x / Var.dimCase)].type >= 0 and Var.TCase[ceil(y / Var.dimCase), floor(x / Var.dimCase)].type >= 0 and Var.TCase[ceil(y / Var.dimCase), ceil(x / Var.dimCase)].type >= 0 and erreur==False:
                break
        pose_indiv(x, y, terrain)

    return

def pose_indiv(x, y, terrain):
    '''Pose un inidividu sur le terrain en (x,y)'''
    pos = vect2D(x, y)
    dpos = vect2D(0, 0)
    if Var.choixSortie==1:
        indiv=individu(Var.choixSortie, pos, dpos, rd.uniform(Var.vminIndiv, Var.vmaxIndiv), Var.rIndiv, terrain,"blue")
        Var.LIndiv.append(indiv)
    else:
        indiv=individu(Var.choixSortie, pos, dpos, rd.uniform(Var.vminIndiv, Var.vmaxIndiv), Var.rIndiv, terrain,"red")
        Var.LIndiv.append(indiv)

    return

def supprime_indiv(terrain):
    '''supprime tous les individus du terrain'''
    for i in Var.LIndiv :
        terrain.delete(i.id)
    Var.LIndiv = []
    return

def sortir_indiv(terrain):
    '''Permet de supprimer un individu lorsqu'il a atteint la sortie'''
    if Var.LIndiv==[]:
        return
    for individu in Var.LIndiv :
        x = floor(individu.pos.x / Var.dimCase)
        y = floor(individu.pos.y / Var.dimCase)
        for s in Var.LSortie:
            if s==[x,y]:
                terrain.delete(individu.id)
                Var.LIndiv.remove(individu)
                Var.TCase[y,x].type=1
    return

# Fonction de gestion des collisions avec les murs, les bords et les autres individus
def touche_indiv(individu1, individu2):
    '''Test si deux individus se touchent'''
    return (individu1.pos - individu2.pos).norme() <= individu1.r + individu2.r +0.1

def rebond_indiv(individu1, individu2):
    '''Lorsqu'il y a collision entre deux individu, calcule les vitesses de chacun après le choc'''
    #if p_scal(individu1.dpos, individu2.dpos) < 0 : #Vérifie si les individus ne s'éloignent pas déjà
    #    return

    n = individu1.pos - individu2.pos
    n1 = projection(individu1.dpos, n)
    n2 = projection(individu2.dpos, n)

    t1 = individu1.dpos - n1
    t2 = individu2.dpos - n2
    #On conserve les composantes tangentielles et on échange les composantes normales
    individu1.dpos = (t1 + n2)
    individu2.dpos = (t2 + n1)

    return

def rebond_mur(individu):
    '''Lorsqu'un individu touche un mur, on le fait rebondir en inversant sa vitesse selon les axes de chocs'''
    pos = individu.pos
    r = individu.r
    c = Var.TCase[floor(pos.y / Var.dimCase), floor(pos.x / Var.dimCase)]
    d = Var.TCase[ceil(pos.y / Var.dimCase), ceil(pos.x / Var.dimCase)]
    murX=False
    murY=False
    if c.type == -1 :
        if pos.x -r-0.1 < c.pos.x or pos.x + r +0.1 > c.pos.x + Var.dimCase :
            individu.dpos.x *= -1
            murX=True
        if pos.y -r-0.1 < c.pos.y or pos.y + r+0.1 > c.pos.y + Var.dimCase :
            individu.dpos.y *= -1
            murY=True

    return

def rebond_bord(individu):
    '''Lorsqu'un individu touche un mur, on le fait rebondir en inversant sa vitesse selon les axes de chocs'''
    pos = individu.pos
    r = individu.r
    if pos.x -r < 0 or pos.x + r > Var.largeur*Var.dimCase:
        individu.dpos.x *= -1
    if pos.y - r < 0 or pos.y + r > Var.hauteur*Var.dimCase :
        individu.dpos.y *= -1
    return

# Programme de gestion des mouvements
def bouge_indiv():
    '''Gestion du mouvement des individus en fonction de l'environnement de chacun'''
    for i, individu1 in enumerate(Var.LIndiv) :
        x = floor(individu1.pos.x / Var.dimCase)
        y = floor(individu1.pos.y / Var.dimCase)
        individu1.dpos = individu1.dpos.normalise() * np.random.normal(individu1.vmoy, 0.2)
        individu1.dpos += Var.Tdirection[individu1.choixSortie-1][y,x]
        for individu2 in Var.LIndiv[i+1:] :
            if touche_indiv(individu1, individu2) :
                rebond_indiv(individu1, individu2)
        rebond_bord(individu1)
        rebond_mur(individu1)
        individu1.bouge()
    return

##individuCarre pour le cas où l'individu est dans une seule case à la fois

class individuCarre:
    def __init__(self, choixSortie,  pos, canvas, color):
        self.pos = pos          # Position de chaque individu
        self.choixSortie = choixSortie #Choix sortie
        self.canvas = canvas    # Le Canevas sur lequel on dessine
        self.color = color      # Couleur de chaque individ
        self.id = canvas.create_rectangle(0,0,Var.dimCase,Var.dimCase,fill = color, outline = 'black')
        self.canvas.move(self.id, pos.x, pos.y) #On le place à sa position
        self.score = Var.TCase[floor(pos.y/Var.dimCase),floor(pos.x/Var.dimCase)].score[self.choixSortie-1]

    def bouge(self):
        '''deplace un individu de dpos'''
        x,y=floor(self.pos.x/Var.dimCase),floor(self.pos.y/Var.dimCase)
        V=voisins(x,y,[pas_individu_condition,pas_mur_condition],Var.typeDiagonale)
        if len(V)==0:
            #l individu est bloqué
            return
        a,b=y,x
        dmin=Var.dMaxCase[self.choixSortie-1]
        for v in V:
            Var.TCase[v.y, v.x].explore = False
            c=Var.TCase[v.y,v.x].score[self.choixSortie-1]
            if c < dmin and c < self.score:
                dmin= c
                a,b=v.y,v.x
        dx,dy=(b-x)*Var.dimCase,(a-y)*Var.dimCase
        self.pos.y,self.pos.x=a*Var.dimCase,b*Var.dimCase
        self.canvas.move(self.id, dx,dy)
        Var.TCase[y,x].type=0
        if Var.TCase[a,b].type !=1:
            Var.TCase[a,b].type =2
        self.score = Var.TCase[y,x].score[self.choixSortie-1]
        return

# Fonction de gestion du nombre d'individu
def init_indiv_carre(terrain):
    supprime_indiv(terrain)
    for i in range(Var.NIndiv):
        # Afin d'éviter que des individus se retrouve a moitie dans un mur on genere sur un intervalle ou chacun d'eux est pleinement dans une case
        while 1 :
            x = rd.randint(0, Var.largeur-1)
            y = rd.randint(0,Var.hauteur-1)
            if Var.TCase[y, x].type ==0  :
                break
        pose_indiv_carre(x*Var.dimCase, y*Var.dimCase, terrain)
    return

def pose_indiv_carre(x, y, terrain):
    '''Pose un inidividu sur le terrain en (x,y)'''
    if Var.TCase[floor(y/Var.dimCase),floor(x/Var.dimCase)].type==2:
        return
    pos = vect2D(floor(x/Var.dimCase)*Var.dimCase,floor(y/Var.dimCase)*Var.dimCase)
    if Var.choixSortie==1:
        indiv=individuCarre(Var.choixSortie, pos, terrain, "blue")
    else:
        indiv=individuCarre(Var.choixSortie, pos, terrain, "red")
    Var.TCase[floor(y/Var.dimCase),floor(x/Var.dimCase)].type=2
    Var.LIndiv.append(indiv)
    return

# Programme de gestion des mouvements
def bouge_indiv_carre():
    '''Gestion du mouvement des individus en fonction de l'environnement de chacun'''
    for i, individu1 in enumerate(Var.LIndiv) :
        individu1.bouge()
    rd.shuffle(Var.LIndiv)
    return
