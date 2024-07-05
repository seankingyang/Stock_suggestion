import numpy as np
import matplotlib.pyplot as plt


# import random

start_money = 1000000.0
win_rate = 0.25
loss_rate = -0.1
prob_of_win = 0.5  # 60%
number_of_games = 30

# List the posistion from 1% to 100%
invest_proportion_list = np.linspace(0.01, 1, 99)


def experiment(start_money, invest_proportion, random_games):
    for game in random_games:
        money_to_invest = round(start_money * invest_proportion, 0)
        start_money = start_money - money_to_invest
        if game:
            start_money = start_money + money_to_invest * (win_rate + 1)
        else:
            start_money = start_money + money_to_invest * (loss_rate + 1)
    return start_money


def showData(total_list, total_money_list):
    x_arr = [i for i in range(100)]
    bucket = [0] * 100
    money_bucket = [0] * 100
    for idx, val in enumerate(total_list):
        # print(int(val*100))
        bucket[int(val * 100) - 1] += 1
        money_bucket[int(val * 100) - 1] += total_money_list[idx]
    bucket_max = max(bucket)
    best_invest_percentage = bucket.index(bucket_max)
    best_avg_result = money_bucket[best_invest_percentage] / bucket_max
    print(
        "best_invest_percentage:",
        best_invest_percentage + 1,
        "\nbest_avg_result:",
        best_avg_result,
    )
    bigger_num = 0
    smaller_or_equal_num = 0
    same_num = 0
    for mo in total_money_list:
        if mo > start_money:
            bigger_num += 1
        if mo < start_money:
            smaller_or_equal_num += 1

    print(
        "\n\nTotal test:",
        len(total_list),
        "\nbigger_num:",
        bigger_num,
        "\nsmaller_or_equal_num:",
        smaller_or_equal_num,
    )
    plt.scatter(np.array(x_arr), np.array(bucket))
    plt.legend([best_avg_result])
    plt.show()


def start(total_test_number=1000):
    total_list = []
    total_money_list = []
    for _ in range(total_test_number):

        random_games = np.random.choice(
            [1, 0], number_of_games, p=[prob_of_win, 1.0 - prob_of_win]
        )
        # print(random_games)
        outcome_list = []
        for invest_proportion in invest_proportion_list:
            outcome = experiment(start_money, invest_proportion, random_games)
            outcome_list.append(outcome)
        total_list.append(
            invest_proportion_list[outcome_list.index(max(outcome_list))]
        )
        total_money_list.append(max(outcome_list))
    print(total_money_list, "\n", len(total_money_list))
    showData(total_list, total_money_list)
    # plt.plot(np.array(invest_proportion_list),np.array(outcome_list))
    # plt.show()


start(5000)
# f : Bet ratio
# b : Odds/ benefit ration
# p : win ration
# q : loss ratio
b = win_rate
l = loss_rate
p = prob_of_win
q = 1 - prob_of_win

f = (p * b + q * l) / b
random_games = np.random.choice(
    [1, 0], number_of_games, p=[prob_of_win, 1.0 - prob_of_win]
)
ben = experiment(start_money, f, random_games)
print(f * 100, ben)
