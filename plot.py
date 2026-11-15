"""Plots Fig. 5 and Fig. 6 of the paper from results/*.json. Run after sim.py."""
import json,os,numpy as np,matplotlib
os.makedirs('figures',exist_ok=True)
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10.5,'axes.spines.top':False,'axes.spines.right':False})
R=json.load(open('results/policies.json')); S=json.load(open('results/beta_sweep.json'))
devs=[('desk','Настільний ПК'),('mid','Ноутбук\nсереднього класу'),('weak','Слабкий\nноутбук')]
pols=[('never','Без адаптації','white',''),('always','Завжди адаптувати','0.85',''),('user','Лише вартість\nдля користувача','white','///'),('proposed','Запропонована\nмодель','0.25','')]
fig,axs=plt.subplots(1,2,figsize=(10,4.2),dpi=300)
x=np.arange(3); w=0.2
for j,(key,lab,fc,h) in enumerate(pols):
    t=[R[f'{d}|{key}']['time'] for d,_ in devs]; ci=[R[f'{d}|{key}']['time_ci'] for d,_ in devs]
    e=[R[f'{d}|{key}']['E'] for d,_ in devs]
    axs[0].bar(x+(j-1.5)*w,t,w,yerr=ci,color=fc,hatch=h,edgecolor='black',lw=0.7,capsize=2,label=lab)
    axs[1].bar(x+(j-1.5)*w,e,w,color=fc,hatch=h,edgecolor='black',lw=0.7)
axs[0].set_ylabel('Середній час на задачу, с'); axs[1].set_ylabel('Енергія на адаптації за сесію, Дж')
axs[0].set_title('а) Час взаємодії',fontsize=10.5); axs[1].set_title('б) Енергоспоживання адаптацій',fontsize=10.5)
for a in axs: a.set_xticks(x,[l for _,l in devs])
axs[0].set_ylim(0,10)
fig.legend(*axs[0].get_legend_handles_labels(),loc='lower center',ncol=4,frameon=False,fontsize=9,bbox_to_anchor=(0.5,-0.08))
fig.tight_layout(); fig.savefig('figures/fig5_policies.png',bbox_inches='tight')
fig,axs=plt.subplots(1,2,figsize=(10,3.6),dpi=300)
B=[0,1,2,5,10,20]
for d,lab,ls in [('mid','Ноутбук середнього класу','-'),('weak','Слабкий ноутбук',':')]:
    axs[0].plot(B,[S[f'{d}|{b}']['time'] for b in B],'k'+ls,marker='o',ms=5,label=lab)
    axs[1].plot(B,[S[f'{d}|{b}']['E'] for b in B],'k'+ls,marker='o',ms=5,label=lab)
axs[0].set_ylim(6,9); axs[1].set_ylim(0,3.2)
axs[0].set_ylabel('Середній час на задачу, с'); axs[1].set_ylabel('Енергія на адаптації, Дж')
for a in axs: a.set_xlabel('Коефіцієнт β, с')
axs[0].set_title('а) Час взаємодії',fontsize=10.5); axs[1].set_title('б) Енергоспоживання адаптацій',fontsize=10.5)
axs[1].legend(frameon=False,fontsize=9,loc='lower left')
from matplotlib.ticker import FuncFormatter
f=FuncFormatter(lambda v,p:('%g'%v).replace('.',','))
for a in axs: a.xaxis.set_major_formatter(f); a.yaxis.set_major_formatter(f)
fig.tight_layout(); fig.savefig('figures/fig6_beta.png',bbox_inches='tight')
