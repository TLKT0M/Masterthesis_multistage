

from yasol.yasol_interface import Yasol

import numpy as np
class GoodAgent:
    
    def __init__(self,env):
        self.env=env
        self.strategy = []
        self.itemcount=0
        self.first=True
        self.uncertain=0
        self.gg_select=0

        
    def optimal(self,items,uncertain,gg_select,bg_select,action):
        runtime,optimal,varsdict = self.env.yasol.build("multistage","goodguy","optimal","optimal",action,items,uncertain,gg_select,bg_select)
        taken = [x for x in varsdict['vars'] if int(x['value'])==1 ]
        yasol_sol=np.subtract(np.zeros(gg_select*2),np.ones(gg_select*2))
        for i in range(gg_select*2):
            for item in taken:
                if int(item['block'])-1==i:
                    yasol_sol[i] = int((int(item['index'])-1) % len(items))
        return yasol_sol,optimal,runtime,items,uncertain
    
    def ms_step(self,items,uncertain,gg_select,bg_select,action):
        runtime,optimal,varsdict = self.env.yasol.build("multistage","goodguy",self.env.gg_method,self.env.bg_method,action,items,uncertain,gg_select,bg_select)
        taken = [x for x in varsdict['vars'] if int(x['value'])==1 and int(x['block'])==1 and x['name']!="dummy2"]
        for i in taken:
            return int(i['index'])-1
        
    def os_start(self,items,uncertain,gg_select,bg_select,action): # Sort MIN
        if self.first:
            self.first=False

            runtime,optimal,varsdict = self.env.yasol.build("onestage","goodguy",self.env.gg_method,self.env.bg_method,action,items,uncertain,gg_select,bg_select)
            taken = [x for x in varsdict['vars'] if len(x['value'])==1 and int(x['value'])==1 and int(x['block'])==1 and x['name']!="dummy2"]
            if taken !=[]:

                self.strategy = [int(x['index']) for x in taken][::-1]
                
        o=self.strategy[-1*gg_select]
        return o       
            
    def os_step(self,items,uncertain,gg_select,bg_select,action,meth): 
        runtime,optimal,varsdict = self.env.yasol.build("onestage","goodguy",self.env.gg_method,self.env.bg_method,action,items,uncertain,gg_select,bg_select)
        taken = [x for x in varsdict['vars'][:len(items)] if int(x['value'])==1 and int(x['block'])==1 and x['name']!="dummy2"]
        if taken !=[]:
            if meth=="os_step_min_c":
                sorted = np.argsort(items)
            elif meth=="os_step_min_cd":
                sorted = np.argsort(items+uncertain)
            if meth=="os_step_min_d":
                sorted = np.argsort(uncertain)
            taken = [int(x['index']) for x in taken] 
            for o in sorted:
                for i in taken:
                    if i==o:
                        return int(i)

    def min_individual_one(self,items,uncertain,gg_select,bg_select,action,percent):
        if self.first:
            self.first=False
            self.select = gg_select
            self.uncertain= bg_select
        if bg_select/self.uncertain>=50/100:
            items = np.argsort(items+uncertain)
        else:  
            items = np.argsort(items)
        return items[0]
    
    def min_individual_two(self,items,uncertain,gg_select,bg_select,action,percent):
        if self.first:
            self.first=False
            self.select = gg_select
            self.uncertain= bg_select
        if bg_select/self.uncertain>=50/100:
            items = np.argsort(items)
        else:
            items = np.argsort(items+uncertain)
        return items[0]
    
    def min_individual_one_v2(self,items,uncertain,gg_select,bg_select,action,percent):
        if self.first:
            self.first=False
            self.select = gg_select
            self.uncertain= bg_select
        if bg_select/gg_select<percent/100:
            items = np.argsort(items+uncertain)
        else:   
            items = np.argsort(items)
        return items[0]
    

    def min_individual_three(self,items,uncertain,gg_select,bg_select,action,percent):
        if self.first:
            self.first=False
            self.select = gg_select
            self.uncertain= bg_select
        if bg_select/gg_select>=percent/100:
            items = np.argsort(items+uncertain)
        else:
            items = np.argsort(items)
        return items[0]    
        
    def min_individual_three_v2(self,items,uncertain,gg_select,bg_select,action,percent):
        if self.first:
            self.first=False
            self.select = gg_select
            self.uncertain= bg_select
        if bg_select/gg_select>=0.5:
            items = np.argsort(items+uncertain)
        else:
            items = np.argsort(items)
        return items[0]  
    
    def min_c(self,items,uncertain,gg_select,bg_select,action):
        items = np.argsort(items)
        return items[0]
    
    def min_cd(self,items,uncertain,gg_select,bg_select,action):
        items = np.argsort(items+uncertain)
        return items[0]
    