import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import json

fp = "need to read in fp for polarities"
polarities = pd.read_csv(fp).dropna()
data = polarities[['flagged', 'pol_rightness', 'credibility', 'moderacy']]

def visualize_densities(data, dim, title, fp):
    pol_flagged = data[data['flagged']][dim]
    pol_unflagged = data[data['flagged'] == False][dim]
    sns.kdeplot(pol_flagged, shade=True).set_title(title)
    sns.kdeplot(pol_unflagged, shade=True)
    plt.legend(title='Tweet Liked', loc='upper left', labels=['Flagged', 'Unflagged'])
    plt.savefig(fp)
    
def visualize_correlation(data, title, fp, dim1, dim2):
    data = polarities[[dim1, dim2]]
    sns.scatterplot(x=data[dim1], y=data[dim2],
                    hue=polarities['flagged']).set_title(title)
    plt.savefig(fp)
    
def mean_diff(data, dim):
    return np.mean(data[data['flagged'] == True][dim]) - np.mean(data[data['flagged'] == False][dim])

def permutation_test(data, n_reps, dim):
    # Observed statistic
    obs = mean_diff(data, dim)
    print("Observed Mean: " + str(np.mean(data[dim])))
    
    # Running and permuting n_reps of the data
    trials = []
    for i in range(n_reps):
        shuffled_impres = (
            data['flagged']
            .sample(replace=False, frac=1)
            .reset_index(drop=True)
        )
        shuffled = (
            data
            .assign(**{'flagged': shuffled_impres})
        )
        trials.append(mean_diff(shuffled, dim))
    return np.count_nonzero(np.array(trials) >= obs) / n_reps

def run_permutation_test(data, fp):
    outcomes = []
    dimensions = ['pol_rightness', 'credibility', 'moderacy']
    for dim in dimensions:
        out = {'Dimension': dim, 
            'p-value': permutation_test(data, 1000, dim)}
        outcomes.append(out)
    with open(fp, 'w') as fout:
        json.dump(outcomes , fout)
    
def run_two_sided_ttest(data, fp):
    outcomes = []
    dimensions = ['pol_rightness', 'credibility', 'moderacy']
    for dim in dimensions:
        flagged = data[data['flagged'] == True][dim]
        unflagged = data[data['flagged'] == False][dim]
        out = {'Dimension': dim, 
            'Results': stats.ttest_ind(flagged, unflagged, equal_var=True)}
        outcomes.append(out)
    with open(fp, 'w') as fout:
        json.dump(outcomes , fout)
        
def run_one_sided_ttest(data, fp):
    outcomes = []
    dimensions = ['pol_rightness', 'credibility', 'moderacy']
    for dim in dimensions:
        flagged = data[data['flagged'] == True][dim]
        unflagged = data[data['flagged'] == False][dim]
        gen = stats.ttest_ind(flagged, unflagged, equal_var=True)
        out = {'Dimension': dim,
            'p-value': gen[1]/2,
            'Test Statistic': gen[0]
            }
        outcomes.append(out)
    with open(fp, 'w') as fout:
        json.dump(outcomes , fout)