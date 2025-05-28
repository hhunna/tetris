#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SAE 1.01 - Projet: Tetris - BUT INFORMATIQUE 1
# SISSOKO Bakary - JULLIEN Théo | TD B - TP Gamma

import random
from time import time, sleep
from fltk import *

fichier = 'parametres.txt'

def charger_parametres(fichier):
    parametres = {
        "LARGEUR": 10,
        "HAUTEUR": 18,
        "TAILLE_CASE": 30,
        "VITESSE_INITIALE": 0.5,
        "COULEURS": ['red', 'green', 'blue', 'cyan', 'magenta', 'orange', 'yellow']
    }

    try:
        with open(fichier, 'r') as f:
            for ligne in f:
                ligne=ligne.strip()
                if '=' in ligne:
                    cle, valeur = ligne.split('=')
                    if cle == "COULEURS":
                        parametres[cle] = valeur.split(',')
                    elif cle in ["LARGEUR", "HAUTEUR", "TAILLE_CASE"]:
                        parametres[cle] = int(valeur)
                    elif cle == "VITESSE_INITIALE":
                        parametres[cle] = float(valeur)
    except FileNotFoundError:
        pass
    return parametres

parametres = charger_parametres(fichier)

L, H = 8, 4

DELAI_HORIZONTAL = 0.08
DELAI_VERTICAL = 0.04
DELAI_ROTATION = 0.12

largeurFenetre = parametres["LARGEUR"] * parametres["TAILLE_CASE"]
hauteurFenetre = parametres["HAUTEUR"] * parametres["TAILLE_CASE"]
largeurFenetreDroite = L * parametres["TAILLE_CASE"]

#  Pièces du jeu classqiue (Taille 4)
piece_a = [[1, 1, 1, 1]]
piece_b = [[1, 1, 1], [0, 0, 1]]
piece_c = [[1, 1, 1], [1, 0, 0]]
piece_d = [[1, 1, 0], [0, 1, 1]]
piece_e = [[0, 1, 1], [1, 1, 0]]
piece_f = [[1, 1], [1, 1]]
piece_g = [[1, 1, 1], [0, 1, 0]]

# Pièces taille 5
piece_a5 = [[1, 1, 1, 1, 1]]
piece_b5 = [[1, 1, 1], [1, 0, 0], [1, 0, 0]]
piece_c5 = [[1, 1, 1], [1, 1, 0]]
piece_d5 = [[1, 1, 0], [0, 1, 1], [0, 1, 0]]
piece_e5 = [[0, 1, 1], [1, 1, 0], [1, 0, 0]]
piece_f5 = [[1, 0, 1], [1, 1, 1]]
piece_g5 = [[1, 1, 1], [0, 1, 0], [0, 1, 0]]

# Pièces taille 3
piece_a3 = [[1, 1, 1]]
piece_b3 = [[1, 1], [1, 0]]

PIECES = [piece_a, piece_b, piece_c, piece_d, piece_e, piece_f, piece_g]
PIECES_V = [piece_a, piece_b, piece_c, piece_d, piece_e, piece_f, piece_g, piece_a5, piece_b5, piece_c5, piece_d5, piece_e5, piece_f5, piece_g5, piece_a3, piece_b3]

def plateau_vide():
    plateau = []
    for i in range(parametres["HAUTEUR"]):
        plateau.append([])
        for j in range(parametres["LARGEUR"]):
            plateau[i].append(0)
    return plateau

def initialiser_jeu():
    score = 0
    niveau = 1
    lignes_supprimees = 0
    return score, niveau, lignes_supprimees

def nouvelle_piece():
    forme = random.choice(PIECES)
    couleur = random.choice(parametres["COULEURS"])
    x = (parametres["LARGEUR"] - len(forme[0])) // 2
    y = 0
    return forme, couleur, x, y

# SI LE MODE DE JEU EST mode_Polyominosa()
def nouvelle_piece_v2():
    forme = random.choice(PIECES_V)
    couleur = random.choice(parametres["COULEURS"])
    x = (parametres["LARGEUR"] - len(forme[0])) // 2
    y = 0
    return forme, couleur, x, y


def rotation_piece(forme):
    lignes, colonnes = len(forme), len(forme[0])
    nouvelle_forme = []
    for j in range(colonnes):
        nouvelle_ligne = []
        for i in range(lignes):
            nouvelle_ligne.append(0)
        nouvelle_forme.append(nouvelle_ligne)
    for i in range(lignes):
        for j in range(colonnes):
            nouvelle_forme[j][lignes - i - 1] = forme[i][j]
    return nouvelle_forme

