const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const {Story}=require('inkjs');const {execFileSync}=require('node:child_process');
execFileSync(process.execPath,[path.join(__dirname,'build.cjs'),'--check'],{stdio:'inherit'});
const inputArg=process.argv.indexOf('--story');
const storyFile=inputArg>=0?path.resolve(process.argv[inputArg+1]):path.join(__dirname,'ben_mua.preview.json');
const data=fs.readFileSync(storyFile,'utf8').replace(/^\uFEFF/,'');
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'scene_manifest.json'),'utf8'));
assert.equal(manifest.runtimeActivationAllowed,false);
const expected=new Set(manifest.scenes.filter(s=>s.questId).map(s=>s.id));
const stateVars=[...new Set(manifest.sources.flatMap(source=>[...fs.readFileSync(path.resolve(__dirname,'../..',source.path),'utf8').matchAll(/^VAR\s+(\w+)\s*=/gm)].map(m=>m[1])))];
const visited=new Set(),seenStates=new Set();let branches=0,ends=0,transitions=0;
const make=()=>{const s=new Story(data);s.onError=(m)=>{throw Error(m);};return s;};
const queue=[];for(const knot of ['p01_rope','p02_bank','p03_call','p04_depart','p05_before']){const s=make();s.ChoosePathString(knot);queue.push({state:s.state.ToJson(),scene:null,seal:false,exit:false});}
while(queue.length){
 const node=queue.shift();const s=make();s.state.LoadJson(node.state);let scene=node.scene;let seal=node.seal;let lines=0;
 while(s.canContinue){
  assert.ok(++lines<1000,'Unbounded continue loop');const text=s.Continue();
  for(const tag of s.currentTags){if(tag.startsWith('scene:')){scene=tag.slice(6);visited.add(scene);}}
  if(text.includes('Tiếng Huyền Ấn'))assert.ok(seal,'Name revealed before simulated seal interaction');
 }
 if(scene==='READING_ROOM')continue;
 const vars=Object.fromEntries(stateVars.map(n=>[n,s.variablesState[n]]));
 const key=JSON.stringify({scene,vars,seal,choices:s.currentChoices.map(c=>c.text)});
 if(seenStates.has(key))continue;seenStates.add(key);assert.ok(seenStates.size<5000,'State budget exceeded');
 if(!s.currentChoices.length){assert.ok(node.exit,'Unintended dead end at '+scene);ends++;continue;}
 for(const choice of s.currentChoices){
  const clone=make();clone.state.LoadJson(s.state.ToJson());clone.ChooseChoiceIndex(choice.index);branches++;
  queue.push({state:clone.state.ToJson(),scene,seal:seal||(scene==='BM05_SEAL_INTERACTION'&&choice.text.startsWith('Mô phỏng: tương tác')),exit:choice.text==='Đóng bản đọc'});
 }
 transitions++;
}
for(const id of expected)assert.ok(visited.has(id),'Unreachable scene: '+id);
// Re-read from the same session, proving choices do not disappear after one visit.
const replay=make();for(let repeat=0;repeat<2;repeat++){replay.ChoosePathString('p01_rope');while(replay.canContinue)replay.Continue();assert.equal(replay.currentChoices.length,3);replay.ChooseChoiceIndex(0);while(replay.canContinue)replay.Continue();assert.ok(replay.currentChoices.length>=3);}
const canonical=require(path.resolve(__dirname,'../../Implementation/Content/Narrative/Cinema_Production_Pack_v1.json'));
for(const scene of manifest.scenes){if(scene.cinemaId){const ref=canonical.scenes.find(x=>x.sceneId===scene.cinemaId);assert.ok(ref,'Unknown cinema ref');assert.equal(ref.questId,scene.questId,'Cinema associated with wrong quest');}}
const packet=require(path.resolve(__dirname,'../../docs/narrative/workshop/muse_cinema_candidate.json'));
assert.equal(packet.runtimeActivationAllowed,false);
for(const scene of packet.scenes){const ref=canonical.scenes.find(s=>s.sceneId===scene.sceneId);assert.ok(ref);assert.equal(scene.durationSeconds,ref.durationSeconds);assert.equal(scene.triggerDescription,ref.triggerDescription);assert.equal(scene.shots.length,ref.shots.length);let total=0;for(let i=0;i<scene.shots.length;i++){const shot=scene.shots[i];assert.equal(shot.shotId,ref.shots[i].shotId);assert.equal(shot.durationSeconds,ref.shots[i].durationSeconds);assert.equal(shot.inSeconds,total);total+=shot.durationSeconds;assert.equal(shot.outSeconds,total);}assert.equal(total,scene.durationSeconds);}
assert.ok(ends>0,'No explicit ending exercised');
const result={status:'PASS_BRANCH_EXECUTION',sourceDigest:manifest.sourceDigest,reachableScenes:expected.size,choiceEdges:branches,uniqueDecisionStates:transitions,explicitEnds:ends,repeatRead:'PASS',sealRevealGate:'PASS',runtimeActivationAllowed:false,nativeGame:'UNVERIFIED',literaryQuality:'EDITORIAL_JUDGMENT_NOT_SCORED'};
console.log(JSON.stringify(result,null,2));
if(process.argv.includes('--report'))fs.writeFileSync(path.join(__dirname,'branch-report.json'),JSON.stringify(result,null,2)+'\n');
