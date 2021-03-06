## Fichier Moteur.py
## Gère le fonctionnement de la simulation de mouvement de foule

import numpy as np
from copy import *
from Vect2D import *
import Variables as Var
from Case import *
from Texte import *
from Ligne import *
from Individu import *

# Fonctions de modification du terrain et des cases qui agissent sur le texte et le champs vectoriel
def terrain_vierge(terrain):
    '''Cree un terrain vierge'''
    supprime_indiv(terrain)
    cacher_ligne()
    cacher_texte()
    Var.LSortie = []
    Var.LSortie1= []
    Var.LSortie2= []
    for x in range(Var.largeur):
        for y in range(Var.hauteur):
            Var.TCase[y, x].type = 0
            Var.TCase[y, x].score = [inf,inf]
            Var.TCase[y, x].rafraichir()
            Var.Tdirection[0][y, x].x = 0
            Var.Tdirection[0][y, x].y = 0
            Var.Tdirection[1][y, x].x = 0
            Var.Tdirection[1][y, x].y = 0
    return

def creer_sortie(x, y):
    '''Permet de déclarer une case comme étant une sortie'''
    if not([x, y] in Var.LSortie):
        change_case_action(vect2D(x, y))
        Var.LSortie.append([x, y])
        if Var.choixSortie==1:
            Var.LSortie1.append([x, y])
        else:
            Var.LSortie2.append([x, y])

    return

def reset_case():
    '''Remarque les cases comme inexplorées, utile pour refaire un parcours des cases'''
    for x in range(Var.largeur):
        for y in range(Var.hauteur):
            Var.TCase[y, x].explore = False
    return

# Fonction de test de condition :
def pas_mur_condition(C):
    '''boleen qui renvoit vrai si la case n'est pas un mur'''
    return (Var.TCase[C.y, C.x].type != -1)

def pas_individu_condition(C):
    '''boleen qui renvoit vrai si la case n'est pas un individu'''
    return (Var.TCase[C.y, C.x].type != 2)


# Fonction qui réalisent des actions :
def change_distance_action(C):

    if Var.TCase[C.y, C.x].type==1:
            Var.TCase[C.y, C.x].score[Var.Change]=0
            d=0
    else:
        a=min(Var.TCase[C.y-1, C.x].score[Var.Change],Var.TCase[C.y+1, C.x].score[Var.Change])
        b=min(Var.TCase[C.y, C.x-1].score[Var.Change],Var.TCase[C.y, C.x+1].score[Var.Change])
        if abs(a-b)< Var.pas:
            d=round((a+b+sqrt(2*Var.pas**2-(a-b)**2))/2,1)
        else:
            d=round(Var.pas+min(a,b),1)


        '''Atribue une distance du plus court chemin à la case C en fonction de d, la nouvelle distance à une autre sortie'''
    if Var.TCase[C.y, C.x].score[Var.Change] > 0 : # cela signifie qu'on a déjà calculé la distance de cette case à une sortie
        Var.TCase[C.y, C.x].score[Var.Change] = min(d, Var.TCase[C.y, C.x].score[Var.Change]) # on selectionne la plus proche
    else :
        Var.TCase[C.y, C.x].score[Var.Change] = d

    return

def change_case_action(C):
    '''Change le type de case de la case C'''
    if(Var.TCase[C.y, C.x].type == 1) :
        if Var.choixSortie==1:
            Var.LSortie1.remove([C.x, C.y])
        else:
            Var.LSortie2.remove([C.x, C.y])
        Var.LSortie.remove([C.x, C.y])
        Var.TCase[C.y, C.x].score = [inf,inf]

    Var.TCase[C.y, C.x].type = Var.typeCase
    Var.TCase[C.y, C.x].rafraichir()
    return

