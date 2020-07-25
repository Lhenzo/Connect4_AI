import numpy as np  #création matrices
import random
import copy
import sys
import pygame
import easygui
from pygame.locals import *


BLEU = (0,0,255)
NOIR = (0,0,0)
BLANC = (255, 255, 255)
ROUGE = (255,0,0)
JAUNE = (255,255,0)

#table des scores
compteur_vic_J1 = 0
compteur_vic_J2 = 0
compteur_vic_IA = 0
compteur_vic_J1vIA = 0

# garde en mémoire le mode de jeu précédent, si True ne redemande pas les pseudos, si False alors demande les pseudos
J1vJ2 = False

#valeurs d'initialisation nécessaires pour faire tourner le code
continuer = True
rejouer = False
quitter = 1

############################################################## MENU #######################################################################

while continuer:  ## boucle si le joueur désire rejouer ou aller au menu
    if quitter == 0: #permet de ne pas tout selectionner une nouvelle fois si on veut juste rejouer
        pass
    else: #si on appuie sur menu

    #permet au joueur de choisir le mode de jeu : 1v1 ou 1vIA
        if quitter ==1:
            choix_jeu = easygui.indexbox(msg="Choississez le type de jeu", choices=("Joueur 1 contre Joueur 2", "Contre IA"))
            if choix_jeu == 1:
                IA_NIVEAU = easygui.indexbox(msg="Choississez le niveau de difficulté de l'IA", choices=("Très facile", "Moyen", "Expert", "Légende")) #le mode légende met du temps car il cherche loin et est imbattable jusqu'à lors, pas forcément utile
                if IA_NIVEAU == None : #si le joueur clic sur la croix, le jeu se ferme
                    continuer = False
                    break
                else :
                    profondeur = IA_NIVEAU + 1
            elif choix_jeu == 0:

            ###### Si partie rejouer, ne redemande pas la saisie des pseudos
                if rejouer == True and J1vJ2 == True :
                    pass
                else : #si on a joué avec l'IA avant et que l'on veut jouer en 1v1 
                    pseudo = easygui.multenterbox( msg="Renseignez ci-dessous vos pseudos : ", title="Pseudo", fields = ["Joueur Rouge", "Joueur Jaune"])
                    if pseudo == None: #si le joueur clic sur la croix, le jeu se ferme
                        continuer = False
                        break
                    else :
                        pseudo_rouge = pseudo[0]
                        pseudo_jaune = pseudo[1]
                        ##### si pas de saisie, alors désignation automatique
                        if pseudo_rouge == '' :
                            pseudo_rouge = 'ROUGE'
                        if pseudo_jaune == '' :
                            pseudo_jaune = 'JAUNE'

        else : #si le joueur clic sur la croix, le jeu se ferme
            continuer = False
            break

        choix_grille = easygui.indexbox(msg="Choississez la taille de grille", choices=("Taille normale (6x7)", "Choisir"))
        if choix_grille == 0: #grille conventionnelle 
            RANGEE_DIM = 6
            COLONNE_DIM = 7
        elif choix_grille == 1:
            choix_taille_grille = easygui.indexbox(msg="Choisissez parmis les tailles suivantes :", choices=("7 par 8", "8 par 9", "9 par 10"))
            if choix_taille_grille == 0:
                RANGEE_DIM = 7
                COLONNE_DIM = 8
            elif choix_taille_grille == 1:
                RANGEE_DIM = 8
                COLONNE_DIM = 9
            elif choix_taille_grille == 2:
                RANGEE_DIM = 9
                COLONNE_DIM = 10
        else :
            continuer = False
            break

