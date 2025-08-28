import pandas as pd
import sasoptpy as so 
import requests
import os 
import time 
from subprocess import Popen, DEVNULL
from concurrent.futures import ProcessPoolExecutor


def get_data(team_id):
    r = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    fpl_data = r.json()
    element_data = pd.DataFrame(fpl_data['elements'])
    team_data = pd.DataFrame(fpl_data['teams'])
    elements_team = pd.merge(element_data, team_data, left_on= 'team',right_on = 'id')
    player_stats = pd.read_csv("../data/fplreview.csv")
    player_info = pd.read_csv("../data/players.csv")
    team_info = pd.read_csv("../data/teams.csv")

    r = request.get(f'https://fantasy.premierleague.com/api/entry/{team_id}/event/{gw}/picks/')
    picks_data = r.json() #converts a json data to a python variable 
    initial_squad = [o['element'] for i in picks_data['picks']]

    merged_players = pd.merge(
        player_stats,
        player_info,
        left_on='id',
        right_on='player_id',
        how='left'
    )

    review_data = pd.merge(
        merged_players,
        team_info,
        left_on='team_code',
        right_on='code',
        how='left'
    )
    merged_data = pd.merge(elements_team, review_data, left_on=['name', 'web_name'], right_on=['name', 'web_name'])
    merged_data.set_index(['id_x_x'], inplace=True)
    next_gw = int(review_data['gw'].iloc[0] + 1)
    type_data = pd.DataFrame(fpl_data['element_types']).set_index(['id'])
    return {
        'merged_data': merged_data,
        'team_data': team_data,
        'next_gw': next_gw,
        'type_data': type_data,
        'initial_squad': initial_squad,
    }