def obtenir_coordonnees(forme, x, y):
    coordonnees = []
    for i, ligne in enumerate(forme):
        for j, cellule in enumerate(ligne):
            if cellule != 0:
                nx, ny = x + j, y + i
                coordonnees.append((nx, ny))
    return coordonnees

def position_valide(plateau, forme, x, y, dx=0, dy=0):
    cords = obtenir_coordonnees(forme, x, y)
    for cx, cy in cords:
        nx, ny = cx + dx, cy + dy
        if nx < 0 or nx >= parametres["LARGEUR"] or ny < 0 or ny >= parametres["HAUTEUR"]:
            return False
        if ny >= 0 and nx >= 0 and plateau[ny][nx] != 0:
            return False
    return True

def verrouiller_piece(plateau, forme, x, y, couleur):
    cords = obtenir_coordonnees(forme, x, y)
    for cx, cy in cords:
        if 0 <= cy < len(plateau) and 0 <= cx < len(plateau[0]):
            plateau[cy][cx] = couleur

def effacer_lignes(plateau, score, lignes_supprimees, niveau):
    lignes_non_completes = []
    for ligne in plateau:
        cellule_vide = False
        for cellule in ligne:
            if cellule == 0:
                cellule_vide = True
                break
        if cellule_vide:
            lignes_non_completes.append(ligne)
    lignes_effacees = parametres["HAUTEUR"] - len(lignes_non_completes)
    
    plateau = []
    for i in range(lignes_effacees):
        plateau.append([0] * parametres["LARGEUR"])
    plateau += lignes_non_completes

    if lignes_effacees > 0:
        points = [0, 40, 100, 300, 500, 700]
        score += points[lignes_effacees] * niveau
        lignes_supprimees += lignes_effacees
    return plateau, score, lignes_supprimees

def deplacer_piece(x, y, dx, dy):
    return x + dx, y + dy

def gerer_jeu(lignes_supprimees, niveau, vitesse):
    if lignes_supprimees >= niveau * 10:
        niveau += 1
        vitesse *= 0.8
    return niveau, vitesse

def dessine_plateau(plateau):
    for y, ligne in enumerate(plateau):
        for x, cellule in enumerate(ligne):
            if cellule:
                rectangle(x * parametres["TAILLE_CASE"], y * parametres["TAILLE_CASE"], (x + 1) * parametres["TAILLE_CASE"], (y + 1) * parametres["TAILLE_CASE"], remplissage=cellule, couleur="black")

def dessine_plateau2(plateau):
    for y, ligne in enumerate(plateau):
        for x, cellule in enumerate(ligne):
            if cellule:
                rectangle(x * parametres["TAILLE_CASE"] + largeurFenetre, y * parametres["TAILLE_CASE"], (x + 1) * parametres["TAILLE_CASE"] + largeurFenetre, (y + 1) * parametres["TAILLE_CASE"], remplissage=cellule, couleur="black")

def dessine_piece_active(forme_actuelle, couleur_actuelle, x_actuel, y_actuel):
    cords = obtenir_coordonnees(forme_actuelle, x_actuel, y_actuel)
    for cx, cy in cords:
        rectangle(cx * parametres["TAILLE_CASE"], cy * parametres["TAILLE_CASE"], (cx + 1) * parametres["TAILLE_CASE"], (cy + 1) * parametres["TAILLE_CASE"], remplissage=couleur_actuelle, couleur="black")

def dessine_piece_active2(forme_actuelle, couleur_actuelle, x_actuel, y_actuel):
    cords = obtenir_coordonnees(forme_actuelle, x_actuel, y_actuel)
    for cx, cy in cords:
        rectangle(cx * parametres["TAILLE_CASE"] + largeurFenetre, cy * parametres["TAILLE_CASE"], (cx + 1) * parametres["TAILLE_CASE"] + largeurFenetre, (cy + 1) * parametres["TAILLE_CASE"], remplissage=couleur_actuelle, couleur="black")
        