########################################################### DEFINITIONS #######################################################################
    
    def init_grille():
        grille = np.zeros((RANGEE_DIM,COLONNE_DIM)) #créer une matrice nulle au dimensions demandées
        return grille

    def jouer_pion(grille, rangee, colonne, pion): #remplace la valeur 0 par la valeur du pion (1 ou 2)
        grille[rangee][colonne] = pion

    def verif_localisation(grille, colonne): #retourne True si la colonne est jouable
        if grille[RANGEE_DIM-1][colonne] == 0: #vérifie que la colonne n'est pas pleine soit qu'il n'y ai pas de pion tout en haut
            return True
        else:
            return False

    def prochaine_ligne_vide(grille, colonne): #renvoie la dernière valeur de la rangée libre dans une colonne
        for rangee_libre in range(COLONNE_DIM):
            if grille[rangee_libre][colonne] == 0:
                return rangee_libre
            
    def print_grille(grille):
        print(np.flip(grille, 0)) #on retourne la grille crée par numpy, à la fin de tout, juste imprimer la grille normale
        
    def a_qui_le_tour(tour):
        if tour % 2 == 1 : #identification tour joueur avec la parité 
            pion = 1
        else :
            pion = 2
        return pion
            
    def verif_victoire(grille, pion):
        #Horizontale
        for l in range(RANGEE_DIM): #incrémente matrice[i][y] pour vérifier chaque ligne
            for c in range(COLONNE_DIM-3): #-3 car le code prend en compte la colonne +3
                if grille[l][c] == pion and grille[l][c+1] == pion and grille[l][c+2] == pion and grille[l][c+3] == pion :
                    return True
        #Verticale
        for c in range(COLONNE_DIM): #incrémente matrice[i][y] pour vérifier chaque colonne
            for l in range(RANGEE_DIM-3):
                if grille[l][c] == pion and grille[l+1][c] == pion and grille[l+2][c] == pion and grille[l+3][c] == pion :
                    return True
        #Diagonale /
        for c in range(COLONNE_DIM-3): #incrémente matrice[i][y] pour vérifier chaque colonne
            for l in range(RANGEE_DIM-3):
                if grille[l][c] == pion and grille[l+1][c+1] == pion and grille[l+2][c+2] == pion and grille[l+3][c+3] == pion :
                    return True
        #Diagonale \
        for c in range(COLONNE_DIM-3): #incrémente matrice[i][y] pour vérifier chaque colonne
            for l in range(3,RANGEE_DIM):
                if grille[l][c] == pion and grille[l-1][c+1] == pion and grille[l-2][c+2] == pion and grille[l-3][c+3] == pion :
                    return True    

        
    def creation_grille(grille):
        for c in range(COLONNE_DIM):
            for l in range(RANGEE_DIM): #(posX,posY,dimX,dimY)
                pygame.draw.rect(affichage, BLEU, (c*dim_pion, l*dim_pion+dim_pion, dim_pion, dim_pion)) #créer une zone bleu sur dans la fenêtre de jeu
                incr_X = int(c*dim_pion+dim_pion/2)
                incr_Y = int(l*dim_pion+dim_pion+dim_pion/2)
                pygame.draw.circle(affichage, BLANC,(incr_X,incr_Y),rayon) #créer les trous blancs dans la zone bleue pour obtenir une grille puissance 4
        
    def maj_grille(grille): #met à jour grille en ajoutant un rond ROUGE ou JAUNE en fonction de la valeur dans la matricé cachée (1 pour ROUGE ET 2 pour JAUNE)
        for c in range(COLONNE_DIM):
            for l in range(RANGEE_DIM):
                posX = int(c*dim_pion+dim_pion/2)
                posY = dim_hauteur - int(l*dim_pion+dim_pion/2) #prend en compte la marge pour faire apparaitres les consignes et le pion à jouer
                if grille[l][c] == 1:  
                    pygame.draw.circle(affichage, ROUGE,(posX, posY),rayon)
                elif grille[l][c] == 2: 
                    pygame.draw.circle(affichage, JAUNE,(posX, posY),rayon)

    def CoupIA(grille):
        evaluation = Evaluation(grille, 2, IA_NIVEAU)
        # On cherche à trouver le meilleur coup de tous les coups potentiels
        meilleurCoup = -1 #probabilité la plus basse possible (1 = 100% de chance de gagner, -1 = 100% de chance de perdre)
        for i in range(COLONNE_DIM):
            if evaluation[i] > meilleurCoup and verif_localisation(grille, i): 
