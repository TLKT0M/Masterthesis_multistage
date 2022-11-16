



from environment import Environment
import numpy as np
from datetime import datetime
import pandas as pd
from tqdm import tqdm

if __name__ == "__main__":
    episodes =1
    r_p_eps  = 100
    increase_items=False
    gg_list = ["optimal","ms_step","os_start","os_step_min_c","os_step_min_cd","os_step_min_d","min_c","min_cd"]
    bg_list = ["optimal","ms_step","os_step","max_avg_d","max_avg_cd","tree"]
    #gg_list=["optimal"]
    #bg_list=["optimal"]
    sol={"history":[],"solution":[],"runtime":[],"items":[],"uncertain":[],"method":[]}
    time={}
    data={}
    data['eps']=np.zeros(int(episodes * (r_p_eps+1)))
    data['rep']=np.zeros(int(episodes * (r_p_eps+1)))
    time['eps']=np.zeros(int(episodes * (r_p_eps+1)))
    time['rep']=np.zeros(int(episodes * (r_p_eps+1)))
    for gg in gg_list:
        for bg in bg_list:
            if not((gg=="optimal" and bg!="optimal") or (gg!="optimal" and bg=="optimal")) :
                name = str(gg)+"/"+str(bg)
                time[name]= np.zeros(int(episodes * (r_p_eps+1)))
                data[name]= np.zeros(int(episodes * (r_p_eps+1)))
    k=0
    for eps in tqdm(range(1,episodes+1)):
        if increase_items:
            env = Environment(eps * 4,eps * 2,eps*1,50,100,0.5)
        else:
            env = Environment(8,4,2,50,100,0.5)
        for rep in tqdm(range(0,r_p_eps+1)):
            env.full_reset(seed=31+rep)
            for gg in gg_list:
                for bg in bg_list:
                    if not((gg=="optimal" and bg!="optimal") or (gg!="optimal" and bg=="optimal")) :
                        
                        name = str(gg)+"/"+str(bg)
                        env.reset(gg_method=gg,bg_method=bg,percent=r_p_eps*rep)
                        start = datetime.now()
                        h,o,r,i,u = env.step() 
                        end = datetime.now() - start
                        sol["method"].append(name)
                        sol["history"].append(h)
                        sol["solution"].append(round(float(o),4))
                        sol["runtime"].append(round(float(end.total_seconds()),4))
                        sol["items"].append(i)
                        sol["uncertain"].append(u)
                        time[name][k]= round(float(end.total_seconds()),4)
                        data[name][k]= o
                        data['eps'][k]= eps
                        data['rep'][k]= rep
                        time['eps'][k]= eps
                        time['rep'][k]= rep
                        pd.DataFrame.from_dict(sol).to_csv("solutions.csv")
                        pd.DataFrame.from_dict(data).to_csv("data.csv")
                        pd.DataFrame.from_dict(time).to_csv("times.csv")
            k+=1            
        