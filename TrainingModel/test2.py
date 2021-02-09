from agent import AI_Trader
from functions import *
from tqdm import tqdm
import sys
from keras.models import load_model

# hyprtparameters
window_size = 7
episodes = 10
trained_model = load_model("models/ai_trader_4.h5")

batch_size = 64
data = load_mydata("EUR/USD")
data_samples = len(data) - 1
trader = AI_Trader(window_size, False, "ai_trader_4.h5")
RewardStats = [] 

# defining a training loop that will iterate through all the episodes
for episode in range(1, episodes + 1):
    print("Episode: {}/{}".format(episode, episodes))

    i_state = CreateState(data, 0, window_size + 1)
    state = i_state.reshape(1,7,2)
    balance = 100000
    total_profit = 0
    trader.inventory = []
    b=0
    a=0

    for t in tqdm(range(data_samples)):
        action = trader.act(state)

        n_state = CreateState(data, t+1, window_size + 1)
        next_state = n_state.reshape(1, 7, 2)
        reward = 0
        a+=1

        if action == 1:
            trader.inventory.append(data[t][0])
            #print("AI Trader BOUGHT:", formatPrice(data[t][0]))
            b=b+1
            a=0

        elif action == 2 and len(trader.inventory) > 0:
            buy_price = trader.inventory.pop(0)
            reward = max(data[t][0] - buy_price, 0)*100
            
            total_profit += data[t][0] - buy_price
            b=0
            a=0
            #print("AI Trader SOLD: ", formatPrice(data[t][0]), " Profit: " + formatPrice(data[t][0] - buy_price))
        
        if(b>10 or a>20):
            reward+=-200
        
                
        if t == data_samples - 1 :
        # this for loop basically closes all open positions as the episode comes to an end. 
    
            for x in trader.inventory:
                buy_price = trader.inventory.pop(0)
                reward = max(data[t][0] - buy_price, 0)
                total_profit += data[t][0] - buy_price
                #print("AI Trader SOLD: ", formatPrice(data[t][0]), " Profit: " + formatPrice(data[t][0] - buy_price))

            done = True
            stats = [total_profit, episode]
            RewardStats.append(stats)

        else:
            done = False

        trader.memory.append((state, action, reward, next_state, done))
        state = next_state
       
        if done:
            print("########################")
            print("TOTAL PROFIT: {}".format(total_profit))
            print("ACCOUNT BALANCE: {}".format(balance + total_profit))
            print("Final Inventory", trader.inventory)
            print("########################")

           
        if len(trader.memory) > batch_size:
            #print("USING MEMORY TO TRADE")
            hist = trader.expReplay(batch_size)
            #print(hist) 

   # save model weights and parameters at epochs divisible by 10
    if episode % 2 == 0:
        trader.model.save("models/ai_trader_{}.h5".format(episode))

#plotting rewards gained over time
df = pd.DataFrame(RewardStats, columns=['Reward', 'Episode'])
df.set_index('Episode', inplace=True)
plot_totalReward(df)