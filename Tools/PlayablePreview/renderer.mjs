import {NPCS,PACKAGES,RIPPLES,RESCUES,HERBS,distance} from './engine.mjs';
const PPU=20;
const rect=(c,x,y,w,h,color)=>{c.fillStyle=color;c.fillRect(Math.round(x),Math.round(y),w,h);};
function pixelCircle(c,x,y,r,color){c.fillStyle=color;for(let yy=-r;yy<=r;yy++){const w=Math.floor(Math.sqrt(r*r-yy*yy));c.fillRect(Math.round(x-w),Math.round(y+yy),w*2+1,1);}}
function tree(c,x,y,size=1){c.save();c.translate(Math.round(x),Math.round(y));c.scale(size,size);
  rect(c,-12,-8,26,9,'#163c32');rect(c,-4,-35,9,35,'#514c37');rect(c,-2,-32,3,29,'#82734b');
  for(const [xx,yy,rr] of [[0,-58,23],[-17,-41,20],[18,-42,21],[0,-33,23]]){pixelCircle(c,xx,yy,rr,'#173b32');pixelCircle(c,xx-2,yy-4,rr-3,'#285342');pixelCircle(c,xx-5,yy-8,rr-8,'#3b6d4f');pixelCircle(c,xx-7,yy-11,rr-14,'#598555');}
  c.restore();}
function rock(c,x,y,s=1){c.save();c.translate(x,y);c.scale(s,s);rect(c,-11,-10,21,10,'#344e4e');rect(c,-9,-15,16,11,'#637b73');rect(c,-6,-17,9,4,'#91a193');rect(c,2,-11,7,8,'#4d6662');c.restore();}
function lantern(c,x,y){rect(c,x-2,y-35,4,35,'#5b5640');rect(c,x-11,y-34,19,3,'#706a45');rect(c,x-8,y-29,11,15,'#ad6640');rect(c,x-6,y-27,7,10,'#efbc6c');rect(c,x-5,y-25,3,7,'#ffe7a6');rect(c,x-4,y-14,2,6,'#b39551');}
function house(c,x,y){rect(c,x-64,y-61,128,61,'#293d39');rect(c,x-62,y-58,124,54,'#6d6750');rect(c,x-57,y-52,112,46,'#a3946d');
  for(let i=-56;i<60;i+=16)rect(c,x+i,y-52,2,50,'#766c50');rect(c,x-16,y-36,29,36,'#263b39');rect(c,x-12,y-33,21,33,'#4a5141');
  for(const xx of [-42,30]){rect(c,x+xx-10,y-40,20,20,'#293e3b');rect(c,x+xx-8,y-38,16,16,'#d5b974');rect(c,x+xx-1,y-38,2,16,'#64543c');rect(c,x+xx-8,y-31,16,2,'#64543c');}
  for(let row=0;row<7;row++){const w=146-row*12;rect(c,x-w/2,y-65-row*5,w,6,row%2?'#284e4b':'#365f57');}rect(c,x-79,y-65,158,5,'#163732');rect(c,x-82,y-69,12,5,'#4f7a62');rect(c,x+70,y-69,12,5,'#4f7a62');rect(c,x-23,y-8,44,8,'#526153');}

