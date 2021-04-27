#Import des modules 
from riotwatcher import LolWatcher, ApiError
import pandas as pd

#Clé permettant d'acceder à l'API de Riot Games 
api_key = 'RGAPI-6f5fac6c-c6af-4042-98e1-475ba357fc76' 
watcher = LolWatcher(api_key)


class ArbreBinaire:
  
  def __init__(self):

    self.item= None

  def get_data(self):

    #Choix du pseudo permettant d'acceder au stats
    me = watcher.summoner.by_name(my_region, me)                                        

    #Affiche des stats globales sur le joueur 
    my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])

    #Accès à la liste de matches du joueur 
    my_matches = watcher.match.matchlist_by_account(my_region, me['accountId'])

    #Accès aux stats du match souhaité 
    last_match = my_matches['matches'][0]                                                   
    match_detail = watcher.match.by_id(my_region, last_match['gameId'])
    print(match_detail)

    items = []
    for row in match_detail['participants']:       
      items_row = {}
      items_row['Item 1'] = row['stats']['item0']
      items_row['Item 2'] = row['stats']['item1']
      items_row['Item 3'] = row['stats']['item2']
      items_row['Item 4'] = row['stats']['item3']
      items_row['Item 5'] = row['stats']['item4']
      items_row['Item 6'] = row['stats']['item5']
      items.append(items_row)

  def arbre (self, get_data):
    for x in range (items):
      if self.item == None:
        self.item = ArbreBinaire(item(x))
  
  def get_item (self):
    return self.item
  
  def navigation (sefl, arbre):
    a = input("Numero item:")
    a =+ 1
    return self.ArbreBinaire(a)


      
      
      


    
