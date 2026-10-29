// Local single-player playtest. No production HTTP, accounts, currency or save uploads.
export const QUESTS = ['Thư qua bến','Chuông không người','Dưới mặt đầm','Người giữ bờ','Mảnh ấn đầu tiên'];
export const NPCS = [{id:'NPC_LYAN',name:'Ly An',x:42,y:0,color:'#b9c8a9'},
  {id:'NPC_TA_VAN_KHANH',name:'Tạ Vân Khanh',x:64,y:0,color:'#b3cbd3'},
  {id:'NPC_MEDIC_BEN',name:'Thầy thuốc',x:30,y:3,color:'#d1b5a0'},
  {id:'NPC_FISHER_01',name:'Lão ngư',x:112,y:5,color:'#b4bda3'},
  {id:'NPC_CLASS_TRIAL',name:'Quan sát viên',x:188,y:0,color:'#bfc5dc'},
  {id:'NPC_BOAT_KEEPER',name:'Người giữ thuyền',x:343,y:0,color:'#c8b289'}];
export const PACKAGES = [36,44,52].map((x,i)=>({id:'package'+i,x,y:0,name:['Kiện buộc nút đôi','Kiện quấn vải','Kiện có dấu mực'][i]}));
export const RIPPLES = [122,132,142].map((x,i)=>({id:'ripple'+i,x,y:-1,name:'Gợn nước lạ'}));
export const RESCUES = [135,148].map((x,i)=>({id:'rescue'+i,x,y:0,name:'Dân mắc kẹt'}));
export const HERBS = [78,106,157,247,280].map((x,i)=>({id:'herb'+i,x,y:-5,name:'Linh thảo'}));
export const distance = (a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const insideCone=(origin,facing,target,radius,angle)=>{
  const d=distance(origin,target);return d<=radius && (d<1e-8 || ((target.x-origin.x)*facing.x+(target.y-origin.y)*facing.y)/d>=Math.cos(angle*Math.PI/360)-1e-8);
};
const baseMaxHp=l=>100+28*l+70,baseMaxMp=l=>50+12*l+40;
// Footprint obstacles for this procedural playtest only, not reviewed production nav.
const OBSTACLES=[{x1:57,x2:63,y1:5,y2:9},{x1:236,x2:242,y1:5,y2:9},{x1:249,x2:255,y1:5,y2:9}];
const walkable=(x,y)=>!OBSTACLES.some(r=>x>r.x1-.6&&x<r.x2+.6&&y>r.y1-.3&&y<r.y2+.3);
export const xpNext=l=>Math.ceil(100+50*l+25*l*l);

export class Game {
  constructor(save=null){
    this.tick=0;this.events=[];this.effects=[];this.jobs=[];this.randomState=0x7ab1cde;
    this.player={x:18,y:0,face:{x:1,y:0},hp:198,maxHp:198,mp:102,maxMp:102,level:1,xp:0,coin:0,potions:6,intent:0,attack:20,armor:10,anim:'idle',animTick:0};
    this.quest=0;this.active=false;this.completed=[];this.flags={packages:[],ripples:[],rescues:[],herbs:[],fish:0,roots:0,wave:false,escortStage:0,escortCheckpoint:64,boss:false,seal:false};
    this.cooldowns={};this.epoch=1;this.lastCombat=-1000;this.combo=0;this.comboEnd=0;this.guard=null;this.whiffEnd=0;this.dash=null;this.avoidStart=0;this.avoidEnd=0;
    this.escort={x:64,y:1,hp:180,maxHp:180};this.mobs=[];this.warnings=[];this.boss={id:'boss',type:'boss',name:'Mãng Cốt',x:178,y:0,hp:640,maxHp:640,attack:20,armor:6,phase:1,active:false,ready:0,cooldowns:{},idleSince:null};
    this.makeGroup('fishA',84,0,'fish',3);this.makeGroup('fishB',116,0,'fish',4);
    [126,138,151].forEach((x,i)=>this.makeGroup('root'+i,x,0,'root',1));
    this.makeGroup('east',270,0,'stalker',3);
    if(save)this.restore(save);
  }
  emit(type,data={}){this.events.push({type,tick:this.tick,...data});}
  drain(){const e=this.events;this.events=[];return e;}
  rand(){let x=this.randomState;x^=x<<13;x^=x>>>17;x^=x<<5;this.randomState=x>>>0;return this.randomState/4294967296;}
  makeGroup(group,x,y,type,count,wave=false){for(let i=0;i<count;i++){
    const dx=count>1?(i%2?2.4:-2.4):0,dy=count>1?(i-1)*2.2:0;
    // Onboarding preview chooses level1, not the server's REFERENCE_L5 fixture.
    // Art Bible base144/12/2.8 × archetype; HP ceil once. Not a spawn-level migration.
    const stats=type==='root'?{hp:159,attack:12,armor:3.08}:type==='stalker'?{hp:130,attack:13.8,armor:2.24}:{hp:116,attack:9,armor:1.96};
    this.mobs.push({id:group+'_'+i,group,type,wave,name:type==='fish'?'Cá Linh':type==='root'?'Rễ Nước':'Kẻ Rình Bờ',x:x+dx,y:y+dy,home:{x:x+dx,y:y+dy},hp:stats.hp,maxHp:stats.hp,attack:stats.attack,armor:stats.armor,state:'idle',ready:0,respawnAt:0,life:1});
  }}
  mobEnabled(m){if(m.wave)return this.quest===3&&this.active;
    // Quest waves/encounter replace overlapping ordinary spawns in this local instance.
    if(this.quest===3||this.quest===4)return false;
    if(m.type==='root')return this.quest>=2;if(m.type==='stalker')return this.quest>=5;return this.quest>=1;}
  hostile(){return [...this.mobs.filter(m=>m.hp>0&&this.mobEnabled(m)),...(this.boss.active&&this.boss.hp>0?[this.boss]:[])];}
  cooldown(action){return Math.max(0,((this.cooldowns[action]||0)-this.tick)/20);}
  animate(name,ticks=9){this.player.anim=name;this.player.animTick=this.tick;this.player.animUntil=this.tick+ticks;}
  move(dx,dy,distanceWu){const n=Math.hypot(dx,dy);if(!n)return;
    const steps=Math.ceil(distanceWu/.25),sx=dx/n*distanceWu/steps,sy=dy/n*distanceWu/steps;
    for(let i=0;i<steps;i++){const x=clamp(this.player.x+sx,3,356),y=clamp(this.player.y+sy,-11,9);
      if(walkable(x,this.player.y))this.player.x=x;if(walkable(this.player.x,y))this.player.y=y;}
    this.player.face={x:dx/n,y:dy/n};
  }
  faceTarget(){const nearest=this.hostile().sort((a,b)=>distance(a,this.player)-distance(b,this.player))[0];
    if(nearest&&distance(nearest,this.player)<=5){const d=distance(nearest,this.player);if(d>.01)this.player.face={x:(nearest.x-this.player.x)/d,y:(nearest.y-this.player.y)/d};}}
  action(action){
    if(action==='respawn'){if(this.player.hp<=0)this.respawn();return true;}
    if(this.player.hp<=0||this.cooldown(action)>0)return false;
    const p=this.player;
    if(action==='potion'){
      if(p.potions<=0){this.emit('notice',{text:'Đã hết thuốc. Tìm thầy thuốc ở bến.'});return false;}
      if(p.hp===p.maxHp&&p.mp===p.maxMp)return false;
      p.potions--;p.hp=Math.min(p.maxHp,p.hp+100);p.mp=Math.min(p.maxMp,p.mp+50);this.cooldowns.potion=this.tick+200;
      this.effects.push({type:'heal',x:p.x,y:p.y,tick:this.tick,end:this.tick+15});this.emit('heal');return true;
    }
    if(action==='attack'){
      if(this.tick<(this.busyUntil||0))return false;this.faceTarget();
      this.combo=this.tick>this.comboEnd?0:(this.combo+1)%3;this.comboEnd=this.tick+40;
      this.cooldowns.attack=this.tick+10;this.busyUntil=this.tick+10;this.animate('attack'+(this.combo+1),10);
      this.scheduleHit(3,1,4,90,1,'slash');this.emit('swing');return true;
    }
    const cost={guard:12,dash:16,cleave:22,dodge:0}[action];if(cost===undefined)return false;
    if(p.mp<cost){this.emit('notice',{text:'Không đủ nội lực. Dùng thuốc hoặc nghỉ ngoài giao tranh.'});return false;}
    if(this.tick<(this.busyUntil||0)&&action!=='dodge')return false;
    p.mp-=cost;this.cooldowns[action]=this.tick+{guard:200,dash:160,cleave:200,dodge:140}[action];
    if(action==='guard'){
      this.guard={end:this.tick+8,face:{...p.face},attack:p.attack,confirmed:false};this.whiffEnd=0;this.animate('skill1',8);this.emit('guardStart');
    }else if(action==='cleave'){
      this.faceTarget();this.busyUntil=this.tick+12;this.animate('skill3',12);
      [[2,.45],[5,.55],[8,.90]].forEach(([delay,coefficient])=>this.scheduleHit(delay,coefficient,4.4,100,5,'cleave'));this.emit('cleave');
    }else{
      if(action==='dodge'){this.guard=null;this.whiffEnd=0;this.avoidStart=this.tick+2;this.avoidEnd=this.tick+6;}
      else this.faceTarget();
      this.dash={face:{...p.face},remaining:4,hit:action==='dash'};this.animate(action==='dash'?'skill2':'dodge',10);this.emit('dash');
    }return true;
  }
  scheduleHit(delay,coefficient,range,angle,cap,type){this.jobs.push({at:this.tick+delay,epoch:this.epoch,coefficient,range,angle,cap,type,origin:{x:this.player.x,y:this.player.y},face:{...this.player.face}});}
  deal(target,coefficient,attack=this.player.attack,type='hit'){
    if(target.hp<=0)return;
    if(this.rand()>.9025){this.emit('number',{x:target.x,y:target.y,text:'Trượt',kind:'miss'});return;}
    const crit=this.rand()<.0525,damage=Math.max(1,Math.floor(attack*coefficient*100/(100+target.armor)*(crit?1.5:1)));
    target.hp=Math.max(0,target.hp-damage);target.hurtUntil=this.tick+3;this.lastCombat=this.tick;
    this.effects.push({type,x:target.x,y:target.y,tick:this.tick,end:this.tick+8,face:{...this.player.face}});
    this.emit('number',{x:target.x,y:target.y,text:String(damage),kind:crit?'crit':'damage'});this.emit('hit');
    if(target.hp===0){this.emit('kill',{target:target.id});
      if(target===this.boss){this.flags.boss=true;this.boss.active=false;this.warnings=[];this.addXp(120);this.emit('bossDefeated');}
      else{
        if(this.active&&this.quest===1&&target.type==='fish')this.flags.fish=Math.min(4,this.flags.fish+1);
        if(this.active&&this.quest===2&&target.type==='root')this.flags.roots=Math.min(3,this.flags.roots+1);
        this.addXp(12);target.state='dead';
        const group=this.mobs.filter(m=>m.group===target.group);if(group.every(m=>m.hp<=0)&&!target.wave)group.forEach(m=>m.respawnAt=this.tick+360);
      }
      this.emit('progress');
    }
  }
  hurt(damage,source,melee=true,noCounter=false){
    const p=this.player;if(p.hp<=0)return;
    if(this.tick>=this.avoidStart&&this.tick<this.avoidEnd){this.emit('number',{x:p.x,y:p.y,text:'Né!',kind:'good'});return;}
    let reduction=this.tick<this.whiffEnd?.2:0,eligible=false;
    if(this.guard&&this.tick<this.guard.end&&source&&insideCone(p,this.guard.face,source,4.4,120)){
      reduction=.7;eligible=melee&&!noCounter&&!this.guard.confirmed&&source.hp>0;
    }
    const final=Math.max(1,Math.floor(damage*100/(100+p.armor)*(1-reduction)));p.hp=Math.max(0,p.hp-final);this.lastCombat=this.tick;
    this.emit('number',{x:p.x,y:p.y,text:'−'+final,kind:'hurt'});this.emit('hurt');
    if(p.hp<=0){this.guard=null;this.whiffEnd=0;p.intent=0;this.epoch++;this.jobs=[];this.dash=null;this.animate('death',40);this.emit('death');return;}
    if(eligible){this.guard.confirmed=true;p.intent=Math.min(5,p.intent+2);
      this.jobs.push({at:this.tick+1,epoch:this.epoch,type:'counter',targetId:source.id,attack:this.guard.attack,face:{...this.guard.face}});
      this.emit('parry');this.effects.push({type:'parry',x:p.x,y:p.y,tick:this.tick,end:this.tick+10});
    }
  }
  addXp(amount){const p=this.player;p.xp+=amount;while(p.level<10&&p.xp>=xpNext(p.level)){
    p.xp-=xpNext(p.level);p.level++;const oldMax=p.maxHp;p.maxHp=baseMaxHp(p.level);p.maxMp=baseMaxMp(p.level);p.hp=Math.min(p.maxHp,p.hp+p.maxHp-oldMax);
    this.emit('level',{level:p.level});
  }if(p.level===10)p.xp=0;}
  accept(){const giver=NPCS.find(n=>n.id===(this.quest===0||this.quest===2?'NPC_LYAN':'NPC_TA_VAN_KHANH'));
    if(this.active||this.quest>=5||this.player.hp<=0||distance(this.player,giver)>4)return false;this.active=true;this.questXp=Math.floor(xpNext(this.player.level)*(this.quest===4?.55:.25));
    this.emit('accepted',{quest:this.quest});return true;}
  ready(){const f=this.flags;return this.active&&[f.packages.length===3,f.ripples.length===3&&f.fish>=4,f.roots>=3&&f.rescues.length===2&&f.wave,f.escortStage>=4,f.boss&&f.seal][this.quest];}
  turnIn(){const receiver=NPCS.find(n=>n.id===(this.quest===4?'NPC_CLASS_TRIAL':'NPC_TA_VAN_KHANH'));
    if(!this.ready()||this.player.hp<=0||distance(this.player,receiver)>4)return false;
    const q=this.quest,p=this.player;this.completed.push(q);this.active=false;this.quest++;
    this.addXp(this.questXp||Math.floor(xpNext(p.level)*(q===4?.55:.25)));if(q===0)p.coin+=20;if(q===3)p.coin+=30;
    if(q===1||q===2||q===3)p.potions+=2;
    if(q===4)p.attack=26; // Explicit local starter-weapon fixture; not a production ItemDefinition.
    p.hp=p.maxHp;p.mp=p.maxMp;this.emit('reward',{quest:q});return true;
  }
  interactables(){
    const f=this.flags,items=[...NPCS.filter(n=>n.id!=='NPC_CLASS_TRIAL'||f.boss)];
    if(this.quest===0&&this.active)items.push(...PACKAGES.filter(o=>!f.packages.includes(o.id)));
    if(this.quest===1&&this.active)items.push(...RIPPLES.filter(o=>!f.ripples.includes(o.id)));
    if(this.quest===2&&this.active)items.push(...RESCUES.filter(o=>!f.rescues.includes(o.id)));
    items.push(...HERBS.filter(o=>!f.herbs.includes(o.id)));
    if(this.quest>=2)items.push({id:'waystone',name:'Bia bến gỗ',x:150,y:3});
    if(this.quest===4&&this.active&&f.boss&&!f.seal)items.push({id:'seal',name:'Mảnh Huyền Ấn',x:178,y:0});
    if(this.quest>=5)items.push({id:'gate',name:'Cổng Thanh Lạc',x:348,y:0});
    return items;
  }
  nearest(){const goal=this.goal();return this.interactables().filter(o=>distance(o,this.player)<=4).sort((a,b)=>
    (a.id===goal?.id?-1:b.id===goal?.id?1:distance(a,this.player)-distance(b,this.player)))[0]||null;}
  interact(id){const obj=this.interactables().find(o=>o.id===id);if(!obj||distance(obj,this.player)>4||this.player.hp<=0)return null;
    const f=this.flags;
    if(id.startsWith('package')){if(!f.packages.includes(id))f.packages.push(id);this.emit('pickup');this.emit('progress');return {kind:'collected',name:obj.name};}
    if(id.startsWith('ripple')){if(!f.ripples.includes(id))f.ripples.push(id);this.emit('discovery');this.emit('progress');return {kind:'discovery',text:'Trên bờ không một tiếng động. Dưới mặt nước, một vòng chuông vừa ngân lên.'};}
    if(id.startsWith('rescue')){if(f.roots<3)return {kind:'discovery',text:'Rễ nước còn níu dưới chân họ. Hãy phá cả ba gốc rễ trước.'};
      if(!f.rescues.includes(id))f.rescues.push(id);this.emit('progress');return {kind:'discovery',text:'“Tôi nhìn thấy một người đứng dưới nước… người ấy có khuôn mặt giống ngươi.”'};}
    if(id.startsWith('herb')){if(!f.herbs.includes(id)){f.herbs.push(id);this.player.potions++;this.emit('pickup');}return {kind:'collected',name:'Linh thảo · nhận 1 thuốc hỗ trợ'};}
    if(id==='seal'){f.seal=true;this.emit('discovery');this.emit('progress');return {kind:'discovery',text:'Mảnh ấn ấm lên trong lòng bàn tay. Năm vết sáng chậm rãi khép thành một dấu. Huyền Ấn… ngươi chưa từng nghe cái tên ấy, vậy mà nó lại quen đến lạ.'};}
    if(id==='gate')return {kind:'ending'};
    if(id==='waystone')return {kind:'waystone'};
    if(id==='NPC_MEDIC_BEN')return {kind:'medic'};
    if(id==='NPC_FISHER_01')return {kind:'discovery',text:'“Cá bỏ chỗ nước sâu mà lên bờ. Người trong làng bảo mùa mưa… ta sống ở bến này sáu mươi năm, chưa mùa mưa nào như thế.”'};
    const giver=this.quest===0||this.quest===2?'NPC_LYAN':'NPC_TA_VAN_KHANH';
    const receiver=this.quest===4?'NPC_CLASS_TRIAL':'NPC_TA_VAN_KHANH';
    if(this.quest<5&&this.ready()&&id===receiver)return {kind:'turnin',quest:this.quest,npc:obj.name};
    if(this.quest<5&&!this.active&&id===giver)return {kind:'offer',quest:this.quest,npc:obj.name};
    return {kind:'discovery',text:this.quest>=5?'“Đường về Thanh Lạc đã mở. Nhưng tiếng chuông vẫn còn dưới nước… hãy nhớ điều ngươi đã nhìn thấy.”':'“Cứ đi đi. Khi đã tìm được điều cần tìm, hãy trở lại bến.”'};
  }
  objectives(){const f=this.flags;if(this.quest>=5)return [{text:'Đến cổng Thanh Lạc ở bờ Đông',done:false}];
    if(!this.active)return [{text:'Gặp '+(this.quest===0||this.quest===2?'Ly An':'Tạ Vân Khanh')+' để nhận nhiệm vụ',done:false}];
    const rows=[[[`Nhặt đủ ba kiện thư (${f.packages.length}/3)`,f.packages.length===3]],
      [[`Kiểm tra ba gợn nước (${f.ripples.length}/3)`,f.ripples.length===3],[`Hạ Cá Linh (${f.fish}/4)`,f.fish>=4]],
      [[`Phá Rễ Nước (${f.roots}/3)`,f.roots>=3],[`Cứu dân mắc kẹt (${f.rescues.length}/2)`,f.rescues.length===2],['Tránh đợt sóng từ đầm',f.wave]],
      [[`Hộ tống Ly An qua hai checkpoint (${Math.min(2,Math.floor(f.escortStage/2))}/2)`,f.escortStage>=4]],
      [['Hạ Mãng Cốt ở Đầm Chuông',f.boss],['Chạm mảnh Huyền Ấn',f.seal]]][this.quest];
    return [...rows.map(([text,done])=>({text,done})),{text:this.quest===4?'Xác nhận môn phái tại quan sát viên':'Trở lại gặp Tạ Vân Khanh',done:false}];
  }
  goal(){const f=this.flags;if(this.quest>=5)return {x:348,y:0,name:'Cổng Thanh Lạc'};
    if(!this.active)return NPCS.find(n=>n.id===(this.quest===0||this.quest===2?'NPC_LYAN':'NPC_TA_VAN_KHANH'));
    if(this.ready())return NPCS.find(n=>n.id===(this.quest===4?'NPC_CLASS_TRIAL':'NPC_TA_VAN_KHANH'));
    if(this.quest===0)return PACKAGES.find(o=>!f.packages.includes(o.id));
    if(this.quest===1)return RIPPLES.find(o=>!f.ripples.includes(o.id))||this.mobs.find(m=>m.type==='fish'&&m.hp>0);
    if(this.quest===2)return (f.roots<3?this.mobs.find(m=>m.type==='root'&&m.hp>0):RESCUES.find(o=>!f.rescues.includes(o.id)))||{x:148,y:0,name:'Vùng sóng'};
    if(this.quest===3)return {x:f.escortStage<2?80:120,y:0,name:'Đường hộ tống Ly An'};
    return {x:f.boss?178:170,y:0,name:f.boss?'Mảnh Huyền Ấn':'Đầm Chuông'};
  }
  step(input={x:0,y:0}){
    this.tick++;const p=this.player;if(p.hp<=0)return;
    this.effects=this.effects.filter(e=>e.end>this.tick);
    if(this.guard&&this.tick>=this.guard.end){if(!this.guard.confirmed)this.whiffEnd=this.tick+20;this.guard=null;}
    if(this.dash){this.move(this.dash.face.x,this.dash.face.y,11/4);if(--this.dash.remaining===0){if(this.dash.hit){this.scheduleHit(1,1.5,4,90,1,'slash');p.intent=Math.min(5,p.intent+1);}this.dash=null;}}
    else if((input.x||input.y)&&this.tick>=(this.busyUntil||0)){this.move(input.x,input.y,.3);if(p.anim!=='walk'){p.anim='walk';p.animTick=this.tick;}}
    else if(this.tick>=(p.animUntil||0)){p.anim='idle';}
    const due=this.jobs.filter(j=>j.at<=this.tick);this.jobs=this.jobs.filter(j=>j.at>this.tick);
    for(const j of due){if(j.epoch!==this.epoch||p.hp<=0)continue;
      if(j.type==='counter'){const target=this.hostile().find(m=>m.id===j.targetId);if(target&&insideCone(p,j.face,target,4.4,120))this.deal(target,1.8,j.attack,'parry');continue;}
      this.effects.push({type:j.type,x:j.origin.x,y:j.origin.y,face:j.face,tick:this.tick,end:this.tick+6});
      this.hostile().filter(m=>insideCone(j.origin,j.face,m,j.range,j.angle)).sort((a,b)=>distance(j.origin,a)-distance(j.origin,b)).slice(0,j.cap).forEach(m=>this.deal(m,j.coefficient));
    }
    for(const m of this.mobs){
      if(m.hp<=0){if(m.respawnAt&&this.tick>=m.respawnAt){m.hp=m.maxHp;m.x=m.home.x;m.y=m.home.y;m.state='idle';m.respawnAt=0;m.life++;}continue;}
      if(!this.mobEnabled(m))continue;
      if(distance(p,m.home)>16){m.state='return';const d=distance(m,m.home);if(d>.2){m.x+=(m.home.x-m.x)/d*.18;m.y+=(m.home.y-m.y)/d*.18;}else{m.hp=m.maxHp;m.state='idle';}continue;}
      const d=distance(m,p);
      if(m.state==='windup'){
        if(this.tick>=m.ready){if(distance(m,p)<3)this.hurt(m.attack,m,true);m.state='recover';m.ready=this.tick+26;}continue;
      }
      if(m.state==='recover'&&this.tick<m.ready)continue;
      if(d<=7){this.lastCombat=this.tick;if(d>2){m.x+=(p.x-m.x)/d*.13;m.y+=(p.y-m.y)/d*.13;m.state='chase';}else{m.state='windup';m.ready=this.tick+13;}}
      else m.state='idle';
    }
    if(this.quest===2&&this.active&&this.flags.rescues.length===2&&!this.flags.wave&&!this.warnings.some(w=>w.kind==='lesson')&&this.tick>=(this.lessonRetry||0)){
      this.warnings.push({kind:'lesson',shape:'circle',x:p.x,y:p.y,r:4,start:this.tick,at:this.tick+26,end:this.tick+32});this.emit('warning',{text:'Sóng trào! Rời vòng đỏ hoặc nhấn Shift để né.'});}
    this.stepEscort();this.stepBoss();
    for(const w of this.warnings){if(!w.resolved&&this.tick>=w.at){w.resolved=true;
      const hit=w.shape==='cone'?insideCone(w,w.face,p,w.r,120):w.shape==='annulus'?distance(w,p)>=3&&distance(w,p)<=7:distance(w,p)<=w.r;
      const avoided=this.tick>=this.avoidStart&&this.tick<this.avoidEnd;
      if(w.kind==='lesson'){if(!hit||avoided){this.flags.wave=true;this.emit('progress');this.emit('notice',{text:'Ngươi đã tránh được thủy triều.'});}else{this.hurt(20,null,false);this.lessonRetry=this.tick+60;}}
      else if(hit)this.hurt(w.damage,this.boss,w.shape==='cone');
    }}this.warnings=this.warnings.filter(w=>w.end>this.tick);
    if(this.tick%20===0){p.mp=Math.min(p.maxMp,p.mp+(this.tick-this.lastCombat>100?5:2));if(this.tick-this.lastCombat>100)p.hp=Math.min(p.maxHp,p.hp+4);}
  }
  stepEscort(){if(this.quest!==3||!this.active)return;const f=this.flags,e=this.escort,p=this.player;
    const waveAlive=this.mobs.some(m=>m.wave&&m.hp>0);
    if(waveAlive)return;
    if(f.escortStage===1){f.escortStage=2;f.escortCheckpoint=80;this.emit('progress');}
    if(f.escortStage===3){f.escortStage=4;f.escortCheckpoint=120;this.emit('progress');this.emit('notice',{text:'Ly An đã qua bờ an toàn. Trở về báo Tạ Vân Khanh.'});return;}
    if(f.escortStage>=4)return;
    const stop=f.escortStage<2?80:120;
    const escortTarget=Math.abs(p.x-stop)<4?{x:stop,y:1}:p;
    if(distance(e,escortTarget)>.7&&distance(e,p)<15){const d=distance(e,escortTarget);e.x+=(escortTarget.x-e.x)/d*.24;e.y+=(escortTarget.y-e.y)/d*.24;}
    if(e.x>=stop-1){e.x=stop;f.escortStage=stop===80?1:3;this.makeGroup('escort'+stop,stop+3,0,stop===80?'fish':'root',3,true);this.emit('warning',{text:'Phục kích! Bảo vệ đường đi của Ly An.'});}
  }
  stepBoss(){const b=this.boss,p=this.player;
    if(this.quest!==4||!this.active||this.flags.boss)return;
    if(!b.active&&distance(b,p)<13){b.active=true;b.ready=this.tick+35;this.emit('bossStart');}
    if(!b.active)return;
    if(distance(b,p)>22){if(b.idleSince===null)b.idleSince=this.tick;if(this.tick-b.idleSince>=200){b.hp=b.maxHp;b.active=false;b.phase=1;b.cooldowns={};this.warnings=[];this.emit('notice',{text:'Mãng Cốt đã lặn trở lại. Encounter được đặt lại.'});}return;}b.idleSince=null;
    b.phase=b.hp<=b.maxHp*.3?3:b.hp<=b.maxHp*.6?2:1;
    if(this.tick<b.ready||this.warnings.some(w=>w.kind==='boss'&&w.end>this.tick))return;
    let kind=['C','B','A'].find(k=>(b.cooldowns[k]||0)<=this.tick);if(!kind)return;
    const d=distance(b,p)||1,face={x:(p.x-b.x)/d,y:(p.y-b.y)/d};let w={kind:'boss',start:this.tick,resolved:false};
    if(kind==='A')Object.assign(w,{shape:'cone',x:b.x,y:b.y,face,r:8,at:this.tick+18,damage:b.attack*1.2});
    if(kind==='B')Object.assign(w,{shape:'circle',x:p.x,y:p.y,r:4,at:this.tick+24,damage:b.attack*1.5});
    if(kind==='C')Object.assign(w,{shape:'annulus',x:b.x,y:b.y,r:7,at:this.tick+20,damage:b.attack*1.3});
    w.end=w.at+6;this.warnings.push(w);b.cooldowns[kind]=this.tick+{A:80,B:180,C:240}[kind];b.ready=w.at+Math.ceil((kind==='A'?16:20)*(b.phase>=2?.8:1));
    this.emit('bossWarning',{attack:kind,text:{A:'Quét thân — tránh vùng quạt!',B:'Lặn trồi — rời điểm nước xoáy!',C:'Vòng bọt — vào tâm hoặc ra ngoài vòng!'}[kind]});
  }
  respawn(){const p=this.player;p.x=24;p.y=0;p.hp=p.maxHp;p.mp=p.maxMp;p.intent=0;this.guard=null;this.whiffEnd=0;this.warnings=[];this.jobs=[];this.dash=null;this.epoch++;
    this.boss.active=false;this.boss.hp=this.boss.maxHp;this.boss.phase=1;this.boss.cooldowns={};this.boss.idleSince=null;
    if(this.quest===3){this.mobs=this.mobs.filter(m=>!m.wave);this.escort.x=this.flags.escortCheckpoint;this.escort.y=1;this.flags.escortStage=this.flags.escortCheckpoint>=120?4:this.flags.escortCheckpoint>=80?2:0;}
    this.lastCombat=this.tick-200;this.animate('idle');this.emit('respawn');
  }
  travelHome(){if(this.quest<2||this.player.hp<=0)return false;this.player.x=24;this.player.y=0;this.guard=null;this.whiffEnd=0;this.player.intent=0;this.epoch++;this.jobs=[];this.warnings=[];return true;}
  save(){return {version:1,quest:this.quest,active:this.active,questXp:this.questXp,completed:this.completed,flags:this.flags,player:{...this.player},escort:{...this.escort}};}
  restore(s){if(!s||s.version!==1||!Number.isInteger(s.quest)||s.quest<0||s.quest>5||!Array.isArray(s.completed)||s.completed.length!==s.quest)return false;
    if(!s.completed.every((q,i)=>q===i)||typeof s.active!=='boolean'||!s.player||!s.flags)return false;
    const p=s.player,f=s.flags,fields=['x','y','hp','mp','level','xp','coin','potions'];if(fields.some(k=>!Number.isFinite(p[k])))return false;
    if(!Number.isInteger(p.level)||p.level<1||p.level>10||p.x<3||p.x>356||p.y< -11||p.y>9)return false;
    for(const [key,allowed] of [['packages',PACKAGES],['ripples',RIPPLES],['rescues',RESCUES],['herbs',HERBS]]){
      if(!Array.isArray(f[key])||new Set(f[key]).size!==f[key].length||f[key].some(id=>!allowed.some(a=>a.id===id)))return false;}
    if(!Number.isInteger(f.escortStage)||f.escortStage<0||f.escortStage>4||![64,80,120].includes(f.escortCheckpoint))return false;
    if(!Number.isInteger(f.fish)||f.fish<0||f.fish>4||!Number.isInteger(f.roots)||f.roots<0||f.roots>3)return false;
    if(['wave','boss','seal'].some(k=>typeof f[k]!=='boolean'))return false;
    this.quest=s.quest;this.active=s.quest<5&&s.active;this.completed=[...s.completed];this.flags=structuredClone(f);
    this.player={...this.player,...Object.fromEntries(fields.map(k=>[k,p[k]]))};this.player.maxHp=baseMaxHp(p.level);this.player.maxMp=baseMaxMp(p.level);
    this.player.hp=clamp(p.hp,0,this.player.maxHp);this.player.mp=clamp(p.mp,0,this.player.maxMp);this.player.coin=clamp(Math.floor(p.coin),0,999999);this.player.potions=clamp(Math.floor(p.potions),0,99);
    this.player.xp=clamp(Math.floor(p.xp),0,xpNext(p.level)-1);this.player.attack=s.quest>=5?26:20;
    this.questXp=Number.isFinite(s.questXp)?clamp(Math.floor(s.questXp),0,100000):Math.floor(xpNext(p.level)*.25);
    this.escort.x=this.flags.escortCheckpoint;this.escort.y=1;
    // Transient combat state is not loaded; escort waves restart at the committed checkpoint.
    if(this.quest===3&&this.active)this.flags.escortStage=this.flags.escortCheckpoint>=120?4:this.flags.escortCheckpoint>=80?2:0;
    if(this.flags.boss)this.boss.hp=0;
    return true;
  }
}
