
import os
import numpy as np
from datetime import datetime
import subprocess
import xml.etree.ElementTree as et
class Yasol:

    def __init__(self,del_mode):
        self.path='src/yasol/instances'
        if del_mode:
            self.clear_instances()
    def clear_instances(self):
        self.delete_folders(self.path)      
    def delete_folders(self,path):
        for f in os.listdir(path):
            if os.path.isdir(os.path.join(path, f)):
                self.delete_folders(os.path.join(path, f))
            else:
                os.remove(os.path.join(path, f))
    
    
    def objective(self,mode,pi,items,uncertain,action,gg_select,bg_select):
        if mode=='onestage':
            objective= "MINIMIZE\n"
            x=""
            pi= "+"+str(bg_select)+"pi "
            p=""
            
            for i in range(len(items)):
                x = x + "+"+str(items[i])+"x_"+str(i)+"_0 "
                p = p + "+"+str(uncertain[i])+"p_"+str(i)+"_0 "
            return objective+x+pi+p+"\n"
        elif mode=='multistage':
            objective= "MINIMIZE\n"
            x = ""
            q = ""
            if action!=-1:
                gg_select+=1
            for i in range(len(items)):
                for s in range(gg_select):
                    if action!=-1:
                        if s != 0:
                            x=x+"+"+str(items[i])+"x_"+str(i)+"_"+str(s)+" "
                    else:
                        x=x+"+"+str(items[i])+"x_"+str(i)+"_"+str(s)+" "
            for i in range(len(uncertain)):
                for s in range(gg_select):
                    q=q+"+"+str(uncertain[i])+"q_"+str(i)+"_"+str(s)+" "
            return objective+x+q+"\n"

    def gg_select(self,mode,items,action,gg_select):
        if mode=='onestage':
            x=""
            for i in range(len(items)):
                x = x +"+x_"+str(i)+"_0 "
            return x+"= "+str(gg_select)+"\n"
        elif mode=='multistage':
            x = ""
            if action!=-1:
                gg_select+=1
            for i in range(len(items)):

                for s in range(gg_select):
                    if action!=-1:
                        if s != 0:
                            x=x+"+x_"+str(i)+"_"+str(s)+" "
                    else:
                        x=x+"+x_"+str(i)+"_"+str(s)+" "
            if action!=-1:
                x=x+"= "+str(gg_select-1)+"\n"
            else:
                x=x+"= "+str(gg_select)+"\n"        
            return x
        return "" 
        
    def gg_select_one(self,mode,pi,items,uncertain,action,gg_select):

        if mode=='onestage':
            c=""
            for i in range(len(items)):
                c = c +"+p_"+str(i)+"_0 -"+str(pi)+"pi -"+str(uncertain[i])+"x_"+str(i)+"_0 >= 0 \n"
            return c
        elif mode=='multistage':
            x = ""
            if action!=-1:
                gg_select+=1
            for i in range(len(items)):

                for s in range(gg_select):
                    
                    if action!=-1:
                        if s != 0:
                            x=x+"+x_"+str(i)+"_"+str(s)+" "
                    else:
                        x=x+"+x_"+str(i)+"_"+str(s)+" "
                if i==action:        
                    x=x+"<= 0\n"
                else:
                    x=x+"<= 1\n"
            return x
        return "" 
    def select_stage(self,mode,items,gg_select,action):
        x=""
        if mode=='multistage':
            if action!=-1:
                gg_select+=1
            for s in range(gg_select):
                if action!=-1:
                    if s != 0:
                        for i in range(len(items)):
                            x=x+"+x_"+str(i)+"_"+str(s)+" "
                        x=x+"= 1\n"
                else:    
                    for i in range(len(items)):
                        x=x+"+x_"+str(i)+"_"+str(s)+" "
                    x=x+"= 1\n"
            return x
        else:
            return ""
    def constraints(self,mode,pi,items,uncertain,action,gg_select):
        subject = "SUBJECT TO\n"
        gg_select_con = self.gg_select(mode,items,action,gg_select)
        once_select = self.gg_select_one(mode,pi,items,uncertain,action,gg_select)
        select_stage = self.select_stage(mode,items,gg_select,action)
        constraints = subject+gg_select_con+once_select+select_stage
        return constraints
    def select_selected(self,items,uncertain, gg_select,action,mode):
        q=""
        
        if mode == "onestage":
           return ""
        else:
            if action!=-1:
                gg_select+=1
            for i in range(len(items)):
                for s in range(gg_select):
                    if action!=-1:
                        if s != 0:
                            q=q+"q_"+str(i)+"_"+str(s)+" -x_"+str(i)+"_"+str(s)+" <= 0\n"
                    else:
                        q=q+"q_"+str(i)+"_"+str(s)+" -x_"+str(i)+"_"+str(s)+" <= 0\n"
            for u in range(len(uncertain)):
                for s in range(gg_select):
                    if action!=-1:
                        if s == 0:
                            if u == action:
                                q=q+"q_"+str(u)+"_"+str(s)+" <= 1\n"
                            else:
                                q=q+"q_"+str(u)+"_"+str(s)+" <= 0\n"
        return q
    
    def unc_select_stage(self, items,gg_select,mode,action):
        q=""
        if mode=="multistage":
            if action!=-1:
                gg_select+=1
            for s in range(gg_select):
                for i in range(len(items)):
                    q=q+"+q_"+str(i)+"_"+str(s)+" "
                q=q+"<= 1\n"
            return q
        else:
            return ""
    def unc_once_state(self, items,gg_select,mode,action):
        q=""
        if mode=="multistage":
            if action!=-1:
                gg_select+=1
            for i in range(len(items)):
                for s in range(gg_select):
                    q=q+"+q_"+str(i)+"_"+str(s)+" "
                q=q+"<= 1\n"
            return q
        else:
            return ""
        
    def unc_gammas(self,items,gg_select,bg_select,mode,action):
        q=""
        if mode=="multistage":
            if action!=-1:
                gg_select+=1
            for s in range(gg_select):
                for i in range(len(items)):
                    q=q+"+q_"+str(i)+"_"+str(s)+" "
            q=q+"<= "+str(bg_select)+"\n" 
            return q    
        return ""
            
    def uncertain_constraints(self,items,uncertain,gg_select,bg_select,action,mode):
        if mode =="multistage":
            subject = "UNCERTAINTY SUBJECT TO\n"
            select_select = self.select_selected(items,uncertain,gg_select,action,mode)
            once_stage = self.unc_once_state(uncertain,gg_select,mode,action)
            select_stage = self.unc_select_stage(uncertain,gg_select,mode,action)
            gammas= self.unc_gammas(uncertain,gg_select,bg_select,mode,action)
            unc_constraints = subject+select_select+once_stage+select_stage+gammas
            return unc_constraints
        else:
            return ""
    
    def bounds(self,mode,pi,items,uncertain,action,gg_select):
        sums = sum(uncertain)
        if mode =="multistage":
            bounds="BOUNDS\n"
            x=""
            q=""
            if action!=-1:
                gg_select+=1
            for stage in range(gg_select):
                for item in range(len(items)):
                    if action!=-1:
                        if stage != 0:
                            x=x+"0 <= x_"+str(item)+"_"+str(stage)+" <= 1\n"
                    else:
                        x=x+"0 <= x_"+str(item)+"_"+str(stage)+" <= 1\n"
                for unc in range(len(uncertain)):
                    q=q+"0 <= q_"+str(unc)+"_"+str(stage)+" <= 1\n"
            bounds=bounds+x+q + "0 <= dummy <= 1\n" + "0 <= dummy2 <= 1\n"
        else:
            bounds="BOUNDS\n"
            x=""
            pi="0 <= pi <= "+str(sums)+"\n"
            p=""
            for item in range(len(items)):    
                x=x+"0 <= x_"+str(item)+"_0 <= 1\n"
                p=p+"0 <= p_"+str(item)+"_0 <= "+str(sums)+"\n"
            bounds=bounds+x+p+pi
        return bounds
    
    def bins(self,items,uncertain,gg_select,action,mode):

        if mode=="onestage":
            bins="BINARIES\n"
            x=""
            for item in range(len(items)):
                x=x+"x_"+str(item)+"_0\n"
            bins=bins+x
        else:
            bins="BINARIES\n"
            x=""
            q=""
            if action!=-1:
                gg_select+=1
            for item in range(len(items)):
                for stage in range(gg_select):
                    if action!=-1:
                        if stage!=0:
                             x=x+"x_"+str(item)+"_"+str(stage)+"\n"
                        
                    else:
                        x=x+"x_"+str(item)+"_"+str(stage)+"\n"
                        
            for unc in range(len(uncertain)):
                for stage in range(gg_select):
                    q=q+"q_"+str(unc)+"_"+str(stage)+"\n"
            bins=bins+x+q+"dummy\n"+"dummy2\n"
        return bins
    
    def exists(self,items,gg_select,action,mode):
        if mode=="onestage":
            e="EXISTS\n"
            x=""
            p=""
            pi="pi\n"
            for item in range(len(items)):
                x=x+"x_"+str(item)+"_0\n"
                p=p+"p_"+str(item)+"_0\n"
            e=e+x+pi+p
        else:
            e="EXISTS\n"
            x=""
            if action!=-1:
                gg_select+=1
            for item in range(len(items)):
                for stage in range(gg_select):
                    if action!=-1:
                        if stage!=0:
                             x=x+"x_"+str(item)+"_"+str(stage)+"\n"
                        
                    else:
                        x=x+"x_"+str(item)+"_"+str(stage)+"\n"
            e=e+x+"dummy\n"+"dummy2\n"
        return e
    def alls(self,items,uncertain,gg_select,mode,action):
        q="ALL\n"
        if mode=="onestage":
            return q
        else:
            if action!=-1:
                gg_select+=1
            for item in range(len(uncertain)):
                for stage in range(gg_select):
                    q=q+"q_"+str(item)+"_"+str(stage)+"\n"
        return q
    
    def order(self,items,uncertain,gg_select,action,mode):
        
        if mode=="onestage":
            e="ORDER\n"
            x=""
            p=""
            pi="pi\n"
            for item in range(len(items)):
                x=x+"x_"+str(item)+"_0\n"
                p=p+"p_"+str(item)+"_0\n"
            order=e+x+pi+p
        else:
            order = "ORDER\n"+"dummy2\n"
            x=""
            q=""
            ord=""
            if action!=-1:
                gg_select+=1
            for stage in range(gg_select):
                x=""
                q=""
                
                for item in range(len(items)):
                    if action!=-1:
                        if stage!=0:
                            x=x+"x_"+str(item)+"_"+str(stage)+"\n"
                    else:
                        x=x+"x_"+str(item)+"_"+str(stage)+"\n"
                        
                for unc in range(len(uncertain)):
                    q=q+"q_"+str(unc)+"_"+str(stage)+"\n"
                ord =ord+x+q
            order =order+ord+"dummy\n"
        return order
    
    def bbeao(self,mode,pi,items,uncertain,action,gg_select,bg_select):
        bounds = self.bounds(mode,pi,items,uncertain,action,gg_select)
        bins = self.bins(items,uncertain,gg_select,action,mode)
        exists = self.exists(items,gg_select,action,mode)
        alls = self.alls(items,uncertain,gg_select,mode,action)
        order = self.order(items,uncertain,gg_select,action,mode)
        bbeao=bounds+bins+exists+alls+order+"END"
        return bbeao

    def construct(self,mode,direction,action,items,uncertain,gg_select,bg_select,pi,p_name):
        f_name = str(mode)+"-"+str(direction)+"-"+str(datetime.utcnow())+".qip"
        f_name=f_name.replace(" ","_")
        f_name = os.path.join(os.path.join(self.path,p_name),f_name)
        f = open(f_name, "w")
        f.write(self.objective(mode,pi,items,uncertain,action,gg_select,bg_select))
        f.write(self.constraints(mode,pi,items,uncertain,action,gg_select))
        f.write(self.uncertain_constraints(items,uncertain,gg_select,bg_select,action,mode))
        f.write(self.bbeao(mode,pi,items,uncertain,action,gg_select,bg_select))
        f.close()
        return f_name
    
    def solve(self,path):
        cmd = 'cd /Users/tomlorenzklein/Documents/Yasol_4.0.0.3_beta_debug/Yasol/Debug/;./Yasol_clp /Users/tomlorenzklein/Documents/master_project/'+path+' '
        arch = subprocess.check_output(cmd, shell=True)
        
    def get_solution(self,path):
        path = path+".sol"
        tree = et.parse(path)
        root = tree.getroot()
        runtime= root[0].attrib.get("Runtime")
        optimal = root[0].attrib.get("ObjectiveValue")
        vars = root[3].findall('variable')
        varsdict = {"vars":[]}
        for var in vars:
            vardict = var.attrib
            varsdict["vars"].append(vardict)
        return runtime,optimal,varsdict
    
    def build(self,mode,direction,gg_mode,bg_mode,action,items,uncertain,gg_select,bg_select):
        pi=1
        folders= [dir for dir in os.listdir(self.path)]
        p_name = gg_mode+"-"+bg_mode
        if p_name not in folders:
            os.mkdir(os.path.join(self.path,p_name))
        #print("ACTION",action)
        path =self.construct(mode,direction,action,items,uncertain,gg_select,bg_select,pi,p_name)
        self.solve(path)
        
        runtime,optimal,varsdict = self.get_solution(path)

        return runtime,optimal,varsdict
        