def affiche_piece_suivante(forme_suivante, couleur_suivante):
    x_fenetre = largeurFenetre + (largeurFenetreDroite - (len(forme_suivante[0]) * parametres["TAILLE_CASE"])) // 2
    for y, ligne in enumerate(forme_suivante):
        for x, cellule in enumerate(ligne):
            if cellule == 1:
                rectangle(x * parametres["TAILLE_CASE"] + x_fenetre, y * parametres["TAILLE_CASE"] + parametres["TAILLE_CASE"], (x + 1) * parametres["TAILLE_CASE"] + x_fenetre, (y + 1) * parametres["TAILLE_CASE"] + parametres["TAILLE_CASE"], remplissage=couleur_suivante, couleur="black")

def affiche_interface(score, niveau, lignes_supprimees):
    x = largeurFenetre
    rectangle(x, 0, x + 1, hauteurFenetre, remplissage="black")
    x += largeurFenetreDroite // 2 // 2
    y = hauteurFenetre // 2
    taille = 20
    texte(x, y-taille*2, f"Niveau : {niveau}", taille=taille, couleur="black")
    texte(x, y, f"Score : {score}", taille=taille, couleur="black")
    texte(x, y+taille*2, f"Lignes : {lignes_supprimees}", taille=taille, couleur="black")

def pourrissement(plateau):
    cellules_occupees = []
    for i in range(len(plateau)):
        for j in range(len(plateau[i])):
            if plateau[i][j] != 0:
                cellules_occupees.append((j, i))
    if cellules_occupees:
        j, i = random.choice(cellules_occupees)
        plateau[i][j] = 0
    return plateau

def lignes_completes(plateau):
    plateau_lignes_completes = []
    for ligne in plateau:
        count = 0
        for cellule in ligne:
            if cellule:
                count+=1
        if count == parametres["LARGEUR"]:
            plateau_lignes_completes.append(ligne)
    return plateau_lignes_completes

def envoyer_lignes(plateau, n, plateau_lignes_completes):
    plateau_cellule = []
    for ligne in plateau:
        ligne_vide = True
        for cellule in ligne:
            if cellule != 0:
                ligne_vide = False
                break
        if ligne_vide == False:
            plateau_cellule.append(ligne)

    nouveau_plateau = []
    nb = parametres["HAUTEUR"] - len(plateau_cellule) - (n-1)
    for i in range(nb):
        nouveau_plateau.append([0] * parametres["LARGEUR"])
    nouveau_plateau.extend(plateau_cellule)

    plateau_ligne = []
    for ligne in plateau_lignes_completes:
        if len(plateau_ligne) < (n-1):
            plateau_ligne.append(ligne)
        else:
            break

    index_aleatoire = random.randrange(0, parametres["LARGEUR"])
    for i in range(len(plateau_ligne)):
        plateau_ligne[i][index_aleatoire] = 0

    nouveau_plateau.extend(plateau_ligne)
    return nouveau_plateau

def detecter_piece(plateau, ignore=None):

    couleur = None
    piece = set()
    ignore = ignore or set()
    for i in range(len(plateau)):
        for j in range(len(plateau[0])):
            if (i, j) not in ignore and plateau[i][j] != 0:
                if plateau[i][j] == couleur or couleur is None:
                    couleur = plateau[i][j]
                    piece.add((i,j))
                    if len(piece) >= 4:
                        return piece, couleur
    return None, None

def verifier_contact(piece1, piece2):
    voisins = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    contacts = 0

    for x1, y1 in piece1:
        for dx, dy in voisins:
            voisin = (x1 + dx, y1 + dy)
            if voisin in piece2:
                contacts += 1
                if contacts >= 2:
                    return True
    return False

def supprimer(plateau, piece1, piece2):
    for i, j in piece1:
        plateau[i][j] = 0
    for i, j in piece2:
        plateau[i][j] = 0

