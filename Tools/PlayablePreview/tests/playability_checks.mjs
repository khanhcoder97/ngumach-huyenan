import assert from 'node:assert/strict';
import {Game} from '../engine.mjs';
import {SaveStore,decodeSave,exportSave} from '../save-store.mjs';
let checks=0;
const check=(ok,label)=>{assert.ok(ok,label);checks++;};
function fixture(){const g=new Game();g.quest=1;g.completed=[0];g.active=true;g.player.x=80;g.flags.packages=['package0','package1','package2'];return g;}
const g=fixture(),a=g.mobs[0],b=g.mobs[1];a.x=81;a.y=0;b.x=82;b.y=0;a.hp=b.hp=100;
check(!g.selectTarget('NPC_LYAN'),'NPC is not a hostile target');
check(!g.selectTarget('boss'),'inactive boss cannot be selected');
check(!g.selectTarget('east_0'),'locked phase monster cannot be selected');
check(g.selectTarget(b.id)&&g.target()===b,'explicit target lock');
g.rand=()=>.1;g.action('attack');for(let i=0;i<3;i++)g.step();
check(b.hp<100&&a.hp===100,'single-target hit prioritizes the selected valid target over a closer mob');
g.clearTarget();check(g.target()===null,'target can be cleared');
const first=g.cycleTarget();check(first===a,'cycle starts at nearest eligible target');
check(g.cycleTarget()!==a,'cycle moves to the next target');
b.x=115;g.selectTarget(b.id);const hp=b.hp;for(let i=0;i<10;i++)g.step();g.action('attack');for(let i=0;i<3;i++)g.step();
check(b.hp===hp,'locking a distant target does not bypass attack range');
b.hp=0;g.step();check(g.target()===null,'dead target lock is cleared');
g.selectTarget(a.id);g.quest=3;g.step();check(g.target()===null,'phase-hidden target is cleared');
const travel=fixture();travel.quest=2;travel.player.x=150;travel.action('dodge');check(travel.dash!==null,'dodge fixture started');
travel.travelHome();check(travel.player.x===24&&travel.dash===null&&travel.avoidEnd===0,'travel clears pending dash and immunity state');
const lesson=fixture();lesson.quest=2;lesson.flags.rescues=['rescue0','rescue1'];lesson.player.x=24;lesson.step();
check(!lesson.warnings.some(w=>w.kind==='lesson'),'lesson wave does not spawn at safe respawn after death');
lesson.player.x=148;lesson.step();check(lesson.warnings.some(w=>w.kind==='lesson'),'lesson wave still starts in the marsh');
const boss=fixture();boss.quest=4;boss.player.x=176;boss.step();check(boss.boss.active,'boss fixture activates');boss.player.x=24;
for(let i=0;i<202;i++)boss.step();const events=boss.drain();
check(!boss.boss.active&&events.filter(e=>e.type==='bossReset').length===1,'boss reset emits one audio/target lifecycle signal');
check(!events.some(e=>e.type==='bossDefeated')&&boss.player.coin===0,'reset does not grant a kill reward');

class MemoryStorage{
  constructor(){this.data=new Map();this.failKey=null;}
  getItem(key){return this.data.get(key)||null;}
  setItem(key,value){if(key===this.failKey)throw new Error('quota fixture');this.data.set(key,value);}
}
const memory=new MemoryStorage(),store=new SaveStore(memory,'qa'),original=fixture();
check(store.load().source==='empty','empty storage is explicit');store.write(original);check(store.load().game.quest===1,'existing v1 save shape remains loadable');
original.player.x=90;store.write(original);check(store.recovery().player.x===80,'previous valid save retained');
memory.setItem('qa','broken JSON');const fallback=store.load();check(fallback.source==='previous'&&fallback.game.player.x===80,'malformed primary recovers from valid previous save');
const backup=memory.getItem('qa.previous');store.write(original);check(memory.getItem('qa.previous')===backup,'invalid old data never replaces the recovery slot');
const exported=exportSave(original),candidate=decodeSave(exported);check(candidate.player.x===90&&candidate.quest===1,'export/import roundtrip preserves progress');
check(candidate.targetId===null,'transient target locks are not imported');
const before=memory.getItem('qa');memory.failKey='qa';original.player.x=94;assert.throws(()=>store.write(original));checks++;
check(memory.getItem('qa')===before,'failed primary write preserves committed progress');
const prior=store.recovery().player.x;memory.failKey='qa.previous';assert.throws(()=>store.write(original));checks++;
check(store.load().game.player.x===90&&store.recovery().player.x===prior,'failed backup write does not replace current progress');
for(const bad of ['not JSON',JSON.stringify({format:'wrong',fileVersion:1,save:original.save()}),JSON.stringify({format:'NGUMACH_BENMUA_LOCAL',fileVersion:2,save:original.save()}),JSON.stringify({...original.save(),quest:99}),JSON.stringify({...original.save(),player:{...original.player,x:'not a coordinate'}}),' '.repeat(64001)]){
  assert.throws(()=>decodeSave(bad));checks++;
}check(original.player.x===94,'invalid import does not mutate the running game');
const corrupt=new MemoryStorage();corrupt.setItem('bad','broken');const broken=new SaveStore(corrupt,'bad');check(broken.load().source==='invalid'&&corrupt.getItem('bad')==='broken','failed load does not overwrite a corrupt save');
const unavailable=new SaveStore({getItem(){throw new Error('blocked');}},'private');check(unavailable.load().source==='unavailable','blocked storage can still start an unsaved local game');
console.log('PASS playability/target/save assertions:',checks);
