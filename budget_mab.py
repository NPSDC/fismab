from ucb_budget import UCB_with_budget_and_fair
from thompson_budget import fairness_with_budget_thompson_sampling
from budget_helper import *
import pickle as pi
import sys

def run_mab(k, B, nTimes, reward_means, cost_means, pickle_file, method = "UCB", alpha = None, R = None):
    #budget_arr = []
    #regret_arr = []
    other_vars = {"N":[], "X":[], "C":[], "arm_pulled":[], "tB":[], "bud_arr":[], "reg_arr":[]}
    for i in range(nTimes):
        if(method == "UCB"):
            N, X, C, arm_pulled, tB = UCB_with_budget_and_fair(k, B, reward_means, cost_means, alpha = alpha, R = R)
        elif(method == "thompson"):
            N, X, C, arm_pulled, tB = fairness_with_budget_thompson_sampling(k, B, reward_means, cost_means, alpha = alpha, R = R)
        else:
            sys.exit("Invalid input")
        other_vars["N"].append(N)
        other_vars["X"].append(X)
        other_vars["C"].append(C)
        other_vars["arm_pulled"].append(arm_pulled)
        other_vars["tB"].append(tB)
        regret, reg_sum, budget_sum = compute_regret(C, arm_pulled, cost_means, reward_means, tB)
        other_vars["bud_arr"].append(budget_sum)
        other_vars["reg_arr"].append(reg_sum)
    with open(pickle_file, "wb") as w:
        pi.dump(other_vars, w)
    return other_vars["bud_arr"], other_vars["reg_arr"]


def compute_average_regret(regret_array, budget_array, B, interval = 500):
    """Parameters
    regret_array - A list of numpy arrays of size N*tB containing regret, N is the number of times an experiment has been run, tB is varying the time required to reacha budget
    regret_array - A list of numpy arrays of size N*tB containing budget, N is the number of times an experiment has been run, tB is varying the time required to reacha budget
    """
    match = lambda a, b: np.array([ np.where(b == x)[0][0] if x in b else None for x in a ])
    n_trials = len(regret_array)
    min_budget = 1e10
    for i in range(len(budget_array)):
        min_budget = min(budget_array[i][-1], min_budget)
    
    #print(min_budget)
    time_bud = range(0, B + 1, interval)
    inds_match = list()
    
    if(len(regret_array) != len(budget_array)):
        sys.exit("number of dimensions not same")
    if(np.sum(regret_array[0].shape == budget_array[0].shape) != len(regret_array[0].shape)):
        sys.exit("Regret shape not same as budget shape")
    
    av_reg = np.zeros(len(time_bud))
    for i in range(n_trials):
        inds_match.append(match(time_bud, budget_array[i]))
        av_reg += regret_array[i][inds_match[i]]
    
    
    av_reg /= n_trials
    
    return inds_match, av_reg

if __name__ == "__main__":
    nTimes = 10 ## number of times to run the algorithm
    B = 1000
    k = 10
    reward_means = np.random.rand(10)
    cost_means = np.random.choice(range(1,k*10+1), size = k, replace = False)/10
    bud_arr, reg_array = run_mab(k, B, 10, reward_means, cost_means, "ucb_bud.pickle")
    reg = compute_average_regret(reg_array, bud_arr, B, interval = 100)