# Fonction de calcul du champs scalaire
# ===============================================================================================================
def voisins(x, y, Lcondition, voisins_diag):
    '''Renvoie la liste des voisins de la case (x,y) qui satisfont une liste de conditions'''
    # Si voisins_diag = False : on considère les voisins avec une frontière commune avec notre case
    # Si voisins_diag = True : on considère les voisins diagonaux en plus
    L = []
    V = [vect2D(x - 1, y), vect2D(x + 1, y), vect2D(x, y - 1), vect2D(x, y + 1)]
    if voisins_diag :
        V += [vect2D(x - 1,y - 1), vect2D(x - 1,y + 1), vect2D(x + 1,y - 1), vect2D(x + 1,y + 1)]
    for C in V : # C est un vecteur de coordonnées de la forme vect2D(x,y)
        if 0 <= C.x and C.x < Var.largeur and 0 <= C.y and C.y < Var.hauteur : # On vérifie que le voisin est dans le domaine du terrain
            if Var.TCase[C.y, C.x].explore == False : # On vérifie que la case n'a pas déjà été explorée
                flag = True
                for condition in Lcondition : # On vérifie que le voisin vérifie toutes les conditions de Lcondition
                    if not(condition(C)) :
                        flag = False
                        break
                if(flag): # Si c'est le cas, on l'ajoute à la liste des voisins disponibles vvvvv vcg
                    L.append(C)
                    Var.TCase[C.y, C.x].explore = True
    return L

def wavefront(x, y, Lcondition, Laction, maxd, voisins_diag):
    '''choisit les voisins de la case (x,y) selon Lcondition et leur applique Laction dans un rayon maxd
    *param : -> x,y coordonnées de la case de départ
             -> Lcondition une liste de condition à vérifier
             -> Laction une liste d'action à effectuer
             -> maxd la distance maximale sur lequel on va appliquer l'algorithme
             -> voisins_diag : Si voisins_diag = False : on considère les voisins avec une frontière commune avec notre case
                    Si voisins_diag = True : on considère les voisins diagonaux en plus
    '''
    L = [vect2D(x, y)]
    for d in range(maxd):
        if len(L) == 0 :
            break
        V = []
        for C in L : #Pour chaque case de L, on ajoute les voisins qui vérifient les conditions
            V += voisins(C.x, C.y, Lcondition, voisins_diag)
            for action in Laction :
                action(C)

        L = deepcopy(V)
    reset_case()
    return

def recalcule_champ_potentiel():
    '''Recalcule le champ scalaire, c'est le programme de base qui fait fonctionner notre algorithme'''
    #for x in range(Var.largeur):
    #    for y in range(Var.hauteur):
    #        Var.TCase[y, x].score = inf # On réinitialise toutes les cases à la distance par défaut -1
    Var.Change=0
    for (x, y) in Var.LSortie1 :
        wavefront(x, y, [pas_mur_condition], [change_distance_action], Var.hauteur * Var.largeur, False)
    Var.Change=1
    for (x, y) in Var.LSortie2 :
        wavefront(x, y, [pas_mur_condition], [change_distance_action], Var.hauteur * Var.largeur, False)

        # Pour chaque sortie, on effectue wavefront, c'est à dire qu'on regarde le plus court chemin de chaque case à cette sortie, et on prend le minimum
        # La distance maximum correspond ici au nombre de cases sur le plateau
    direction(1)
    direction(2)
    rafraichir()
    return
# ===============================================================================================================

def direction(sortie) :
    '''Calcule le tableau des directions à prendre'''
    if len(Var.LSortie2)==0 and sortie==2:
        return
    for x in range(Var.largeur):
        for y in range(Var.hauteur):
            if(Var.TCase[y, x].score[sortie-1] != -1):
                V = voisins(x, y, [pas_mur_condition], False)
                reset_case()
                #On va calculer le vecteur à prendre : le gradient de distance
                def aux1():
                    '''Fonction auxiliaire qui gère le cas où on est en contact avec un obstacle'''
                    s = Var.TCase[y, x].score[sortie-1]
                    vx = 0
                    vy = 0
                    for v in V :
                        if Var.TCase[v.y, v.x].score[sortie-1] < s :# on calcule les gradient directionnels entre v et (x,y) et on les somme
                            vx += (v.x - x)
                            vy += (v.y - y)
                    return (vx, vy)
                def aux2():
                    '''Fonction auxiliaire qui gère le cas ou on doit choisir '''
                    s = Var.TCase[y, x].score[sortie-1]
                    vx = 0
                    vy = 0
                    for v in V :
                        if Var.TCase[v.y, v.x].score[sortie-1] < s : # On choisit arbitrairement un voisin disponible en fonction du gradient
                            vx = v.x - x
                            vy = v.y - y
                    return (vx, vy)
                if len(V) == 4 : # Tous les voisins sont des cases accessibles, on calcule un gradient discret avec les cases autour de celle qu'on considère
                    vx = Var.TCase[y, x - 1].score[sortie-1] - Var.TCase[y, x + 1].score[sortie-1]
                    vy = Var.TCase[y - 1, x].score[sortie-1] - Var.TCase[y + 1, x].score[sortie-1]
                    if Var.TCase[int(y + np.sign(vy)), int(x + np.sign(vx))].type < 0 : # On gère le cas ou on fonce sur un mur
                        (vx, vy) = aux2()
                elif len(V) == 2 :
                    if abs(V[0].x - x) + abs(V[1].x - x) == 1 : # Problème de murs en coin
                        (vx, vy) = aux2()
                    else :                                      # Problème des couloirs
                        (vx, vy) = aux1()
                #Autre problème
                else :
                    (vx, vy) = aux1()
                if vect2D(vx, vy).norme() !=0 : #Normalisation du vecteur
                    Var.Tdirection[sortie-1][y, x] = vect2D(vx, vy).normalise()
                else :
                    (vx, vy) = aux2()
                    if vect2D(vx,vy).norme() !=0 :
                        Var.Tdirection[sortie-1][y, x] = vect2D(vx, vy).normalise()
                    else :
                        Var.Tdirection[sortie-1][y, x] = vect2D(vx, vy)

    return