#si la valeur de proba du coup potentiel i de la liste eval a une + grosse valeur, cette valeur est retenue comme étant la meilleure pour l'IA
                meilleurCoup = evaluation[i]

#ce meilleur coup est stocké dans une liste de meilleurCoups pour avoir toutes les possibilités rapportant au meilleur coup à faire (car il se peut que plusieurs coups donnent la victoire par exemple)
        meilleurCoups = []
        for i in range(len(evaluation)):
            if evaluation[i] == meilleurCoup and verif_localisation(grille, i):
                meilleurCoups.append(i)
        return random.choice(meilleurCoups) #tous les meilleurs coups on a la même valeur : meilleurCoup, donc on choisit au hasard


    def Evaluation(grille, pion, profondeur):
        if profondeur == 0 or tour == limite_tour:
            return [0] * COLONNE_DIM
        #Evalue la situation du jeu à chaque coup
        evaluation = [0] * COLONNE_DIM #créer une liste composé de 0, de longueur = au nb de colonne (nb de possibilités)
        for colonneCoupUn in range(COLONNE_DIM):
            simulationGrille = copy.deepcopy(grille) #création d'une copie de la grille pour simuler les coups de l'IA
            if not verif_localisation(simulationGrille, colonneCoupUn): #vérifie si la colonne est encore dispo, si pas dispo continue
                continue
            rangee = prochaine_ligne_vide(simulationGrille, colonneCoupUn)
            jouer_pion(simulationGrille, rangee, colonneCoupUn, pion)
            if verif_victoire(simulationGrille, pion):
                #1 représente 100% de chance de gagner et donc pour une victoire evaluation du coup = 1
                evaluation[colonneCoupUn] = 1
                break #ne calcule pas les coups restants, inutile
            else:
                #Simule le coup du joueur et détermine son coup optimal (on suppose que le joueur humain joue de façon optimale à chaque fois)
                if tour == limite_tour:
                    evaluation[colonneCoupUn] = 0
                else:
                    for repColonneJoueur in range(COLONNE_DIM):
                        simulationGrille2 = copy.deepcopy(simulationGrille) #copie de la grille de simulation pour simuler le coup du joueur pour chaque coup de l'IA possible
                        if not verif_localisation(simulationGrille2, repColonneJoueur):
                            continue
                        rangee = prochaine_ligne_vide(simulationGrille2, repColonneJoueur)
                        jouer_pion(simulationGrille2, rangee, repColonneJoueur, 1)
                        if verif_victoire(simulationGrille2, 1):
                            #si le joueur gagne, c'est 100% de chance de perdre pour l'IA et donc -1 est la pire probabilité de gagner pour l'IA
                            evaluation[colonneCoupUn] = -1
                            break #ne calcule pas les coups restants, inutile
                        else:
                            #sinon, on continue jusqu'à trouver les possibilités de coup pour l'IA (on continue à évaluer tout en descendant dans l'arbre en profondeur)
                            resultats = Evaluation(simulationGrille2, pion, profondeur - 1)
                            # print(results)
                            evaluation[colonneCoupUn] += (sum(resultats) / COLONNE_DIM) / COLONNE_DIM #ajoute la probabilité de gagner/perdre dans la liste en fonction de la colonne jouée (len liste = 7)
                            
        return evaluation

######################################################### INITIALISATION #########################################################################
    
    game_over = False
    tour = random.randint(1, 2) #le joueur qui commence n'est pas toujours le joueur rouge !
    #grille composée de 42 cases donc maximum 42 tours, +1 pour laisser jouer le 42ème tour si c'est le joueur rouge qui commence, +2 si c'est le jaune car aquiletour détermine en fonction de la parité
    if tour == 1:
        limite_tour = (RANGEE_DIM*COLONNE_DIM)+1
    else:
        limite_tour = (RANGEE_DIM*COLONNE_DIM)+2
    pygame.init()

    #dimensions grille pygame
    dim_pion = 80
    dim_hauteur = (RANGEE_DIM+1) * dim_pion  # +1 pour laisser de la place au pion à jouer
    dim_largeur = COLONNE_DIM * dim_pion 
    dimension = (dim_hauteur, dim_largeur) #dimension de la grille HAUTEUR x LARGEUR
    
    #dimension cercle (pour le pion)
    rayon = int(dim_pion/2.1)


    #création de la grille 
    grille = init_grille() #créer la matrice nulle 
    #print_grille(grille) #pivote la matrice de 180°
    affichage = pygame.display.set_mode(dimension)
    creation_grille(grille) #créer le décor du jeu
    pygame.display.update()