def main():
    cree_fenetre(largeurFenetre + largeurFenetreDroite, hauteurFenetre)
    plateau = plateau_vide()
    forme_actuelle, couleur_actuelle, x_actuel, y_actuel = nouvelle_piece()
    forme_suivante, couleur_suivante, x_suivant, y_suivant = nouvelle_piece()
    score, niveau, lignes_supprimees = initialiser_jeu()
    dernier_temps = time()
    dernier_deplacement_horizontal = 0
    dernier_deplacement_vertical = 0
    dernier_rotation = 0
    vitesse = parametres["VITESSE_INITIALE"]

    while True:
        ev = donne_ev()
        tev = type_ev(ev)
        if tev == "ClicGauche":
            break
        efface_tout()
        dessine_plateau(plateau)
        dessine_piece_active(forme_actuelle, couleur_actuelle, x_actuel, y_actuel)
        affiche_piece_suivante(forme_suivante, couleur_suivante)
        affiche_interface(score, niveau, lignes_supprimees)
        mise_a_jour()
        temps_courant = time()

        if touche_pressee('Left') and (temps_courant - dernier_deplacement_horizontal > DELAI_HORIZONTAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, -1, 0):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, -1, 0)
            dernier_deplacement_horizontal = temps_courant

        elif touche_pressee('Right') and (temps_courant - dernier_deplacement_horizontal > DELAI_HORIZONTAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 1, 0):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 1, 0)
            dernier_deplacement_horizontal = temps_courant

        if touche_pressee('Down') and (temps_courant - dernier_deplacement_vertical > DELAI_VERTICAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 0, 1):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 0, 1)
            dernier_deplacement_vertical = temps_courant

        if touche_pressee('Up') and (temps_courant - dernier_rotation > DELAI_ROTATION):
            nouvelle_forme = rotation_piece(forme_actuelle)
            if position_valide(plateau, nouvelle_forme, x_actuel, y_actuel):
                forme_actuelle = nouvelle_forme
            dernier_rotation = temps_courant

        if touche_pressee('p'):
            efface_tout()
            texte(L, H, "PAUSE", couleur="black", taille=25)
            attend_clic_gauche()

        if temps_courant - dernier_temps > vitesse:  
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 0, 1):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 0, 1)
            else:
                verrouiller_piece(plateau, forme_actuelle, x_actuel, y_actuel, couleur_actuelle)
                forme_actuelle, couleur_actuelle, x_actuel, y_actuel = forme_suivante, couleur_suivante, x_suivant, y_suivant
                forme_suivante, couleur_suivante, x_suivant, y_suivant = nouvelle_piece()
                plateau, score, lignes_supprimees = effacer_lignes(plateau, score, lignes_supprimees, niveau)
                niveau, vitesse = gerer_jeu(lignes_supprimees, niveau, vitesse)
                if not position_valide(plateau, forme_actuelle, x_actuel, y_actuel):
                    #verrouiller_piece(plateau, forme_actuelle, x_actuel, y_actuel, couleur_actuelle)
                    #dessine_plateau(plateau)
                    #sleep(2)
                    efface_tout()
                    texte((largeurFenetre+largeurFenetreDroite)//2, hauteurFenetre//2, f"Game Over! Score: {score}", taille=20, couleur="black", ancrage='center')
                    mise_a_jour()
                    while True:
                        ev = donne_ev()
                        tev = type_ev(ev)
                        if tev == "ClicGauche":
                            break
                        mise_a_jour()
                    return
            dernier_temps = temps_courant


def mode_Polyominosa():
    cree_fenetre(largeurFenetre + largeurFenetreDroite, hauteurFenetre)
    plateau = plateau_vide()
    forme_actuelle, couleur_actuelle, x_actuel, y_actuel = nouvelle_piece_v2()
    forme_suivante, couleur_suivante, x_suivant, y_suivant = nouvelle_piece_v2()
    score, niveau, lignes_supprimees = initialiser_jeu()
    dernier_temps = time()
    dernier_deplacement_horizontal = 0
    dernier_deplacement_vertical = 0
    dernier_rotation = 0
    vitesse = parametres["VITESSE_INITIALE"]

    while True:
        ev = donne_ev()
        tev = type_ev(ev)
        if tev == "ClicGauche":
            break
        efface_tout()
        dessine_plateau(plateau)
        dessine_piece_active(forme_actuelle, couleur_actuelle, x_actuel, y_actuel)
        affiche_piece_suivante(forme_suivante, couleur_suivante)
        affiche_interface(score, niveau, lignes_supprimees)
        mise_a_jour()
        temps_courant = time()

        if touche_pressee('Left') and (temps_courant - dernier_deplacement_horizontal > DELAI_HORIZONTAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, -1, 0):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, -1, 0)
            dernier_deplacement_horizontal = temps_courant

        elif touche_pressee('Right') and (temps_courant - dernier_deplacement_horizontal > DELAI_HORIZONTAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 1, 0):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 1, 0)
            dernier_deplacement_horizontal = temps_courant

        if touche_pressee('Down') and (temps_courant - dernier_deplacement_vertical > DELAI_VERTICAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 0, 1):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 0, 1)
            dernier_deplacement_vertical = temps_courant

        if touche_pressee('Up') and (temps_courant - dernier_rotation > DELAI_ROTATION):
            nouvelle_forme = rotation_piece(forme_actuelle)
            if position_valide(plateau, nouvelle_forme, x_actuel, y_actuel):
                forme_actuelle = nouvelle_forme
            dernier_rotation = temps_courant

        if touche_pressee('p'):
            efface_tout()
            texte(L, H, "PAUSE", couleur="black", taille=25)
            attend_clic_gauche()

        if temps_courant - dernier_temps > vitesse:  
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 0, 1):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 0, 1)
            else:
                verrouiller_piece(plateau, forme_actuelle, x_actuel, y_actuel, couleur_actuelle)
                forme_actuelle, couleur_actuelle, x_actuel, y_actuel = forme_suivante, couleur_suivante, x_suivant, y_suivant
                forme_suivante, couleur_suivante, x_suivant, y_suivant = nouvelle_piece_v2()
                plateau, score, lignes_supprimees = effacer_lignes(plateau, score, lignes_supprimees, niveau)
                niveau, vitesse = gerer_jeu(lignes_supprimees, niveau, vitesse)
                if not position_valide(plateau, forme_actuelle, x_actuel, y_actuel):
                    print("Game Over! Score:", score)
                    break
            dernier_temps = temps_courant
    ferme_fenetre()


