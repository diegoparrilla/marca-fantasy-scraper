# coding=utf-8
#
#  python3 scraper.py --config CONFIG_FILE.INI
#

import configparser
import datetime
import getopt
import json
import logging
import logging.config
import os
import shutil
import sys
import time
import traceback
from itertools import zip_longest
from os import path

import requests
DEFAULT_CONFIG_FILE = 'etc/conf.ini'
CONFIG_API_SECTION = 'api'
CONFIG_API_PLAYERS_ENDPPOINT = 'players_endpoint'

def current_milli_time(): return int(round(time.time() * 1000))

def write_file_json(logger, name, content):
    logger.debug("Writing content to JSON file: %s" % name)
    f = open(name, 'w', encoding='utf-8')
    json.dump(content, f, indent=4)
    f.close()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            debug = False
            initfile = DEFAULT_CONFIG_FILE
            options, remainder = getopt.getopt(
                argv[1:], 'h:c:d', ['help', 'config=', 'debug'])
            for opt, arg in options:
                if opt in ('-c', '--config'):
                    initfile = arg
                if opt in ('-d', '--debug'):
                    debug = True
                elif opt in ('-h', '--help'):
                    print("python3 scraper.py --config CONFIG_FILE.INI")
                    return 0
        except getopt.error as msg:
            raise Exception(msg)

        logging.config.fileConfig(initfile)
        logging.captureWarnings(True)

        logger_ = logging.getLogger(__name__)

        config = configparser.ConfigParser()
        config.read(initfile)

        if not os.path.exists('laliga'):
            os.makedirs('laliga')

        players_endpoint = config.get(CONFIG_API_SECTION, CONFIG_API_PLAYERS_ENDPPOINT)
        logger_.info('The API endpoint: %s' % players_endpoint)

        player_aggr_content = []
        player_csv_row = 'ID,EQUIPO_ID,PUNTOS,PUNTOS_MEDIA'
        player_csv_row += ',NOMBRE,APODO,SLUG,POSICION_ID'
        player_csv_row += ',POSICION,VALOR_MERCADO,ESTADO_JUGADOR'
        for w in range(1,39):
            player_csv_row += ',SEMANA_%s' % w
        for w in range(1,39):
            player_csv_row += ',SEMANA_%s_AGGR' % w
        player_aggr_content.append(player_csv_row)

        csv_content = []
        csv_row = 'ID,SLUG,EQUIPO_ID,SEMANA,PUNTOS_TOTALES'
        csv_row += ',MIN_JUGADOS,GOLES,ASISTENCIAS_GOL,ASISTENCIAS_SIN_GOL'
        csv_row += ',LLEGADAS_AREA,PENALTIS_PROVOCADOS,PENALTIS_PARADOS,PARADAS'
        csv_row += ',DESPEJES,PENALTIS_FALLADOS,GOLES_EN_PROPIA,GOLES_EN_CONTRA'
        csv_row += ',TARJETAS_AMARILLAS,SEGUNDAS_AMARILLAS,TARJETAS_ROJAS,TIROS_A_PUERTA'
        csv_row += ',REGATES,BALONES_RECUPERADOS,POSESIONES_PERDIDAS,PUNTOS_MARCA'
        csv_row += ',MIN_JUGADOS_PUNTOS,GOLES_PUNTOS,ASISTENCIAS_GOL_PUNTOS,ASISTENCIAS_SIN_GOL_PUNTOS'
        csv_row += ',LLEGADAS_AREA_PUNTOS,PENALTIS_PROVOCADOS_PUNTOS,PENALTIS_PARADOS_PUNTOS,PARADAS_PUNTOS'
        csv_row += ',DESPEJES_PUNTOS,PENALTIS_FALLADOS_PUNTOS,GOLES_EN_PROPIA_PUNTOS,GOLES_EN_CONTRA_PUNTOS'
        csv_row += ',TARJETAS_AMARILLAS_PUNTOS,SEGUNDAS_AMARILLAS_PUNTOS,TARJETAS_ROJAS_PUNTOS,TIROS_A_PUERTA_PUNTOS'
        csv_row += ',REGATES_PUNTOS,BALONES_RECUPERADOS_PUNTOS,POSESIONES_PERDIDAS_PUNTOS,PUNTOS_MARCA_PUNTOS'
        csv_content.append(csv_row)
        for index in range(0,1499):
            response = requests.get('%s/%s' % (players_endpoint,index))
            if response.status_code == 200:
                payload = response.json()
                team_id = payload['team']['id']
                team_shortname = payload['team']['shortName']
                team_folder = 'laliga/%s-%s' % (team_id, team_shortname)
                if not os.path.exists(team_folder):
                    os.makedirs(team_folder)
                player_id = index
                player_slug = payload['slug']
                player_filename = 'laliga/%s-%s/%s-%s.json' % (team_id, team_shortname, player_id, player_slug)
                player_status = payload['playerStatus']
                if player_status != 'out_of_league':
                    f = open(player_filename, 'w', encoding='utf-8')
                    json.dump(payload, f, indent=4)
                    f.close()                
                    logger_.info('Scraped player with id=%s' % index)
                    player_scores = [ 0 for x in range(0,38)]
                    player_scores_aggr = [ 0 for x in range(0,38)]
                    player_aggr = 0
                    for week in payload['playerStats']:
                        stats = week['stats']
                        week_number = week['weekNumber']
                        total_points = week['totalPoints']
                        csv_row = '%s,%s,%s,%s,%s' % (player_id,player_slug,team_shortname,week_number,total_points)
                        csv_row += ',%s,%s,%s,%s' % (stats['mins_played'][0],stats['goals'][0],stats['goal_assist'][0],stats['offtarget_att_assist'][0])
                        csv_row += ',%s,%s,%s,%s' % (stats['pen_area_entries'][0],stats['penalty_won'][0],stats['penalty_save'][0],stats['saves'][0])
                        csv_row += ',%s,%s,%s,%s' % (stats['effective_clearance'][0],stats['penalty_failed'][0],stats['own_goals'][0],stats['goals_conceded'][0])
                        csv_row += ',%s,%s,%s,%s' % (stats['yellow_card'][0],stats['second_yellow_card'][0],stats['red_card'][0],stats['total_scoring_att'][0])
                        csv_row += ',%s,%s,%s,%s' % (stats['won_contest'][0],stats['ball_recovery'][0],stats['poss_lost_all'][0],stats['marca_points'][0])
                        csv_row += ',%s,%s,%s,%s' % (stats['mins_played'][1],stats['goals'][1],stats['goal_assist'][1],stats['offtarget_att_assist'][1])
                        csv_row += ',%s,%s,%s,%s' % (stats['pen_area_entries'][1],stats['penalty_won'][1],stats['penalty_save'][1],stats['saves'][1])
                        csv_row += ',%s,%s,%s,%s' % (stats['effective_clearance'][1],stats['penalty_failed'][1],stats['own_goals'][1],stats['goals_conceded'][1])
                        csv_row += ',%s,%s,%s,%s' % (stats['yellow_card'][1],stats['second_yellow_card'][1],stats['red_card'][1],stats['total_scoring_att'][1])
                        csv_row += ',%s,%s,%s,%s' % (stats['won_contest'][1],stats['ball_recovery'][1],stats['poss_lost_all'][1],stats['marca_points'][1])
                        csv_content.append(csv_row)
                        player_aggr += total_points
                        player_scores[week_number - 1] = total_points               
                        player_scores_aggr[week_number - 1] = player_aggr               
                    player_csv_row = '%s,%s,%s,%s' % (player_id,team_shortname,payload['points'],payload['averagePoints'])
                    player_csv_row += ',"%s","%s",%s,%s' % (payload['name'],payload['nickname'],payload['slug'],payload['positionId'])
                    player_csv_row += ',%s,%s,%s' % (payload['position'],payload['marketValue'],payload['playerStatus'])
                    for w in range(0,38):
                        player_csv_row += ',%s' % player_scores[w]
                    old_player_score = 0
                    for w in range(0,38):
                        new_player_score = old_player_score
                        if player_scores_aggr[w] > 0:
                            new_player_score = player_scores_aggr[w]
                            old_player_score = new_player_score
                        player_csv_row += ',%s' % new_player_score
                    player_aggr_content.append(player_csv_row)
                else:
                    logger_.warning('Player with id=%s not in LaLiga anymore' % index)
            if response.status_code == 404:
                logger_.warn('Player with id=%s not found' % index)
        f = open('laliga/players-performance.csv', 'w', encoding='utf-8')
        for item in csv_content:
            f.write('%s\n' % item)
        f.close()                

        f = open('laliga/players.csv', 'w', encoding='utf-8')
        for item in player_aggr_content:
            f.write('%s\n' % item)
        f.close()                

        sys.exit(1)

        return 0
    except Exception as e:
        traceback.print_exc()
        print("ERROR: ", e)
        print("For help, use --help")
        return 2


if __name__ == "__main__":
    sys.exit(main())
