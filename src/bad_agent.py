from yasol.yasol_interface import Yasol
import numpy as np

class BadAgent:
        def __init__(self,env):
            self.env=env
    
    
        def ms_step(self,items,uncertain,gg_select,bg_select,action):
            runtime,optimal,varsdict = self.env.yasol.build("multistage","badguy",self.env.gg_method,self.env.bg_method,action,items,uncertain,gg_select,bg_select)
            taken = [x for x in varsdict['vars'] if int(x['value'])==1 and int(x['block'])==2 and x['name']!="dummy2"]
            if len(taken)>0:
                return True
            else:
                return False
                    
                
        def os_step(self,items,uncertain,gg_select,bg_select,action):
            items = np.delete(items,action)
            runtime,optimal,varsdict = self.env.yasol.build("onestage","badguy",self.env.gg_method,self.env.bg_method,action,items,uncertain,gg_select,bg_select)
            taken = [int(x['index'])-1-len(items) for x in varsdict['vars'] if int(x['index'])>len(items) and int(x['block'])==1 and float(x['value'])>float(0.0)]
            uval = np.argsort(uncertain)[::-1]
            tval=[]
            for i in uval:
                if i in taken:
                    tval.append(i)
            if action in tval:
                return True
            else:
                return False
    
        def max_avg_d(self,items,uncertain,gg_select,bg_select,action):
            if uncertain[action]>np.average(uncertain):
                return True
            else:
                return False
    
        def max_avg_cd(self,items,uncertain,gg_select,bg_select,action):
            cd=items+uncertain
            if cd[action]>np.average(cd):
                return True
            else:
                return False