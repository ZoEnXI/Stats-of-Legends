from flask import Flask, render_template, request, url_for
import sqlite3 as sql
from riotwatcher import LolWatcher, ApiError
import pandas as pd

app = Flask(__name__)

# Page principale

@app.route('/')
def index():
    return render_template('index.html')

# Page d'Inscription

@app.route('/')
def deconnexion():
    return render_template('index.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

# Enregistrement dans la base de donnée + Confirmation des mots de passe + Affichage du message d'échec ou de réussite
@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    msg = ""

    if request.method == 'POST':
        try:
            # Intérieur de la table : joueurs
            pseudo = request.form['pseudo']
            password = request.form['password']
            password_2 = request.form['password_2']
            region = request.form['region']

            # Condition pour la vérification des mots de passes
            if password == password_2:
                # Ecriture dans la base de donnée .db si jamais le mdp est égale à la cdmdp
                with sql.connect("database/database.db") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO joueurs (pseudo,password, password_2, region) VALUES (?,?,?,?)", (
                        pseudo, password, password_2, region))
                    con.commit()
                    # Message dans result.html
                    msg = "Vous avez bien été enregistré dans notre base de donnée"
            # Si mdp != cdmdp :
            else:
                # Message dans result.html
                msg = "Erreur lors de votre enregistrement: veuillez vérifier que les mots de passe soient similaires"
                con.rollback()
        finally:
            # HTML qui affiche le message
            return render_template("result.html", msg=msg)
            con.close()

# Page de Connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


# Page de Connection