def solve_multi_period_fpl(team_id, gw, ft, itb, horizon, objective, decay_base=0.84): #team id, gameweek, free transfers, in the bank, how many gameweeks to look ahead, objective, how you penalise future game weeks
    
    #data 
    problem_name = f'mp_b{itb}_h{horizon}_i{objective[0]}_d{decay_base}'
    data = get_data(team_id)
    merged_data = data['merged_data']
    team_data = data['team_data']
    next_gw = data['next_gw']
    type_data = data['type_data']
    initial_squad = data['initial_squad']

    #sets
    players = merged_data.index.to_list()
    element_types = type_data.index.to_list()
    teams = team_data['name'].to_list()
    gameweeks = list(range(next_gw, next_gw + horizon))
    all_gw = [next_gw-1] + gameweeks 

    #variables
    model = so.Model(name=problem_name)
    squad = model.add_variables(players, all_gw, name='squad', vartype = so.binary)
    lineup = model.add_variables(players, gameweeks, name='lineup', vartype = so.binary)
    captain = model.add_variables(players,gameweeks,  name='captain', vartype = so.binary)
    vicecap = model.add_variables(players, gameweeks, name='vicecap', vartype = so.binary)
    tranfer_in = model.add_variable(players, ameweeks, name='tranfer_in', vartype='binary')
    tranfer_out = model.add_variable(players, gameweeks, name='tranfer_iut', vartype='binary')
    in_the_bank = model.add_variables(all_gw, name = 'itb', vartype=so.continuous,lb=0) #how much is in the bank
    free_tranfers = model.add_variables(all_gw, name='ft', vartype=so.integer, lb=1, up=2) #upper bound now needs to change to 5 (CHANGE)
    penalized_tranfers = model.add_variable(gameweeks,name='pt',vartype=so.integer,lb=0)
    aux=model.add_variables(gameweeks, name='aux',vartype=so.binary)

    #dinctionaries 
    lineup_type_count = {(t,w): so.expr_sum(lineup[p,w] for p in players if merged_data.loc[p,'element_type'] == t) for t in element_types for w in gameweeks}
    squad_type_count = {(t,w): so.expr_sum(squad[p,w] for p in players if merged_data.loc[p,'element_type'] == t) for t in element_types for w in gameweeks}
    player_price = (merged_data['now_cost_x']/10).to_dict()
    sold_amount = {w: so.expr_sum(player_price[p] * tranfer_out[p,w]) for w in gameweeks}
    bought_amount = {w: so.expr_sum(player_price[p] * tranfer_in[p,w]) for w in gameweeks}
    points_player_week= {(p,w): merged_data.loc[p, f'{w}_pts'] for p in players for w in gameweeks} #the f string mathces the data formula with the expected points 
    squad_count = {w:so.expr_sum(squad[p,w] for p in players) for w in gameweeks} #create a dictionary with each players points for every gameweek
    number_of_tranfers = {w:so.expr_sum(transfer_out[p,w] for p in players) for w in gameweeks}
    number_of_tranfers[next_gw-1] = 1 #might have to change this too (CHANGE)
    tranfer_diff = {w: number_of_tranfers[w] - free_tranfers[w] for w in gameweeks}

    #intial conditions
    model.add_constraints((squad[p, next_gw-1] ==1 for p in initial_squad), name = 'initial_squad_players')
    model.add_constraints((squad[p, next_gw-1] ==0 for p in players if p not in initial_squad), name = 'initial_squad_others')
    model.add_constraint(in_the_bank[next_gw-1] == itb, name= 'initial_itb')
    model.add_constraint(free_tranfer[next_gw-1] == ft, name='initial_ft')

    #Constraints
    
    model.add_constraints((squad_count[w] == 15 for w in gameweeks), name='squad_count') #we added a gameweek dimension to each of these constraints/(s) [plural now] 
    model.add_constraints((so.expr_sum(lineup[p,w] for p in players) == 11 for w in gameweeks), name='lineup_count') 
    model.add_constraints((so.expr_sum(captain[p, w] for p in players) == 1 for w in gameweeks), name='captain_count')
    model.add_constraints((so.expr_sum(vicecap[p, w] for p in players) == 1 for w in gameweeks), name='vicecap_count')
    model.add_constraints((lineup[p, w] <= squad[p, w] for p in players for w in gameweeks), name='lineup_squad_rel')
    model.add_constraints((captain[p, w] <= lineup[p, w] for p in players for w in gameweeks), name='captain_lineup_rel')
    model.add_constraints((vicecap[p, w] <= lineup[p, w] for p in players for w in gameweeks), name='vicecap_lineup_rel')
    model.add_constraints((captain[p, w] + vicecap[p, w] <= 1 for p in players for w in gameweeks), name='cap_vc_rel')

    lineup_type_count = {t: so.expr_sum(lineup[p] for p in players if merged_data.loc[p,'element_type'] == t) for t in element_types}
    squad_type_count = {t: so.expr_sum(squad[p] for p in players if merged_data.loc[p,'element_type'] == t) for t in element_types}

    model.add_constraints((lineup_type_count[t,w] == [type_data.loc[t, 'squad_min_play'], type_data.loc[t, 'squad_max_play']] for t in element_types for w in gameweeks), name='valid_formation')
    model.add_constraints((squad_type_count[t,w] == type_data.loc[t, 'squad_select'] for t in element_types for w in gameweeks), name='valid_squad')
    model.add_constraints((so.expr_sum(squad[p,w] for p in players if merged_data.loc[p,'name'] == t) <=3 for t in teams for w in gameweeks), name = 'team_limit')
    
    ## Tranfer constraints 
    model.add_constraints((squad[p,w] == squad[p,w-1] + tranfer_in[p,w] - tranfer_out[p,w] for p in players for w in gameweeks), name ='squad_tranfer_relation')
    model.add_constraints((in_the_bank[w] == in_the_bank[w-1] + sold_amount[w] - bought_amount[w] for w in gameweeks), name='cont_budget')

    ## Free tranfer constraints 
    model.add_constraints((free_tranfers[w] == aux[w]+1 for w in gameweeks), name='aux_ft_rel')
    model.add_constraints((free_tranfers[w-1] - number_of_tranfers[w-1] <= 2*aux[2] for w in gameweeks), name='focre_aux_1')
    model.add_constraints((free_tranfers[w-1] - number_of_tranfers[w-1] >= aux[w] + (14)*(1-aux[w]) for w in gameweeks), name='force_aux_2')
    model.add_constraints((penalized_tranfers[w] >= tranfer_diff[w] for w in gameweeks), name = 'pen_tranfer_rel')



    total_points = so.expr_sum(float(merged_data.loc[p, 'ep_next_x'] or 0.0) * (lineup[p] + captain[p] + 0.1 * vicecap[p])for p in players)
    model.set_objective(-total_points, sense='N', name='total_xp')
    model.export_mps(f'single_period_{budget}.mps')
    command = f'cbc single_period.mps -solve -solu solutution_sp_{budget}.txt'
    Popen(command, shell=True, stdout=DEVNULL).wait()
    #os.system(command)
    for v in model.get_variables():
        v.set_value(0)
    skipped = False
    with open(f'solutution_sp_{budget}.txt', 'r') as f:
        for line in f:
            if 'objective_value' in line:
                continue
            words = line.split()
            var = model.get_variable(words[1])
            if var is None and not skipped:
                skipped = True
                continue
            var.set_value(float(words[2]))
    
    picks = []
    for p in players:
        if squad[p].get_value() > 0.5:
            lp = merged_data.loc[p]
            print(lp['web_name'])
            is_captain = 1 if captain[p].get_value() >0.5 else 0
            is_lineup = 1 if lineup[p].get_value() >0.5 else 0
            is_vice = 1 if vicecap[p].get_value() >0.5 else 0
            position = type_data.loc[lp['element_type'], 'singular_name_short']
            picks.append([
                lp['web_name'],
                position,
                lp['element_type'],
                lp['name'],
                lp['now_cost_x']/10,
                lp['ep_next_x'], #this is dodgey
                is_lineup,
                is_captain,
                is_vice,
                ])

    picks_df = pd.DataFrame(picks, columns = ['name', 'pos','type','team','price','xp','lineup','captain','vicecap']).sort_values(by=['lineup','type','xp'], ascending=[False, True, False])

    total_xp = so.expr_sum( (lineup[p] + captain[p]) * float(merged_data.loc[p, 'ep_next_x']) for p in players).get_value()
    print(f'Total expected value for budget {budget}: {total_xp}')
    return { 'model':model, 'picks':picks_df, 'total_xp':total_xp}

if __name__ == "__main__":
   
    t0 = time.time()
    get_data()  # Load data once to cache it
    budget = list(range(80,121,5))
    with ProcessPoolExecutor(max_workers=16) as execturor:
        responses = execturor.map(solve_single_period_fpl, budget)
        all_xp_values = [r['total_xp'] for r in responses]
    results = zip(budget, all_xp_values)
    df = pd.DataFrame(results, columns=['budget', 'xp'])
    print(df)
    print(time.time() - t0, 'spent in the loop')


    pass