# 4ESGI_Python_BlockChain
Mini Blockchain en Python + Flask

Bienvenue dans Mini Blockchain Web, une application pédagogique construite avec Python, Flask et 0 dépendances externes (sauf requests, hashlib, time).
Ce projet te permet de visualiser, manipuler et simuler le fonctionnement d'une blockchain, y compris des attaques et la synchronisation entre nœuds

Fonctionnalités
 - Preuve de travail avec difficulté ajustable
 - Ajout de transactions manuelles
 - Minage de blocs avec transactions
 - Simulation d’une attaque 51%
 - Réinitialisation de la chaîne
 - Ajout et synchronisation entre nœuds
 - Détection automatique des chaînes corrompues
 - Graphique de croissance de la chaîne via Chart.js


    Exemples de tests pour chaque bouton sur l'interface Web
   
|:Bouton| 	                                           |Action:|
|:Ajouter transaction|                            |Entrer "Alice" ➜ "Bob" et valider. La transaction "Alice -> Bob" est ajoutée au pool:|
|:Miner|	                                          |Mine un bloc avec les transactions du pool (ou "System -> Miner" si vide):|
|:Attaque 51%	                                    |Modifie manuellement le contenu du dernier bloc. Le hash devient invalide ➜ chaîne détectée comme corrompue:|
|:Réinitialiser|	                                  |Réinitialise la blockchain (supprime tous les blocs sauf le Genesis):|
|:Ajouter nœud|	                                    |Dans l’instance 5000, entrer http://127.0.0.1:5001 pour ajouter un autre nœud:|
|:Synchroniser avec pairs|	                        |L’instance 5000 compare sa chaîne à celle du nœud pair et la remplace si celle du pair est plus longue ET valide:|

Blockchain
 - Block : objet contenant transactions, hash, timestamp, Merkle root, etc.

 - Blockchain : liste des blocs + logique de minage, validation, remplacement.

Flask Routes
 - / : page HTML principale avec formulaire, graphique, et liste des blocs

 - /add_transaction : ajoute une transaction au pool

 - /mine : mine un bloc

 - /attack : simule une attaque 51%

 - /reset : réinitialise toute la chaîne

 - /register_node : ajoute un nœud pair

 - /sync : tente de synchroniser avec les pairs