@app.route('/connection', methods=['POST'])
def connection():
    # Définition du message du result.html
    msg = ''

    pseudo = request.form['pseudo']
    password = request.form['password']
    region = request.form['region']

    print(region)

    # Connexion à la base de donnée
    with sql.connect("database/database.db") as con:
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM joueurs WHERE pseudo=? AND password=? AND region=?", (pseudo, password, region))
        info = cur.fetchone()
        # Si info n'est pas égale à None
        if info != None:
            # Si pseudo(dans db) = pseudo entré et que mot de passe(dans db) = mot de passe entré
            if info[0] == pseudo and info[1] == password and info[3] == region:
                
                a = info[0]

                # Clé permettant d'acceder à l'API de Riot Games
                api_key = 'RGAPI-6f5fac6c-c6af-4042-98e1-475ba357fc76'
                watcher = LolWatcher(api_key)

                # Choix du serveur + conversion du nom du serveur en miniscule 
                if info[3] == "EUW1":
                    my_region = "euw1"

                if info[3] == "NA1":
                    my_region = "na1"

                if info[3] == "BR1":
                    my_region = "br1"

                if info[3] == "EUN1":
                    my_region = "eun1"
                
                if info[3] == "JP1":
                    my_region = "jp1"
                
                if info[3] == "KR":
                    my_region = "kr"

                if info[3] == "LA1":
                    my_region = "la1"

                if info[3] == "LA2":
                    my_region = "la2"     

                if info[3] == "OC1":
                    my_region = "oc1"    

                if info[3] == "TR1":
                    my_region = "tr1"

                if info[3] == "RU":
                    my_region = "ru" 

                #  Entrée du pseudo permettant d'acceder au stats
                me = watcher.summoner.by_name(my_region, a)

                # Acquisition des stats globales sur le joueur
                my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])

                # Accès à la liste de matches du joueur
                my_matches = watcher.match.matchlist_by_account(my_region, me['accountId'])

                # Accès aux stats du dernier match joué
                last_match = my_matches['matches'][0]
                match_detail = watcher.match.by_id(my_region, last_match['gameId'])

                # Création d'un premier dictionnaire comporatant diverses stats 
                participants = []
                for row in match_detail['participants']:
                    participants_row = {}
                    participants_row['champion'] = row['championId']
                    participants_row['RoleTemp'] = row['timeline']['lane']
                    participants_row['Role'] = row['timeline']['role']
                    participants_row['VD'] = row['stats']['win']
                    participants_row['Kills'] = row['stats']['kills']
                    participants_row['Deaths'] = row['stats']['deaths']
                    participants_row['Assists'] = row['stats']['assists']
                    participants_row['Niveau'] = row['stats']['champLevel']
                    participants_row['CS'] = row['stats']['totalMinionsKilled']
                    participants_row['Gold total'] = row['stats']['goldEarned']
                    participants_row['Dégats total'] = row['stats']['totalDamageDealt']
                    participants_row['Score de vision'] = row['stats']['visionScore']
                    participants.append(participants_row)

                # Vérification de la version de League of Legends
                latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']

                # Acquisition de la liste de champion
                static_champ_list = watcher.data_dragon.champions(latest, False, 'fr_FR')

                # Les champions sont nommé par des numéros, ceci permet d'afficher leur nom en lettre 
                champ_dict = {}
                for key in static_champ_list['data']:
                    row = static_champ_list['data'][key]
                    champ_dict[row['key']] = row['id']
                for row in participants:
                    (str(row['champion']) + ' ' + champ_dict[str(row['champion'])])
                    row['Champion'] = champ_dict[str(row['champion'])]

                # Obtention des noms des joueurs dans un dictionnaire
                Summoner_name = []
                for row in match_detail['participantIdentities']:
                    Summoner_name_row = {}
                    Summoner_name_row['Joueur'] = row['player']['summonerName']
                    Summoner_name.append(Summoner_name_row)

                # Création de deux tableaux
                df = pd.DataFrame(participants)
                df2 = pd.DataFrame(Summoner_name)

                # supprime les numero de manière a ce que l'on voit uniquement le nom des champion.
                df.pop('champion')

                # remplace les True par victoire et False par défaite
                df.loc[df.VD == True, 'VD'] = 'Victoire'
                df.loc[df.VD == False, 'VD'] = 'Défaite'

                # fusion des deux tableau + nom des Role
                df3 = pd.merge(df2, df, left_index=True, right_index=True)
                df3 = df3[['Joueur', 'Champion', 'RoleTemp', 'Role', 'VD', 'Kills',
                            'Deaths', 'Assists', 'Niveau', 'CS', 'Gold total', 'Dégats total']]


                # On renomme et attribut les roles + modification des noms de champions posant problèmes
                df3.loc[df3.Role == 'DUO_SUPPORT', 'Role'] = 'SUPPORT'
                df3.loc[df3.Role == 'DUO_CARRY', 'Role'] = 'AD CARRY'
                df3.loc[df3.Role == 'NONE', 'Role'] = 'JUNGLE'
                df3.loc[df3.RoleTemp == 'TOP', 'Role'] = 'TOPLANER'
                df3.loc[df3.RoleTemp == 'MIDDLE', 'Role'] = 'MIDLANER'
                df3.loc[df3.RoleTemp == 'NONE', 'VD'] = 'ABANDON'

                df3.loc[df3.Champion == 'MonkeyKing', 'Champion'] = 'Wukong'
                df3.loc[df3.Champion == 'MissFortune', 'Champion'] = 'Miss Fortune'
                df3.loc[df3.Champion == 'AurelionSol', 'Champion'] = 'Aurelion Sol'
                df3.loc[df3.Champion == 'JarvanIV', 'Champion'] = 'Jarvan IV'
                df3.loc[df3.Champion == 'LeeSin', 'Champion'] = 'Lee Sin'
                df3.loc[df3.Champion == 'MasterYi', 'Champion'] = 'Maître Yi'
                df3.loc[df3.Champion == 'DrMundo', 'Champion'] = 'DR. Mundo'
                df3.loc[df3.Champion == 'Chogath', 'Champion'] = "Cho'gath"
                df3.loc[df3.Champion == 'Kaisa', 'Champion'] = "Kai'sa"
                df3.loc[df3.Champion == 'Khazix', 'Champion'] = "Kha'zix"
                df3.loc[df3.Champion == 'Kogmaw', 'Champion'] = "Kog'maw"
                df3.loc[df3.Champion == 'Nunu', 'Champion'] = "Nunu et Willump"
                df3.loc[df3.Champion == 'Reksai', 'Champion'] = "Rek'sai"
                df3.loc[df3.Champion == 'TahmKench', 'Champion'] = "Tahm Kench"
                df3.loc[df3.Champion == 'TwistedFate', 'Champion'] = "Twisted Fate"
                df3.loc[df3.Champion == 'Velkoz', 'Champion'] = "Vel'koz"
                df3.loc[df3.Champion == 'XinZhao', 'Champion'] = "Xin Zhao"
                df3.loc[df3.Champion == 'Zoe', 'Champion'] = "Zoé"
                df3.loc[df3.Champion == 'Seraphine', 'Champion'] = "Séraphine"

                #Suppression de role Temp qui permet d'avoir plus de précision quand au roles joué par le joueur
                df3.pop('RoleTemp')

                # Création du tableau des stats de classement 
                df4 = pd.DataFrame(my_ranked_stats)
                
                # On renomme certains éléments 
                df4.loc[df4.inactive == True, 'inactive'] = 'Inactif'
                df4.loc[df4.inactive == False, 'inactive'] = 'Actif'

                df4.loc[df4.hotStreak == True, 'hotStreak'] = 'Oui'
                df4.loc[df4.hotStreak == False, 'hotStreak'] = 'Non'

                df4.rename({'tier': 'Tier', 'rank': 'Rang', 'summonerName': 'Joueur', 'leaguePoints': 'LP', 'wins': 'Victoire',
                            'losses': 'Défaite', 'inactive': 'Activité', 'hotStreak': 'Série de victoire'}, axis=1, inplace=True)
                
                #Supression de ce qui ne nous intéresse pas 
                df4.pop('leagueId')
                df4.pop('queueType')
                df4.pop('summonerId')
                df4.pop('veteran')
                df4.pop('freshBlood')
                df4.drop(df.index[:0], inplace=True)

                # Affichage des tableaus  dans le terminal
                print(df3)
                print(df4)

                
                # Codes HTML qui sera utilisé lors de la conversion des tableau pandas en fichier HTML 

                pd.set_option('colheader_justify', 'center')

                html_string = '''
                <html>
                    <head><title>HTML Pandas Dataframe with CSS</title></head>
                    <link rel="stylesheet" type="text/css" href="../static/df_style.css"/> 
                    <body>
                    {table}
                    </body>
                </html>
                '''

                html_string2 = '''
                <html>
                    <head><title>HTML Pandas Dataframe with CSS</title></head>
                    <link rel="stylesheet" type="text/css" href="../static/df_style2.css"/>
                    <body>
                    {table}
                    </body>
                </html>
                '''

                # Conversion des tableau panda en fichiers HTML
                with open(r'../SITE/templates/match.html', 'w', encoding="utf-8") as f:
                    f.write(html_string.format(table=df3.to_html(classes='mystyle', index=False)))

                with open(r'../SITE/templates/stats.html', 'w', encoding="utf-8") as f:
                    f.write(html_string2.format(table=df4.to_html(classes='mystyle', index=False)))

                # Redirection sur indexconnect
                stats = url_for('stats')
                match = url_for('match')
                return render_template('indexconnect.html', iframe=stats, iframe2 =match)
            else:
                return render_template('login.html')
        else:
            con.commit()
            return render_template('signup.html')


@app.route('/connection/stats')
def stats():
    return render_template('stats.html')

@app.route('/connection/match')
def match():
    return render_template('match.html')
    
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
