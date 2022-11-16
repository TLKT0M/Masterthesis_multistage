

import numpy as np
import pandas as pd
from good_agent import GoodAgent
from bad_agent import BadAgent
from yasol.yasol_interface import Yasol
from tqdm import tqdm
class Environment:
    
    def __init__(self,ITEM_COUNT,SELECT_COUNT,BG_SELECT_COUNT,MIN_PRICE,MAX_PRICE,BUDGET):
        self.ITEM_COUNT = ITEM_COUNT
        self.SELECT_COUNT = SELECT_COUNT
        self.BG_SELECT_COUNT = BG_SELECT_COUNT
        self.MIN_PRICE = MIN_PRICE
        self.MAX_PRICE = MAX_PRICE
        self.BUDGET = BUDGET
        
        self.full_reset()
    
    def full_reset(self,seed=0,percent=0):
        if seed!=0:
            np.random.seed(seed)
        self.percent=percent
        self.items = np.random.randint(self.MIN_PRICE,self.MAX_PRICE,self.ITEM_COUNT)
        self.uncertain = np.random.randint(0,self.MIN_PRICE*self.BUDGET,self.ITEM_COUNT)
        self.yasol = Yasol(True)
    
    def reset(self,gg_method="ms_step" ,bg_method="avg_cd",percent=0):
        self.yitems=self.items
        self.percent=percent
        self.yuncertain = self.uncertain
        self.gg_select = self.SELECT_COUNT
        self.bg_select = self.BG_SELECT_COUNT
        self.stage = 0
        self.position=np.arange(self.SELECT_COUNT*2)
        self.preposition = np.arange(self.SELECT_COUNT*2)
        self.history = np.subtract(np.zeros(self.SELECT_COUNT*2),np.ones(self.SELECT_COUNT*2))
        self.val = 0.0
        self.vals=[]
        self.gg_method = gg_method
        self.bg_method = bg_method
        
    def get_path(self,gagent,tree,action,select,bg_select,items,ilist,uncertain,preposition):
        select=select-1
        tree = tree[action]
        item=items
        unc=uncertain
        ili=ilist
        prep=preposition
        for i in tree:
            items=item
            uncertain=unc
            ilist=ili
            preposition=prep
            if select>0:
                if i!=-1:
                    bg_select = bg_select - 1

                if self.gg_method=="ms_step":
                    action2 =  gagent.ms_step(items,uncertain,select,bg_select,-1)
                elif self.gg_method=="os_start":
                    action2 =  gagent.os_start(self.yitems,self.yuncertain,select,self.bg_select,-1) 
                elif self.gg_method=="os_step_min_c":
                    action2 =  gagent.os_step(items,uncertain,select,bg_select,-1,self.gg_method)
                elif self.gg_method=="os_step_min_cd":
                    action2 =  gagent.os_step(items,uncertain,select,bg_select,-1,self.gg_method)
                elif self.gg_method=="os_step_min_d":
                    action2 =  gagent.os_step(items,uncertain,select,bg_select,-1,self.gg_method)
                elif self.gg_method=="min_c":
                    action2 =  gagent.min_c(items,uncertain,select,bg_select,-1)
                elif self.gg_method=="min_cd":
                    action2 = gagent.min_cd(items,uncertain,select,bg_select,-1)
                elif self.gg_method=="ind_one":
                    action2 = gagent.min_individual_one(items,uncertain,select,bg_select,-1,self.percent)
                elif self.gg_method=="ind_one_v2":
                    action2 = gagent.min_individual_one_v2(items,uncertain,select,bg_select,-1,self.percent)
                elif self.gg_method=="ind_two":
                    action2 = gagent.min_individual_two(items,uncertain,select,bg_select,-1,self.percent)
                elif self.gg_method=="ind_three":
                    action2 = gagent.min_individual_three(items,uncertain,select,bg_select,-1,self.percent)
                elif self.gg_method=="ind_three_v2":
                    action2 = gagent.min_individual_three_v2(items,uncertain,select,bg_select,-1,self.percent)
                else:
                    print("Select GoodGuy",self.gg_method)

                items=np.delete(items,action2)
                uncertain=np.delete(uncertain,action2)
                action3=action2

                action2=ilist[action2]

                ilist=np.delete(ili,action3)
 
                if bg_select==0:
                    tree[i] = {action2:{-1:{}}}
                elif bg_select>=select:
                    tree[i] = {action2:{action2:{}}}
                else:
                    tree[i] = {action2:{-1:{},action2:{}}}
                self.get_path(gagent,tree[i],action2,select,bg_select,items,ilist,uncertain,preposition)
        return tree
    
    def get_value(self,items,uncertain,d,itemlist,sol,dep,mode):
        mode=mode+1

        for i in d:
            if len(d[i])!=0:
                if i==-1:
                    itemlist.append(i)
                    sol.append(0)
                else:
                    if mode%2==0:
                        dep=dep+1

                        itemlist.append(i)
                        sol.append(items[i])
                    else:

                        itemlist.append(i)
                        sol.append(uncertain[i]) 
                self.get_value(items,uncertain,d[i],itemlist,sol,dep,mode)
            else:
                if i==-1:
                    itemlist.append(i)
                    sol.append(0)
                else:
                    itemlist.append(i)
                    sol.append(uncertain[i]) 
                itemlist.append('X')
                sol.append('X') 
        return itemlist,sol
    
    def special_bg(self,gagent):
        d = {}
        ilist=np.arange(len(self.items))
        preposition=self.preposition
        if self.gg_method=="ms_start":
            action =  gagent.ms_start(self.items,self.uncertain,self.SELECT_COUNT,self.BG_SELECT_COUNT,-1)
        elif self.gg_method=="ms_step":
            action =  gagent.ms_step(self.items,self.uncertain,self.SELECT_COUNT,self.BG_SELECT_COUNT,-1)
        elif self.gg_method=="os_start":
            action =  gagent.os_start(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1)
        elif self.gg_method=="os_step_min_c":
            action =  gagent.os_step(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.gg_method)                
        elif self.gg_method=="os_step_min_cd":
            action =  gagent.os_step(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.gg_method)
        elif self.gg_method=="os_step_min_d":
            action =  gagent.os_step(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.gg_method)
        elif self.gg_method=="min_c":
            action =  gagent.min_c(self.items,self.uncertain,self.SELECT_COUNT,self.BG_SELECT_COUNT,-1)
        elif self.gg_method=="min_cd":
            action =  gagent.min_cd(self.items,self.uncertain,self.SELECT_COUNT,self.BG_SELECT_COUNT,-1)
        elif self.gg_method=="ind_one":
            action = gagent.min_individual_one(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
        elif self.gg_method=="ind_one_v2":
            action = gagent.min_individual_one_v2(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
        elif self.gg_method=="ind_two":
            action = gagent.min_individual_two(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
        elif self.gg_method=="ind_three":
            action = gagent.min_individual_three(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
        elif self.gg_method=="ind_three_v2":
            action = gagent.min_individual_three_v2(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
        else:
            print("Select GoodGuy",self.gg_method)      
 
        ilist=np.delete(ilist,action)
        items=np.delete(self.items,action)
        uncertain=np.delete(self.uncertain,action)
        d[action] = {-1:{},action:{}}
        d[action] =self.get_path(gagent,d,action,self.SELECT_COUNT,self.BG_SELECT_COUNT,items,ilist,uncertain,preposition)

        itemlist,sol=self.get_value(self.items,self.uncertain,d,[],[],0,-1)

   
        l=[]
        lu=[]
        for i in itemlist:
            if i=='X':
                lu.append(l)
                l=[]
            else:
                l.append(i)

        m=np.zeros((len(lu),self.SELECT_COUNT*2))-2
        for i in range(len(lu)):
            m[i][int(self.SELECT_COUNT*2-len(lu[i])):] = lu[i]
        

        for i in range(len(m)):
            for o in range(len(m[i])):
                if int(m[i][o])==int(-2):
                    m[i][o]=m[i-1][o]
        l=[]
        lu=[]
        for i in sol:
            if i=='X':
                lu.append(l)
                l=[]
            else:
                l.append(i)
        v=np.zeros((len(lu),self.SELECT_COUNT*2))-2
        for i in range(len(lu)):
            v[i][int(self.SELECT_COUNT*2-len(lu[i])):] = lu[i]
        val_arr=[]
        for i in range(len(v)):
            row_val=0.0
            for o in range(len(v[i])):
                if int(v[i][o])==int(-2):
                    v[i][o]=v[i-1][o]
                row_val=row_val+v[i][o]
            val_arr.append(row_val)

        return m[val_arr.index(max(val_arr))],max(val_arr),0.0,self.items,self.uncertain
    
    def step(self):
        gagent=GoodAgent(self)
        bagent = BadAgent(self)
        
        if self.gg_method=="optimal" and self.bg_method == "optimal":
            return gagent.optimal(self.items,self.uncertain,self.SELECT_COUNT,self.BG_SELECT_COUNT,-1)
        elif self.bg_method == "tree" and self.gg_method!="optimal":
            return self.special_bg(gagent)
        else:
            for i in range(self.SELECT_COUNT):

                if self.gg_method=="ms_step":
                    action =  gagent.ms_step(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1)
                elif self.gg_method=="os_start":
                    action =  gagent.os_start(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1)
                elif self.gg_method=="os_step_min_c":
                    action =  gagent.os_step(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.gg_method)
                elif self.gg_method=="os_step_min_cd":
                    action =  gagent.os_step(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.gg_method)
                elif self.gg_method=="os_step_min_d":
                    action =  gagent.os_step(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.gg_method)
                elif self.gg_method=="min_c":
                    action =  gagent.min_c(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1)
                elif self.gg_method=="min_cd":
                    action =  gagent.min_cd(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1)
                elif self.gg_method=="ind_one":
                    action = gagent.min_individual_one(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
                elif self.gg_method=="ind_one_v2":
                    action = gagent.min_individual_one_v2(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
                elif self.gg_method=="ind_two":
                    action = gagent.min_individual_two(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
                elif self.gg_method=="ind_three":
                    action = gagent.min_individual_three(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
                elif self.gg_method=="ind_three_v2":
                    action = gagent.min_individual_three_v2(self.yitems,self.yuncertain,self.gg_select,self.bg_select,-1,self.percent)
                else:
                    print("Select GoodGuy",self.gg_method)   
                self.history[self.stage] = self.position[action]
                
                self.val += self.yitems[action]
                self.stage+=1
                self.gg_select =self.gg_select-1
                if self.bg_select == 0:
                    bg_action = False   
                elif (self.SELECT_COUNT*2)-1-self.stage>(self.bg_select-1)*2:
                    if self.bg_method == "max_avg_cd":
                        bg_action = bagent.max_avg_cd(self.yitems,self.yuncertain,self.gg_select,self.bg_select,action)
                    elif self.bg_method == "max_avg_d":
                        bg_action = bagent.max_avg_d(self.yitems,self.yuncertain,self.gg_select,self.bg_select,action)
                    elif self.bg_method == "ms_step":
                        bg_action = bagent.ms_step(self.yitems,self.yuncertain,self.gg_select,self.bg_select,action)
                    elif self.bg_method == "os_step":
                        bg_action = bagent.os_step(self.yitems,self.yuncertain,self.gg_select,self.bg_select,action)
                else:
                    bg_action=True
                if bg_action:
                    self.history[self.stage] = self.position[action]
                    self.val = self.val + self.yuncertain[action]  
                    self.bg_select -=1
                self.yitems=np.delete(self.yitems,action)
                self.yuncertain=np.delete(self.yuncertain,action)
                self.manage_positions(action)
                self.stage+=1
        return self.history, self.val,0.0,self.items,self.uncertain
                    
    def manage_positions(self,action):
        self.position = np.delete(self.position,action)
        
