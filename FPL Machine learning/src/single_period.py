import pandas as pd
import sasoptpy as so 
import requests
import os 
import time 
from subprocess import Popen, DEVNULL
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache

@lru_cache(maxsize=1)
def get_data():
    r = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    fpl_data = r.json()
    element_data = pd.DataFrame(fpl_data['elements'])
    team_data = pd.DataFrame(fpl_data['teams'])
    elements_team = pd.merge(element_data, team_data, left_on= 'team',right_on = 'id')
    player_stats = pd.read_csv("../data/fplreview.csv")
    player_info = pd.read_csv("../data/players.csv")
    team_info = pd.read_csv("../data/teams.csv")


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
    }

def solve_single_period_fpl(budget):
    data = get_data()
    merged_data = data['merged_data']
    team_data = data['team_data']
    next_gw = data['next_gw']
    type_data = data['type_data']

    players = merged_data.index.to_list()
    element_types = type_data.index.to_list()
    teams = team_data['name'].to_list()

    model = so.Model(name='single_period')
    squad = model.add_variables(players, name='squad', vartype = so.binary)
    lineup = model.add_variables(players, name='lineup', vartype = so.binary)
    captain = model.add_variables(players, name='captain', vartype = so.binary)
    vicecap = model.add_variables(players, name='vicecap', vartype = so.binary)

    #constraints
    squad_count = so.expr_sum(squad[p] for p in players) 
    model.add_constraint((squad_count == 15), name='squad_count')
    model.add_constraint(so.expr_sum(lineup[p] for p in players) == 11, name='lineup_count')
    model.add_constraint(so.expr_sum(captain[p] for p in players) == 1, name='captain_count')
    model.add_constraint(so.expr_sum(vicecap[p] for p in players) == 1, name='vicecap_count')
    model.add_constraints((lineup[p] <= squad[p] for p in players), name='lineup_squad_rel')
    model.add_constraints((captain[p] <= lineup[p] for p in players), name='captain_lineup_rel')
    model.add_constraints((vicecap[p] <= lineup[p] for p in players), name='vicecap_lineup_rel')
    model.add_constraints((captain[p] + vicecap[p] <= 1 for p in players), name='cap_vc_rel');

    lineup_type_count = {t: so.expr_sum(lineup[p] for p in players if merged_data.loc[p,'element_type'] == t) for t in element_types}
    squad_type_count = {t: so.expr_sum(squad[p] for p in players if merged_data.loc[p,'element_type'] == t) for t in element_types}
    model.add_constraints((lineup_type_count[t] == [type_data.loc[t, 'squad_min_play'], type_data.loc[t, 'squad_max_play']] for t in element_types), name='valid_formation')
    model.add_constraints((squad_type_count[t] == type_data.loc[t, 'squad_select'] for t in element_types), name='valid_squad')
    price = so.expr_sum(merged_data.loc[p, 'now_cost_x']/10 * squad[p] for p in players)
    model.add_constraint(price <= budget, name = 'budget_limit')
    model.add_constraints((so.expr_sum(squad[p] for p in players if merged_data.loc[p,'name'] == t) <=3 for t in teams), name = 'team_limit')
    total_points = so.expr_sum(float(merged_data.loc[p, 'ep_next_x'] or 0.0) * (lineup[p] + captain[p] + 0.1 * vicecap[p])for p in players)

    model.set_objective(-total_points, sense='N', name='total_xp');
    model.export_mps(f'single_period_{budget}.mps')
    command = f'cbc single_period_{budget}.mps -solve -solu solutution_sp_{budget}.txt'
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


'''
    t0 = time.time()
    results = []
    for budget in range(80, 120,5):
        r = solve_single_period_fpl(budget=budget)
        results.append([budget, r['total_xp']])
    df = pd.DataFrame(results, columns=['budget', 'total_xp'])
    print(df)
    print(time.time() - t0, 'spent in the loop')
'''