export class Renderer{
  constructor(canvas,mini,content,images){this.canvas=canvas;this.c=canvas.getContext('2d',{alpha:false});this.mini=mini;this.content=content;this.images=images;this.camera={x:22,y:0};this.numbers=[];this.tracking=true;this.rain=true;this.reduced=false;this.buildTerrain();this.resize();}
  resize(){this.canvas.width=Math.round(this.canvas.clientWidth);this.canvas.height=Math.round(this.canvas.clientHeight);this.c.imageSmoothingEnabled=false;}
  buildTerrain(){this.terrain=document.createElement('canvas');this.terrain.width=7200;this.terrain.height=720;const c=this.terrain.getContext('2d');c.imageSmoothingEnabled=false;
    rect(c,0,0,7200,720,'#3c6451');let seed=893451;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
    for(let i=0;i<28000;i++){const x=Math.floor(random()*7200),y=Math.floor(random()*720);rect(c,x,y,2+Math.floor(random()*4),1+Math.floor(random()*3),['#456e54','#50775a','#355e4f','#3d6751','#64835b'][i%5]);}
    c.fillStyle='#244d58';c.beginPath();c.moveTo(0,0);c.lineTo(7200,0);for(let x=7200;x>=0;x-=20)c.lineTo(x,175+Math.sin(x/220)*35+Math.sin(x/71)*10);c.closePath();c.fill();
    for(let x=0;x<7200;x+=18){const y=175+Math.sin(x/220)*35+Math.sin(x/71)*10;rect(c,x,y,20,5,'#668069');rect(c,x,y+5,20,3,'#426653');}
    // A top-down candidate corridor. Canonical anchors remain unchanged in production files.
    for(let x=0;x<7200;x+=8){const center=360+Math.sin(x/180)*5,w=x<1360?63:44;rect(c,x,center-w,8,w*2,'#6c7256');rect(c,x,center-w+4,8,w*2-8,'#8a8862');rect(c,x,center-w+10,8,w*2-20,'#9e9470');}
    for(let i=0;i<3200;i++){const x=random()*7200,y=330+random()*60;rect(c,x,y,random()<.5?2:4,2,['#b4a47a','#797c5d','#c1ae80'][i%3]);}
    // Main pier and the shallow-water bridge.
    for(const [start,end]of [[560,1360],[1840,2160],[4040,4560]]){rect(c,start,307,end-start,90,'#3b5147');for(let x=start;x<end;x+=13){rect(c,x,313,11,78,x%26?'#8b8260':'#9c9068');rect(c,x+2,314,1,74,'#b0a073');}rect(c,start,309,end-start,4,'#bdac7c');rect(c,start,392,end-start,5,'#5b604a');for(let x=start+5;x<end;x+=80){rect(c,x,294,7,15,'#4c5140');rect(c,x,394,7,14,'#4c5140');}}
    for(let i=0;i<260;i++){const x=20+random()*7140,y=random()<.5?460+random()*140:230+random()*25;tree(c,x,y,.7+random()*.65);}
    for(const x of [160,420,1580,1760,1940,2160,2580,3140,5160,5560,5780,6020,6280])rock(c,x,420,.8+random());
    house(c,1200,260);house(c,4780,260);house(c,5040,250);
    for(const x of [620,1280,2100,4200,4440,4920,6800,7080])lantern(c,x,300);
    // Bell tower, ropes and ruined stone apron above the encounter.
    rect(c,3480,241,160,21,'#6a8077');rect(c,3500,220,120,20,'#99a594');rect(c,3516,120,10,103,'#625b43');rect(c,3590,120,10,103,'#625b43');rect(c,3504,116,109,9,'#8a8056');rect(c,3536,138,42,47,'#8e885b');rect(c,3531,176,52,10,'#c1a96c');rect(c,3553,127,8,13,'#ceb574');rect(c,3554,186,6,29,'#a49560');
    for(let i=0;i<4;i++){rock(c,3380+i*120,280,.7);rect(c,3380+i*120,247,3,30,'#c0b38c');}
    // Eastern gate.
    for(const x of [6870,7050]){rect(c,x,267,28,146,'#4c6661');rect(c,x-4,264,36,9,'#9ca487');rect(c,x+4,280,18,119,'#7d8d78');}rect(c,6860,253,228,15,'#3a6355');rect(c,6884,236,180,18,'#507760');rect(c,6935,267,75,25,'#314f49');
  }
  point(x,y){return {x:Math.round(this.canvas.width/2+(x-this.camera.x)*PPU),y:Math.round(this.canvas.height/2-(y-this.camera.y)*PPU)};}
  label(text,x,y,color='#e9e8ce',size=11){const c=this.c;c.font=`600 ${size}px Segoe UI, sans-serif`;c.textAlign='center';c.lineWidth=3;c.strokeStyle='#102225';c.strokeText(text,x,y);c.fillStyle=color;c.fillText(text,x,y);}
  number(e,tick){this.numbers.push({...e,end:tick+25});}
  draw(game,time,title=false){const c=this.c,p=game.player,w=this.canvas.width,h=this.canvas.height;
    const target=title?{x:42,y:0}:p;this.camera.x+=(target.x-this.camera.x)*.15;this.camera.y+=(target.y-this.camera.y)*.12;
    this.camera.x=Math.max(w/PPU/2,Math.min(360-w/PPU/2,this.camera.x));
    rect(c,0,0,w,h,'#244b48');
    const worldOrigin=this.point(0,18);c.drawImage(this.terrain,worldOrigin.x,worldOrigin.y);
    // Quiet moving water highlights, independent of simulation authority.
    c.globalAlpha=.3;for(let i=0;i<65;i++){const x=(i*119+Math.sin(time*.0005+i)*8)%7200,wy=30+(i*41)%140;const pt=this.point(x/20,18-wy/20);rect(c,pt.x,pt.y,12+i%9,1,'#a6c5ae');}c.globalAlpha=1;
    const arena=this.point(178,0);c.strokeStyle='#94a98c50';c.lineWidth=2;c.setLineDash([7,10]);c.beginPath();c.ellipse(arena.x,arena.y,220,220,0,0,Math.PI*2);c.stroke();c.setLineDash([]);
    for(const o of PACKAGES){if(game.flags.packages.includes(o.id))continue;const s=this.point(o.x,o.y);rect(c,s.x-11,s.y-18,23,18,'#4d4934');rect(c,s.x-9,s.y-16,19,14,'#a28b56');rect(c,s.x-10,s.y-11,21,3,'#d0ba7c');rect(c,s.x-2,s.y-17,3,17,'#5b6746');if(game.quest===0&&game.active)this.marker(s.x,s.y-30,'◆',time);}
    if(game.quest===1&&game.active)for(const o of RIPPLES){const s=this.point(o.x,o.y);c.strokeStyle=game.flags.ripples.includes(o.id)?'#789f9c':'#b5e0cb';c.lineWidth=2;for(let r=0;r<3;r++){c.beginPath();c.ellipse(s.x,s.y,8+r*7+Math.sin(time*.003)*2,3+r*4,0,0,Math.PI*2);c.stroke();}if(!game.flags.ripples.includes(o.id))this.marker(s.x,s.y-26,'◇',time);}
    for(const o of HERBS){if(game.flags.herbs.includes(o.id))continue;const s=this.point(o.x,o.y);rect(c,s.x-1,s.y-15,3,15,'#7f9a62');rect(c,s.x-8,s.y-12,8,5,'#a8c280');rect(c,s.x+2,s.y-18,8,6,'#84b59d');rect(c,s.x-3,s.y-24,7,7,'#b4d4b2');}
    const drawable=[];
    for(const npc of NPCS){if(npc.id==='NPC_CLASS_TRIAL'&&!game.flags.boss)continue;if(npc.id==='NPC_LYAN'&&game.quest===3&&game.active)continue;drawable.push({y:npc.y,draw:()=>this.npc(npc,game,time)});}
    if(game.quest===3&&game.active)drawable.push({y:game.escort.y,draw:()=>this.npc({...game.escort,name:'Ly An',id:'escort',color:'#b9c8a9'},game,time)});
    if(game.quest===2&&game.active)for(const o of RESCUES)drawable.push({y:o.y,draw:()=>this.npc({...o,color:game.flags.rescues.includes(o.id)?'#8bac83':'#b29c6a'},game,time)});
    for(const mob of game.mobs)if(game.mobEnabled(mob)&&mob.hp>0)drawable.push({y:mob.y,draw:()=>this.mob(mob,game,time)});
    if(!game.flags.boss)drawable.push({y:0,draw:()=>this.boss(game,time)});
    drawable.push({y:p.y,draw:()=>this.hero(game,time,title)});drawable.sort((a,b)=>b.y-a.y);for(const d of drawable)d.draw();
    if(game.quest===4&&game.flags.boss&&!game.flags.seal){const s=this.point(178,0);pixelCircle(c,s.x,s.y-12,8,'#c6e8ce');rect(c,s.x-4,s.y-18,8,14,'#e5d99b');this.marker(s.x,s.y-34,'◆',time);}
    if(game.quest>=2){const s=this.point(150,3);rock(c,s.x,s.y,1.2);rect(c,s.x-3,s.y-20,6,10,'#a9c6ad');this.label('Bia bến gỗ',s.x,s.y-28,'#cfdfc0',10);}
    for(const warning of game.warnings)this.warning(warning,game);
    for(const e of game.effects)this.effect(e,game);
    if(game.guard||game.tick<game.whiffEnd){const s=this.point(p.x,p.y);c.strokeStyle=game.guard?'#f0dc8c':'#99bdad';c.globalAlpha=game.guard?.9:.45;c.lineWidth=3;c.beginPath();c.arc(s.x,s.y,30,-Math.PI,0);c.stroke();c.globalAlpha=1;}
    if(this.tracking&&!title){const goal=game.goal();if(goal){const s=this.point(goal.x,goal.y);if(s.x<270||s.x>w-215||s.y<110||s.y>h-70){const dx=goal.x-p.x,dy=-(goal.y-p.y),n=Math.hypot(dx,dy)||1;const r=Math.min(w*.24,h*.27);const x=w/2+dx/n*r,y=h/2+dy/n*r;this.label('◆',x,y,'#e7cd80',19);this.label(`${goal.name||'Mục tiêu'} · ${Math.round(distance(goal,p)*.5)}m`,x,y+20,'#e7dba9',10);}else this.marker(s.x,s.y-53,'◆',time);}}
    this.numbers=this.numbers.filter(n=>n.end>game.tick);for(const n of this.numbers){const s=this.point(n.x,n.y);const life=(n.end-game.tick)/25;this.label(n.text,s.x,s.y-40-(1-life)*22,{hurt:'#f49e8e',crit:'#ffe084',good:'#b5e8bd',miss:'#b2c4c2'}[n.kind]||'#f1e6b5',n.kind==='crit'?19:14);}
    if(this.rain&&!this.reduced){c.strokeStyle='#b2d3cb26';c.lineWidth=1;for(let i=0;i<90;i++){const x=(i*193-time*.06)%(w+50),y=(i*79+time*.18)%(h+60);c.beginPath();c.moveTo(x,y);c.lineTo(x-3,y+9);c.stroke();}}
    this.drawMini(game);
  }
  marker(x,y,icon,time){this.label(icon,x,y+Math.sin(time*.004)*3,'#edcc7e',17);}
  npc(n,game,time){const s=this.point(n.x,n.y),c=this.c;if(s.x< -80||s.x>this.canvas.width+80)return;
    c.fillStyle='#0c292980';c.beginPath();c.ellipse(s.x,s.y,12,5,0,0,Math.PI*2);c.fill();
    rect(c,s.x-8,s.y-31,16,26,'#152e30');rect(c,s.x-7,s.y-30,14,22,n.color);rect(c,s.x-10,s.y-27,4,15,n.color);rect(c,s.x+7,s.y-27,4,15,n.color);rect(c,s.x-4,s.y-44,10,12,'#dfc39a');rect(c,s.x-6,s.y-47,14,7,n.id==='NPC_TA_VAN_KHANH'?'#cbd7c6':'#384641');rect(c,s.x-4,s.y-9,3,10,'#334742');rect(c,s.x+3,s.y-9,3,10,'#334742');rect(c,s.x-7,s.y-20,14,3,'#ad9560');
    this.label(n.name,s.x,s.y-53,'#e5d79b',11);const goal=game.goal();if(goal?.id===n.id)this.marker(s.x,s.y-74,game.ready()?'?':'!',time);
  }
  hero(game,time,title){const p=game.player,s=this.point(p.x,p.y),c=this.c;
    c.fillStyle='#09272388';c.beginPath();c.ellipse(s.x,s.y,12,5,0,0,Math.PI*2);c.fill();
    const angle=(Math.atan2(p.face.x,p.face.y)+Math.PI*2)%(Math.PI*2),row=Math.round(angle/(Math.PI/4))%8;
    const anim=title?'idle':p.anim,spec=this.content.sprites[anim]||this.content.sprites.idle,img=this.images[anim]||this.images.idle;
    let frame=Math.floor((game.tick-p.animTick)*spec.fps/20);frame=anim==='death'?Math.min(spec.columns-1,frame):frame%spec.columns;
    c.drawImage(img,frame*48,row*64,48,64,s.x-24,s.y-61,48,64);
    if(!title)this.label('Lữ Khách',s.x,s.y-69,'#e7e8c8',11);
  }
  mob(m,game,time){const s=this.point(m.x,m.y),c=this.c;if(s.x< -100||s.x>this.canvas.width+100)return;
    c.save();c.translate(s.x,s.y);if(m.hurtUntil>game.tick)c.globalAlpha=.6;
    c.fillStyle='#09272688';c.beginPath();c.ellipse(0,0,14,5,0,0,Math.PI*2);c.fill();
    if(m.type==='root'){rect(c,-6,-24,12,22,'#65704b');rect(c,-4,-28,9,12,'#8f9c60');rect(c,-16,-9,14,5,'#425d43');rect(c,3,-8,15,5,'#425d43');rect(c,-14,-29,5,20,'#6b8354');rect(c,9,-36,5,25,'#6b8354');rect(c,-21,-31,12,5,'#7b9a64');rect(c,12,-38,10,5,'#8cad74');rect(c,-4,-21,3,3,'#e9d38a');rect(c,3,-21,3,3,'#e9d38a');}
    else{const phase=Math.sin(time*.005+m.x)*2;rect(c,-12,-21+phase,24,17,'#1c4b54');rect(c,-10,-22+phase,19,12,'#699d9c');rect(c,-6,-26+phase,14,6,'#98c4ad');rect(c,-12,-10+phase,25,5,'#c1d0af');rect(c,-19,-16+phase,8,12,'#488b89');rect(c,8,-20+phase,10,9,'#3f7177');rect(c,3,-22+phase,4,4,m.type==='stalker'?'#eeab6a':'#ecdb9c');rect(c,5,-22+phase,2,2,'#172e2f');}
    c.restore();if(m.state==='windup'){this.label('!',s.x,s.y-47,'#efb377',18);c.strokeStyle='#eea66a';c.lineWidth=2;c.beginPath();c.arc(s.x,s.y,35,0,Math.PI*2);c.stroke();}
    this.label(m.name,s.x,s.y-37,'#d8d5b0',10);if(m.hp<m.maxHp){rect(c,s.x-18,s.y-33,36,3,'#18322b');rect(c,s.x-18,s.y-33,Math.max(1,36*m.hp/m.maxHp),3,'#c97962');}
  }
  boss(game,time){const b=game.boss,s=this.point(b.x,b.y),c=this.c;if(s.x< -180||s.x>this.canvas.width+180)return;
    for(let i=12;i>=0;i--){const x=s.x+Math.sin(time*.0016+i*.6)*21+i*6-48,y=s.y-i*8;pixelCircle(c,x,y,11-i*.25,'#274e4b');pixelCircle(c,x-2,y-3,8-i*.25,'#a7b9a6');rect(c,x-2,y-10,4,6,'#d4dac0');rect(c,x-3,y-4,6,2,'#587b72');}
    pixelCircle(c,s.x,s.y-8,23,'#344f4b');pixelCircle(c,s.x-2,s.y-13,19,'#d3d4b5');rect(c,s.x-21,s.y-27,7,19,'#e4dabb');rect(c,s.x+14,s.y-32,7,22,'#e4dabb');rect(c,s.x-12,s.y-17,8,7,'#234d4a');rect(c,s.x+5,s.y-17,8,7,'#234d4a');rect(c,s.x-10,s.y-16,4,3,'#caad67');rect(c,s.x+7,s.y-16,4,3,'#caad67');rect(c,s.x-12,s.y-3,26,5,'#526854');
    this.label('Mãng Cốt',s.x,s.y-139,'#dfc395',14);
    if(game.boss.phase>=3)for(const side of [-1,1]){const t=this.point(b.x+side*9,b.y);c.strokeStyle='#9cd9c0';c.lineWidth=3;c.strokeRect(t.x-18,t.y-18,36,36);this.label('◇',t.x,t.y+6,'#c4ecd3',22);}
  }
  warning(w,game){const c=this.c,s=this.point(w.x,w.y),progress=Math.min(1,(game.tick-w.start)/(w.at-w.start));c.save();c.strokeStyle=w.resolved?'#f7ca82':'#efac77';c.fillStyle=w.resolved?'#f5c17855':'#bc5d463b';c.lineWidth=2;c.setLineDash([6,4]);c.beginPath();
    if(w.shape==='cone'){const a=Math.atan2(-w.face.y,w.face.x);c.moveTo(s.x,s.y);c.arc(s.x,s.y,w.r*PPU,a-Math.PI/3,a+Math.PI/3);c.closePath();}
    else if(w.shape==='annulus'){c.arc(s.x,s.y,7*PPU,0,Math.PI*2);c.arc(s.x,s.y,3*PPU,0,Math.PI*2,true);}
    else c.arc(s.x,s.y,w.r*PPU,0,Math.PI*2);
    c.fill('evenodd');c.stroke();c.setLineDash([]);c.globalAlpha=.7;c.beginPath();c.arc(s.x,s.y,12+progress*12,-Math.PI/2,-Math.PI/2+progress*Math.PI*2);c.stroke();c.restore();
  }
  effect(e,game){const c=this.c,s=this.point(e.x,e.y),alpha=(e.end-game.tick)/(e.end-e.tick);c.save();c.globalAlpha=alpha;c.lineWidth=e.type==='cleave'?5:3;
    if(e.type==='slash'||e.type==='cleave'){const a=Math.atan2(-(e.face?.y||0),e.face?.x||1);c.strokeStyle='#f0d788';c.beginPath();c.arc(s.x,s.y,45+(1-alpha)*20,a-.9,a+.9);c.stroke();c.strokeStyle='#fff0b4';c.lineWidth=2;c.beginPath();c.arc(s.x,s.y,41+(1-alpha)*20,a-.7,a+.7);c.stroke();}
    else if(e.type==='heal'||e.type==='parry'){c.strokeStyle=e.type==='heal'?'#ade1b4':'#f4dd91';c.beginPath();c.arc(s.x,s.y-15,16+(1-alpha)*22,0,Math.PI*2);c.stroke();}
    else{c.strokeStyle='#ffe0a0';c.beginPath();c.moveTo(s.x-8,s.y-20);c.lineTo(s.x+9,s.y-4);c.moveTo(s.x+7,s.y-23);c.lineTo(s.x-7,s.y-3);c.stroke();}c.restore();
  }
  drawMini(game){const c=this.mini.getContext('2d'),w=168,h=80;c.imageSmoothingEnabled=false;rect(c,0,0,w,h,'#213e3d');rect(c,0,1,w,21,'#2a5660');rect(c,0,37,w,7,'#9b9869');
    for(let i=0;i<35;i++)rect(c,(i*53)%168,18+(i*17)%58,4,3,'#466c50');
    const p=game.player;rect(c,p.x/360*w-2,h/2-p.y*1.4-2,4,4,'#eaf0c0');const goal=game.goal();if(goal)rect(c,goal.x/360*w-2,h/2-goal.y*1.4-2,3,3,'#e8b765');
    c.strokeStyle='#d4d7b06b';c.strokeRect((this.camera.x-this.canvas.width/40)/360*w,20,Math.min(w,this.canvas.width/20/360*w),40);
  }
}