############################################################# LE JEU ###############################################################################

    while not game_over :
        if choix_jeu == 0: #1v1
            J1vJ2 = True
            #A qui de jouer
            pion = a_qui_le_tour(tour)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: #si le joueur click sur la croix de la fenêtre alors le jeu se termine
                    game_over = True
                    
                if event.type == pygame.MOUSEMOTION: #si souris en mouvement
                    pygame.draw.rect(affichage, BLANC, (0,0,dim_largeur,dim_pion)) #créer une marge blanche par dessus la position du pion précédent la position de la souris
                    posX = event.pos[0] #récupère la position de la souris dans l'axe des abscisses
                    posY = int(dim_pion/2)
                    if pion == 1 :
                        pygame.draw.circle(affichage, ROUGE,(posX, posY),rayon)
                    elif pion == 2 :
                        pygame.draw.circle(affichage, JAUNE,(posX, posY),rayon)
                    pygame.display.update() #a chaque fois que la souris se déplace dans la fenetre, pygame actualise la position du pion à jouer dans la marge
                    
                    
                if event.type == pygame.MOUSEBUTTONDOWN: #si click gauche
                    pygame.draw.rect(affichage, BLANC, (0,0,dim_largeur,dim_pion)) #créer une marge blanche pour faire penser que le pion est tombé dans la grille
                    colonne = int(event.pos[0]/dim_pion) #récupère la valeur entière de la colonne à jouer suivant la position de la souris au click 

                    if tour != limite_tour : #si il reste encore de la place dans la grille (car si 42 cases alors 42 tours maximum)
                        if verif_localisation(grille, colonne):
                            rangee = prochaine_ligne_vide(grille, colonne) #prend la valeur de la rangée libre suivant la colone choisie
                            jouer_pion(grille, rangee, colonne, pion) #mise a jour de la matrice
                            maj_grille(grille) #mise a jour de la fenetre de jeu

                            if verif_victoire(grille, pion) : #Si une condition de victoire est respectée par un joueur
                                myfont = pygame.font.SysFont("monospace", 40)
                                if pion == 1 :
                                    compteur_vic_J1 += 1 #compte le nombre de fois que le joueur 2 gagne
                                    titre = myfont.render(pseudo_rouge + ' gagne ! ', 1, NOIR)
                                    affichage.blit(titre, (20,20))
                                elif pion == 2 :
                                    compteur_vic_J2 += 1 #compte le nombre de fois que le joueur 2 gagne
                                    titre = myfont.render(pseudo_jaune + ' gagne ! ', 1, NOIR)
                                    affichage.blit(titre, (20,20))
                                pygame.display.update()
                                scores = easygui.msgbox(msg=pseudo_rouge + ' | ' + str(compteur_vic_J1) + '-'  + str(compteur_vic_J2) + ' | ' + pseudo_jaune, title='Table des scores', ok_button='Continuer')
                                game_over = True
                            tour += 1
                        pygame.display.update()

                    else: #si le jeu se termine sans conditions de victoire, alors match nul
                        myfont = pygame.font.SysFont("monospace", 40)
                        titre = myfont.render("Match nul !", 1, NOIR)
                        affichage.blit(titre, (160,20))
                        pygame.display.update()
                        scores = easygui.msgbox(msg=pseudo_rouge + ' | ' + str(compteur_vic_J1) + '-'  + str(compteur_vic_J2) + ' | ' + pseudo_jaune, title='Table des scores', ok_button='Continuer')
                        game_over = True                
                         

        else : #1vIA
            J1vJ2 = False
            #A qui de jouer
            pion = a_qui_le_tour(tour)
            if pion == 1: #tour de l'humain
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = True

                    if event.type == pygame.MOUSEMOTION: #si souris en mouvement
                        pygame.draw.rect(affichage, BLANC, (0,0,dim_largeur,dim_pion))
                        posX = event.pos[0]
                        posY = int(dim_pion/2)
                        pygame.draw.circle(affichage, ROUGE,(posX, posY),rayon)
                        pygame.display.update()
                                
                    if event.type == pygame.MOUSEBUTTONDOWN: #si click gauche
                        pygame.draw.rect(affichage, BLANC, (0,0,dim_largeur,dim_pion))
                        colonne = int(event.pos[0]/dim_pion)

                        if tour != limite_tour:
                            if verif_localisation(grille, colonne):
                                rangee = prochaine_ligne_vide(grille, colonne)
                                jouer_pion(grille, rangee, colonne, pion)
                                maj_grille(grille)

                                if verif_victoire(grille, pion) :
                                    compteur_vic_J1vIA += 1 #compte le nombre de fois que le joueur gagne contre l'IA
                                    myfont = pygame.font.SysFont("monospace", 40)
                                    titre = myfont.render("Vous avez gagné !", 1, NOIR)
                                    affichage.blit(titre, (80,20))
                                    pygame.display.update()
                                    scores = easygui.msgbox(msg= 'Joueur Rouge | ' + str(compteur_vic_J1vIA) + '-' + str(compteur_vic_IA) +' | IA', title='Table des scores', ok_button='Continuer')
                                    game_over = True
                                tour += 1
                            pygame.display.update()

                        else:
                            myfont = pygame.font.SysFont("monospace", 40)
                            titre = myfont.render("Match nul !", 1, NOIR)
                            affichage.blit(titre, (160,20))
                            pygame.display.update()
                            scores = easygui.msgbox(msg= 'Joueur Rouge | ' + str(compteur_vic_J1vIA) + '-'  + str(compteur_vic_IA) +' | IA', title='Table des scores', ok_button='Continuer')
                            
            else: #tour de l'IA
                if tour != limite_tour:
                    colonne = CoupIA(grille)
                    if verif_localisation(grille, colonne): #après avoir déclanché le move via la récup de la colonne via le CoupIA
                        rangee = prochaine_ligne_vide(grille, colonne)
                        jouer_pion(grille, rangee, colonne, pion)
                        maj_grille(grille)
                        if verif_victoire(grille, pion) :
                                compteur_vic_IA += 1 #compte le nombre de fois que l'IA gagne
                                myfont = pygame.font.SysFont("monospace", 40)
                                titre = myfont.render("L'IA vous a vaincu", 1, NOIR)
                                affichage.blit(titre, (70,20))
                                pygame.display.update()
                                scores = easygui.msgbox(msg= 'Joueur Rouge | ' + str(compteur_vic_J1vIA) + '-' + str(compteur_vic_IA) +' | IA', title='Table des scores', ok_button='Continuer')
                                game_over = True
                        tour += 1
                else:
                    myfont = pygame.font.SysFont("monospace", 40)
                    titre = myfont.render("Match nul !", 1, NOIR)
                    affichage.blit(titre, (160,20))
                    pygame.display.update()
                    scores = easygui.msgbox(msg= 'Joueur Rouge | ' + str(compteur_vic_J1vIA) + '-'  + str(compteur_vic_IA) +' | IA', title='Table des scores', ok_button='Continuer')
                    game_over = True 
    # Lorsque le jeu se termine, une invite de commande propose de rejouer ou de quitter définitevement
    quitter = easygui.indexbox(msg=" Voulez-vous rejouer?", choices=("Rejouer", "Menu", "Quitter"))
    if quitter == 2: #le jeu se ferme définitivement
        continuer = False
        pygame.quit()
    else :
        rejouer = True #condition permettant d'éviter de redemandé la saisie des pseudos