def mode2joueurs():
    cree_fenetre(largeurFenetre * 2, hauteurFenetre)
    plateau1, plateau2 = plateau_vide(), plateau_vide()
    forme_actuelle1, couleur_actuelle1, x_actuel1, y_actuel1 = nouvelle_piece()
    forme_suivante1, couleur_suivante1, x_suivant1, y_suivant1 = nouvelle_piece()
    forme_actuelle2, couleur_actuelle2, x_actuel2, y_actuel2 = nouvelle_piece()
    forme_suivante2, couleur_suivante2, x_suivant2, y_suivant2 = nouvelle_piece()
    score1, niveau1, lignes_supprimees1 = initialiser_jeu()
    score2, niveau2, lignes_supprimees2 = initialiser_jeu()
    dernier_temps1, dernier_temps2 = time(), time()
    dernier_deplacement_horizontal1, dernier_deplacement_horizontal2 = 0, 0
    dernier_deplacement_vertical1, dernier_deplacement_vertical2 = 0, 0
    dernier_rotation1, dernier_rotation2 = 0, 0
    vitesse1, vitesse2 = parametres["VITESSE_INITIALE"], parametres["VITESSE_INITIALE"]
    lignes_suppr_avant1 = lignes_supprimees1
    lignes_suppr_avant2 = lignes_supprimees2
    while True:
        ev = donne_ev()
        tev = type_ev(ev)
        if tev == "ClicGauche":
            break
        efface_tout()
        dessine_plateau(plateau1)
        dessine_plateau2(plateau2)
        dessine_piece_active(forme_actuelle1, couleur_actuelle1, x_actuel1, y_actuel1)
        dessine_piece_active2(forme_actuelle2, couleur_actuelle2, x_actuel2, y_actuel2)
        rectangle(largeurFenetre, 0, largeurFenetre + 1, hauteurFenetre, remplissage="black")
        mise_a_jour()
        temps_courant = time()

        if touche_pressee('p'):
            efface_tout()
            texte(L, H, "PAUSE", couleur="black", taille=25)
            attend_clic_gauche()

        if touche_pressee('q') and (temps_courant - dernier_deplacement_horizontal1 > DELAI_HORIZONTAL):
            if position_valide(plateau1, forme_actuelle1, x_actuel1, y_actuel1, -1, 0):
                x_actuel1, y_actuel1 = deplacer_piece(x_actuel1, y_actuel1, -1, 0)
            dernier_deplacement_horizontal1 = temps_courant
        elif touche_pressee('d') and (temps_courant - dernier_deplacement_horizontal1 > DELAI_HORIZONTAL):
            if position_valide(plateau1, forme_actuelle1, x_actuel1, y_actuel1, 1, 0):
                x_actuel1, y_actuel1 = deplacer_piece(x_actuel1, y_actuel1, 1, 0)
            dernier_deplacement_horizontal1 = temps_courant
        if touche_pressee('s') and (temps_courant - dernier_deplacement_vertical1 > DELAI_VERTICAL):
            if position_valide(plateau1, forme_actuelle1, x_actuel1, y_actuel1, 0, 1):
                x_actuel1, y_actuel1 = deplacer_piece(x_actuel1, y_actuel1, 0, 1)
            dernier_deplacement_vertical1 = temps_courant
        if touche_pressee('z') and (temps_courant - dernier_rotation1 > DELAI_ROTATION):
            nouvelle_forme = rotation_piece(forme_actuelle1)
            if position_valide(plateau1, nouvelle_forme, x_actuel1, y_actuel1):
                forme_actuelle1 = nouvelle_forme
            dernier_rotation1 = temps_courant

        if temps_courant - dernier_temps1 > vitesse1:  
            if position_valide(plateau1, forme_actuelle1, x_actuel1, y_actuel1, 0, 1):
                x_actuel1, y_actuel1 = deplacer_piece(x_actuel1, y_actuel1, 0, 1)
            else:
                verrouiller_piece(plateau1, forme_actuelle1, x_actuel1, y_actuel1, couleur_actuelle1)
                forme_actuelle1, couleur_actuelle1, x_actuel1, y_actuel1 = forme_suivante1, couleur_suivante1, x_suivant1, y_suivant1
                forme_suivante1, couleur_suivante1, x_suivant1, y_suivant1 = nouvelle_piece()
                plateau1_lignes_completes = lignes_completes(plateau1)
                plateau1, score1, lignes_supprimees1 = effacer_lignes(plateau1, score1, lignes_supprimees1, niveau1)
                niveau1, vitesse1 = gerer_jeu(lignes_supprimees1, niveau1, vitesse1)
                if lignes_supprimees1 > lignes_suppr_avant1:
                    n = lignes_supprimees1 - lignes_suppr_avant1
                    if n > 1:
                        plateau2 = envoyer_lignes(plateau2, n, plateau1_lignes_completes)
                        #while not position_valide(plateau2, forme_actuelle2, x_actuel2, y_actuel2):
                            #deplacer_piece(x_actuel2, y_actuel2, 0, -1)
                    lignes_suppr_avant1 = lignes_supprimees1
                if not position_valide(plateau1, forme_actuelle1, x_actuel1, y_actuel1):
                    print("Game Over Player 1! Score:", score1)
                    break
            dernier_temps1 = temps_courant


        if touche_pressee('j') and (temps_courant - dernier_deplacement_horizontal2 > DELAI_HORIZONTAL):
            if position_valide(plateau2, forme_actuelle2, x_actuel2, y_actuel2, -1, 0):
                x_actuel2, y_actuel2 = deplacer_piece(x_actuel2, y_actuel2, -1, 0)
            dernier_deplacement_horizontal2 = temps_courant

        elif touche_pressee('l') and (temps_courant - dernier_deplacement_horizontal2 > DELAI_HORIZONTAL):
            if position_valide(plateau2, forme_actuelle2, x_actuel2, y_actuel2, 1, 0):
                x_actuel2, y_actuel2 = deplacer_piece(x_actuel2, y_actuel2, 1, 0)
            dernier_deplacement_horizontal2 = temps_courant

        if touche_pressee('k') and (temps_courant - dernier_deplacement_vertical2 > DELAI_VERTICAL):
            if position_valide(plateau2, forme_actuelle2, x_actuel2, y_actuel2, 0, 1):
                x_actuel2, y_actuel2 = deplacer_piece(x_actuel2, y_actuel2, 0, 1)
            dernier_deplacement_vertical2 = temps_courant

        if touche_pressee('i') and (temps_courant - dernier_rotation2 > DELAI_ROTATION):
            nouvelle_forme = rotation_piece(forme_actuelle2)
            if position_valide(plateau2, nouvelle_forme, x_actuel2, y_actuel2):
                forme_actuelle2 = nouvelle_forme
                dernier_rotation2 = temps_courant

        if temps_courant - dernier_temps2 > vitesse2:
            if position_valide(plateau2, forme_actuelle2, x_actuel2, y_actuel2, 0, 1):
                x_actuel2, y_actuel2 = deplacer_piece(x_actuel2, y_actuel2, 0, 1)
            else:
                verrouiller_piece(plateau2, forme_actuelle2, x_actuel2, y_actuel2, couleur_actuelle2)
                forme_actuelle2, couleur_actuelle2, x_actuel2, y_actuel2 = forme_suivante2, couleur_suivante2, x_suivant2, y_suivant2
                forme_suivante2, couleur_suivante2, x_suivant2, y_suivant2 = nouvelle_piece()
                plateau2_lignes_completes = lignes_completes(plateau2)
                plateau2, score2, lignes_supprimees2 = effacer_lignes(plateau2, score2, lignes_supprimees2, niveau2)
                niveau2, vitesse2 = gerer_jeu(lignes_supprimees2, niveau2, vitesse2)
                if lignes_supprimees2 > lignes_suppr_avant2:
                    n = lignes_supprimees2 - lignes_suppr_avant2
                    if n > 1:
                        plateau1 = envoyer_lignes(plateau1, n, plateau2_lignes_completes)
                    lignes_suppr_avant2 = lignes_supprimees2
                if not position_valide(plateau2, forme_actuelle2, x_actuel2, y_actuel2):
                    print("Game Over Player 2! Score:", score2)
                    break
            dernier_temps2 = temps_courant
        
    ferme_fenetre()