def rafraichir():
    '''Permet de rafraichir les cases et d'appliquer le dégradé correspondant à la distance du plus court chemin et les valeurs même de cette distance en chaque case en fonction du mode'''
    cacher_ligne()
    cacher_texte()
    if Var.mode == 1 : # mode 1 = aucun affichage
        for x in range(Var.largeur) :
            for y in range(Var.hauteur) :
                Var.TCase[y, x].rafraichir()
    elif(Var.mode >= 2) : # mode 2 = on affiche uniquement un degradé
        bg = (255, 255, 255)      # Bleu foncé
        fg = (255, 0,0)    # Blanc
        for x in range(Var.largeur):
            for y in range(Var.hauteur):
                Var.TCase[y, x].rafraichir()
                if Var.TCase[y ,x].score[Var.choixSortie-1] > 0 and Var.TCase[y, x].score[Var.choixSortie-1] !=inf:
                    Var.TCase[y, x].degrade(fg, bg, Var.hauteur + Var.largeur)
        if Var.mode == 3: # mode 3 = on affiche un dégradé et les valeurs des distances
            for x in range(Var.largeur):
                for y in range(Var.hauteur):
                    Var.Ttexte[y, x].mot = str(Var.TCase[y, x].score[0])+","+str(Var.TCase[y, x].score[1])
                    Var.Ttexte[y, x].rafraichir()
        elif Var.mode == 4: # mode 4 = on affiche un degradé et les vecteurs directionnels
            for x in range(Var.largeur):
                for y in range(Var.hauteur):
                    Var.Tligne[y, x].pos1 = vect2D(x,y) * Var.dimCase + vect2D(1,1) * (Var.dimCase / 2)
                    Var.Tligne[y, x].pos2 = Var.Tligne[y, x].pos1 + Var.Tdirection[Var.choixSortie-1][y,x] * 5
                    Var.Tligne[y, x].rafraichir()
    return

# Fonctions qui réalise des statistiques sur les données de la simulation :
def stat_dMaxCase(label,sortie):
    '''Permet de mettre à jour la plus grande distance entre une case et la sortie la plus proche notée dMaxCase'''
    Var.dMaxCase[Var.choixSortie-1] = 0
    infini = False
    for x in range(Var.largeur):
        for y in range(Var.hauteur):
            if not(infini) :
                if Var.TCase[y,x].type ==0 :
                    if Var.TCase[y,x].score[Var.choixSortie-1]==inf :
                        infini = True
                    elif(Var.TCase[y,x].score[Var.choixSortie-1] > Var.dMaxCase[Var.choixSortie-1]) :
                        Var.dMaxCase[Var.choixSortie-1] = Var.TCase[y,x].score[Var.choixSortie-1]
    label.config(text = str(Var.dMaxCase))
    label.pack()
    return

def stat_nbIndiv(label):
    '''Permet de mettre à jour la fenêtre graphique en affichant le nombre d'individus encore sur le terrain'''
    label.config(text = str(len(Var.LIndiv)))
    label.pack()
    return
