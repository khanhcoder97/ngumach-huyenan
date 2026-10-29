import assert from 'node:assert/strict';
import {Game,PACKAGES,RIPPLES,RESCUES,distance} from '../engine.mjs';
let assertions=0;
function check(ok,label){assert.ok(ok,label);assertions++;}
function step(g,input){g.step(input);if(g.player.hp>0&&g.player.hp<70&&g.player.potions>0)g.action('potion');g.drain();}
function walk(g,x,y=0){for(let i=0;i<1800&&Math.hypot(g.player.x-x,g.player.y-y)>.35;i++){
  step(g,{x:x-g.player.x,y:y-g.player.y});if(g.player.hp<=0)throw Error('Bot died while walking to '+x);
}check(Math.hypot(g.player.x-x,g.player.y-y)<.5,'reached '+x+','+y+' by movement');}
function fight(g,predicate,complete){for(let i=0;i<8000&&!complete();i++){
  const target=g.hostile().filter(predicate).sort((a,b)=>distance(a,g.player)-distance(b,g.player))[0];
  if(!target){step(g,{});continue;}
  const d=distance(g.player,target);if(d>2.6)step(g,{x:target.x-g.player.x,y:target.y-g.player.y});
  else {g.action('cleave');g.action('attack');step(g,{});}
  if(g.player.hp<=0)throw Error('Bot died during fight: '+JSON.stringify({quest:g.quest,stage:g.flags.escortStage,potions:g.player.potions,level:g.player.level,mp:g.player.mp,mobs:g.hostile().filter(predicate).map(m=>({id:m.id,hp:m.hp}))}));
}check(complete(),'combat objective completed');}

// Full opening run uses normal move/interact/attack/step commands, no teleport/HP/quest injections.
const g=new Game();check(!g.accept(),'remote accept rejected');walk(g,42);check(g.interact('NPC_LYAN').kind==='offer','Ly An offers first quest');check(g.accept(),'accept near Ly An');
for(const obj of PACKAGES){walk(g,obj.x,obj.y);check(g.interact(obj.id)?.kind==='collected','collected unique package');}
check(g.flags.packages.length===3&&g.ready(),'all three package objectives ready');
check(g.interact('package0')===null&&g.flags.packages.length===3,'duplicate collection does not progress');
check(!g.turnIn(),'remote reward rejected');walk(g,64);check(g.turnIn(),'quest one reward');const firstCoin=g.player.coin;check(firstCoin===20&&!g.turnIn()&&g.player.coin===20,'reward only once');
check(g.accept(),'quest two accept');fight(g,m=>m.type==='fish',()=>g.flags.fish>=4);
for(const obj of RIPPLES){walk(g,obj.x,obj.y);check(g.interact(obj.id)?.kind==='discovery','water clues discovered');}
walk(g,64);check(g.turnIn(),'quest two turn-in');walk(g,42);check(g.accept(),'quest three accept');
fight(g,m=>m.type==='root',()=>g.flags.roots===3);
for(const obj of RESCUES){walk(g,obj.x,obj.y);check(g.interact(obj.id)?.kind==='discovery','rescued villager');}
// The lesson wave is avoided by ordinary movement; no artificial progress event.
for(let i=0;i<10;i++)step(g,{});walk(g,156,0);for(let i=0;i<80&&!g.flags.wave;i++)step(g,{x:1,y:0});
check(g.flags.wave,'tutorial wave avoided through movement');walk(g,64);check(g.turnIn(),'quest three turn-in');check(g.accept(),'escort accepted');
for(const checkpoint of [80,120]){
  walk(g,checkpoint);for(let i=0;i<150&&!g.mobs.some(m=>m.wave&&m.hp>0);i++)step(g,{});
  fight(g,m=>m.wave,()=>!g.mobs.some(m=>m.wave&&m.hp>0));for(let i=0;i<3;i++)step(g,{});
}
check(g.flags.escortStage===4,'two escort waves and checkpoints complete');walk(g,64);check(g.turnIn(),'escort turn-in');check(g.accept(),'boss quest accepted');
walk(g,176);fight(g,m=>m.type==='boss',()=>g.flags.boss);
walk(g,178);check(g.interact('seal')?.kind==='discovery','seal unlocks only after boss death');walk(g,188);
check(g.interact('NPC_CLASS_TRIAL')?.kind==='turnin','class confirmation offered');check(g.turnIn(),'fifth quest completed');
check(g.quest===5&&g.completed.length===5&&g.player.attack===26,'complete opening and starter weapon fixture');
walk(g,348);check(g.interact('gate')?.kind==='ending','eastern exit reached by movement');
const saved=g.save(),restored=new Game();check(restored.restore(saved)&&restored.quest===5&&restored.flags.boss,'save restores completed opening');
check(!restored.restore({...saved,quest:99}),'invalid quest save rejected');
check(!restored.restore({...saved,player:{...saved.player,x:NaN}}),'invalid numeric save rejected');

// Guard timing and confirmation, isolated fixtures rather than claiming full network implementation.
const guard=new Game();guard.quest=1;guard.active=true;guard.player.x=80;guard.player.face={x:1,y:0};
const mob=guard.mobs[0];mob.x=82;mob.y=0;guard.action('guard');const before=guard.player.hp;
guard.hurt(30,mob,true);guard.hurt(30,mob,true);
check(guard.player.hp===before-16,'front guard DR applied to both confirmed direct hits');
check(guard.player.intent===2&&guard.jobs.filter(j=>j.type==='counter').length===1,'one counter and resource grant per guard');
guard.player.hp=0;guard.action('respawn');check(guard.player.hp===guard.player.maxHp&&guard.player.x===24,'respawn restores safe position');
const whiff=new Game();whiff.action('guard');for(let i=0;i<8;i++)whiff.step();check(whiff.guard===null&&whiff.whiffEnd===28,'guard expiration starts one-second whiff');
for(let i=0;i<20;i++)whiff.step();check(whiff.tick===whiff.whiffEnd,'whiff end exclusive');
const blocked=new Game();blocked.player.x=56;blocked.player.y=7;blocked.move(1,0,11);check(blocked.player.x<56.5,'sweep cannot tunnel through house footprint');
const dead=new Game();dead.quest=0;dead.accept();dead.player.hp=1;dead.hurt(100,null,false);dead.hurt(100,null,false);
check(dead.drain().filter(e=>e.type==='death').length===1,'one death event while dead');
for(const [checkpoint,stage]of [[80,2],[120,4]]){const escort=new Game();escort.quest=3;escort.active=true;escort.completed=[0,1,2];escort.flags.escortCheckpoint=checkpoint;escort.flags.escortStage=stage;
  const copy=new Game();check(copy.restore(escort.save())&&copy.flags.escortStage===stage,'committed escort checkpoint survives reload '+checkpoint);}
console.log('PASS playable engine assertions:',assertions,'| five quests, boss, exit, save and combat gates');