def mode_pourrissement():
    x = int(input("Choisissez une intervalle de pourrissement (par défault : 60) :")) # peut etre via argument fichier invite de cmd
    accelerer = x // 5
    accelerer2 = x // 21
    cree_fenetre(largeurFenetre + largeurFenetreDroite, hauteurFenetre)
    plateau = plateau_vide()
    forme_actuelle, couleur_actuelle, x_actuel, y_actuel = nouvelle_piece()
    forme_suivante, couleur_suivante, x_suivant, y_suivant = nouvelle_piece()
    score, niveau, lignes_supprimees = initialiser_jeu()
    dernier_temps = time()
    dernier_deplacement_horizontal = 0
    dernier_deplacement_vertical = 0
    dernier_rotation = 0
    vitesse = parametres["VITESSE_INITIALE"]
    dernier_pourrissement = time()
    niveau_avant = niveau

    while True:
        ev = donne_ev()
        tev = type_ev(ev)
        if tev == "ClicGauche":
            break
        efface_tout()
        dessine_plateau(plateau)
        dessine_piece_active(forme_actuelle, couleur_actuelle, x_actuel, y_actuel)
        affiche_piece_suivante(forme_suivante, couleur_suivante)
        affiche_interface(score, niveau, lignes_supprimees)
        mise_a_jour()
        temps_courant = time()

        if touche_pressee('Left') and (temps_courant - dernier_deplacement_horizontal > DELAI_HORIZONTAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, -1, 0):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, -1, 0)
            dernier_deplacement_horizontal = temps_courant

        elif touche_pressee('Right') and (temps_courant - dernier_deplacement_horizontal > DELAI_HORIZONTAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 1, 0):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 1, 0)
            dernier_deplacement_horizontal = temps_courant

        if touche_pressee('Down') and (temps_courant - dernier_deplacement_vertical > DELAI_VERTICAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 0, 1):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 0, 1)
            dernier_deplacement_vertical = temps_courant

        if touche_pressee('Up') and (temps_courant - dernier_rotation > DELAI_ROTATION):
            nouvelle_forme = rotation_piece(forme_actuelle)
            if position_valide(plateau, nouvelle_forme, x_actuel, y_actuel):
                forme_actuelle = nouvelle_forme
            dernier_rotation = temps_courant

        if temps_courant - dernier_temps > vitesse:  
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 0, 1):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 0, 1)
            else:
                verrouiller_piece(plateau, forme_actuelle, x_actuel, y_actuel, couleur_actuelle)
                forme_actuelle, couleur_actuelle, x_actuel, y_actuel = forme_suivante, couleur_suivante, x_suivant, y_suivant
                forme_suivante, couleur_suivante, x_suivant, y_suivant = nouvelle_piece()
                plateau, score, lignes_supprimees = effacer_lignes(plateau, score, lignes_supprimees, niveau)
                niveau, vitesse = gerer_jeu(lignes_supprimees, niveau, vitesse)
                if not position_valide(plateau, forme_actuelle, x_actuel, y_actuel):
                    efface_tout()
                    texte((largeurFenetre+largeurFenetreDroite)//2, hauteurFenetre//2, f"Game Over! Score: {score}", taille=20, couleur="black", ancrage='center')
                    mise_a_jour()
                    while True:
                        ev = donne_ev()
                        tev = type_ev(ev)
                        if tev == "ClicGauche":
                            break
                        mise_a_jour()
                    return
            dernier_temps = temps_courant
        if niveau_avant != niveau:
            niveau_avant = niveau
            if x > accelerer:
                x -= accelerer
            else:
                x -= accelerer2
        if temps_courant - dernier_pourrissement >= x:
            plateau = pourrissement(plateau)
            dernier_pourrissement = temps_courant


def elimination_par_couleurs_adjacentes():
    cree_fenetre(largeurFenetre + largeurFenetreDroite, hauteurFenetre)
    plateau = plateau_vide()
    forme_actuelle, couleur_actuelle, x_actuel, y_actuel = nouvelle_piece()
    forme_suivante, couleur_suivante, x_suivant, y_suivant = nouvelle_piece()
    score, niveau, lignes_supprimees = initialiser_jeu()
    dernier_temps = time()
    dernier_deplacement_horizontal = 0
    dernier_deplacement_vertical = 0
    dernier_rotation = 0
    vitesse = parametres["VITESSE_INITIALE"]

    while True:
        ev = donne_ev()
        tev = type_ev(ev)
        if tev == "ClicGauche":
            break
        efface_tout()
        dessine_plateau(plateau)
        dessine_piece_active(forme_actuelle, couleur_actuelle, x_actuel, y_actuel)
        affiche_piece_suivante(forme_suivante, couleur_suivante)
        affiche_interface(score, niveau, lignes_supprimees)
        mise_a_jour()
        temps_courant = time()

        if touche_pressee('Left') and (temps_courant - dernier_deplacement_horizontal > DELAI_HORIZONTAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, -1, 0):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, -1, 0)
            dernier_deplacement_horizontal = temps_courant

        elif touche_pressee('Right') and (temps_courant - dernier_deplacement_horizontal > DELAI_HORIZONTAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 1, 0):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 1, 0)
            dernier_deplacement_horizontal = temps_courant

        if touche_pressee('Down') and (temps_courant - dernier_deplacement_vertical > DELAI_VERTICAL):
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 0, 1):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 0, 1)
            dernier_deplacement_vertical = temps_courant

        if touche_pressee('Up') and (temps_courant - dernier_rotation > DELAI_ROTATION):
            nouvelle_forme = rotation_piece(forme_actuelle)
            if position_valide(plateau, nouvelle_forme, x_actuel, y_actuel):
                forme_actuelle = nouvelle_forme
            dernier_rotation = temps_courant

        if touche_pressee('p'):
            efface_tout()
            texte(L, H, "PAUSE", couleur="black", taille=25)
            attend_clic_gauche()

        if temps_courant - dernier_temps > vitesse:
            if position_valide(plateau, forme_actuelle, x_actuel, y_actuel, 0, 1):
                x_actuel, y_actuel = deplacer_piece(x_actuel, y_actuel, 0, 1)
            else:
                verrouiller_piece(plateau, forme_actuelle, x_actuel, y_actuel, couleur_actuelle)

                piece1, couleur1 = detecter_piece(plateau)
                piece2, couleur2 = detecter_piece(plateau, ignore=piece1)
                if couleur1 == couleur2 and couleur1 != None:
                    contact = verifier_contact(piece1, piece2)
                    if contact:
                        supprimer(plateau, piece1, piece2)

                forme_actuelle, couleur_actuelle, x_actuel, y_actuel = forme_suivante, couleur_suivante, x_suivant, y_suivant
                forme_suivante, couleur_suivante, x_suivant, y_suivant = nouvelle_piece()
                plateau, score, lignes_supprimees = effacer_lignes(plateau, score, lignes_supprimees, niveau)
                niveau, vitesse = gerer_jeu(lignes_supprimees, niveau, vitesse)
                if not position_valide(plateau, forme_actuelle, x_actuel, y_actuel):
                    efface_tout()
                    texte((largeurFenetre+largeurFenetreDroite)//2, hauteurFenetre//2, f"Game Over! Score: {score}", taille=20, couleur="black", ancrage='center')
                    mise_a_jour()
                    while True:
                        ev = donne_ev()
                        tev = type_ev(ev)
                        if tev == "ClicGauche":
                            break
                        mise_a_jour()
                    return
            dernier_temps = temps_courant

if __name__ == '__main__':
    main();