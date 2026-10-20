"""Optional static portfolio chart: pip install matplotlib==3.10.8."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'reports/analysis.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'axes.labelcolor':'#61717b','xtick.color':'#61717b','ytick.color':'#61717b','text.color':'#13232e'})
fig,(a,b)=plt.subplots(1,2,figsize=(14,5.8),gridspec_kw={'width_ratios':[1,1.25]})
fig.set_facecolor('#f2f5f4')
for ax in (a,b):
 ax.set_facecolor('#f2f5f4');ax.set_axisbelow(True)
fig.suptitle('NYC TAXI | January 2025 operations snapshot',x=.055,y=.96,ha='left',fontsize=20,fontweight='bold')
fig.text(.055,.865,'3.24M retained trips  /  $59.02M base fares  /  14.68 min average duration',fontsize=12,color='#087e83')
hours=d['exports']['hours'];a.bar([r['pickup_hour'] for r in hours],[r['trips'] for r in hours],color='#087e83',width=.78)
a.set_title('Recorded pickup activity by hour',loc='left',pad=18,fontweight='bold');a.set_xticks([0,6,12,18,23]);a.set_xlabel('Pickup hour');a.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v/1000:.0f}k'));a.grid(axis='y',color='#dbe4e7')
zones=d['exports']['zones'][:7][::-1];b.barh([r['zone'] for r in zones],[r['trips'] for r in zones],color='#087e83',height=.6)
b.set_title('Leading pickup zones',loc='left',pad=18,fontweight='bold');b.xaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v/1000:.0f}k'));b.set_xlabel('Retained trips');b.grid(axis='x',color='#dbe4e7');b.tick_params(axis='y',length=0)
fig.text(.055,.045,'Source: NYC TLC · Full January 2025 yellow-taxi file, filtered cohort. Base fares exclude extras; observed activity does not establish unmet demand.',fontsize=9,color='#61717b')
fig.subplots_adjust(left=.055,right=.97,top=.74,bottom=.18,wspace=.8)
fig.savefig(ROOT/'docs/analysis-preview.png',dpi=150,facecolor=fig.get_facecolor())
plt.close(fig)
