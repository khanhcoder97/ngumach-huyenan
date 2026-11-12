const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {Compiler, CompilerOptions, JsonFileHandler} = require('inkjs/compiler/Compiler');
const root = path.resolve(__dirname, '../..');
const pinnedVersion=require('./package.json').dependencies.inkjs;
const installedVersion=JSON.parse(fs.readFileSync(path.join(__dirname,'node_modules/inkjs/package.json'),'utf8')).version;
if(installedVersion!==pinnedVersion)throw Error('Run npm ci: installed inkjs differs from pin');
const sourceDir = path.join(root, 'docs/narrative/workshop/ink');
const names = ['main.ink','p00_01.ink','p00_02.ink','p00_03.ink','p00_04.ink','p00_05.ink','c1_06.ink'];
const questForFile = file => file==='main.ink'?null:(file.startsWith('p00_')?'P00-'+file.slice(4,6):'C1-06');
const normalize = s => s.replace(/^\uFEFF/,'').replace(/\r\n?/g,'\n');
const hash = s => crypto.createHash('sha256').update(s).digest('hex');
const sources = Object.fromEntries(names.map(n=>[n,normalize(fs.readFileSync(path.join(sourceDir,n),'utf8'))]));
const errors=[];
for(const [name,text] of Object.entries(sources)) {
  if(text.includes('\uFFFD')||text.normalize('NFC')!==text) throw Error('Source must be valid NFC UTF-8: '+name);
  if(/^\s*EXTERNAL\s/m.test(text)) throw Error('Reading room cannot bind gameplay externals: '+name);
  for(const match of text.matchAll(/^INCLUDE\s+(.+)$/gm)) if(!(match[1].trim() in sources)) throw Error('Include outside locked authoring files');
}
const compiler = new Compiler(sources['main.ink'],new CompilerOptions('main.ink',[],false,(message,type)=>errors.push({message,type}),new JsonFileHandler(sources)));
const story = compiler.Compile();
if(!story || compiler.errors.length) throw Error(JSON.stringify(errors));
const scenes=[];
for(const [file,text] of Object.entries(sources)) {
  const blocks=[...text.matchAll(/^=== (\w+) ===\s*$/gm)];
  for(let i=0;i<blocks.length;i++) {
    const begin=blocks[i].index+blocks[i][0].length;
    const body=text.slice(begin,i+1<blocks.length?blocks[i+1].index:text.length);
    const tags=Object.fromEntries([...body.matchAll(/^# ([a-z]+):([^\n]+)$/gm)].map(m=>[m[1],m[2].trim()]));
    if(tags.scene) scenes.push({id:tags.scene,knot:blocks[i][1],questId:questForFile(file),kind:tags.kind||'SCENE',guard:tags.guard||null,cinemaId:tags.cinema||null,sourcePath:'docs/narrative/workshop/ink/'+file,sourceLine:text.slice(0,blocks[i].index).split('\n').length});
  }
}
if(new Set(scenes.map(s=>s.id)).size!==scenes.length) throw Error('Duplicate scene ID');
const canonical=['docs/production/Narrative_Depth_and_Discovery_vi.md','docs/production/Quest_and_Narrative_Production_Spec_vi.md','docs/production/Quest_Dialogue_Production_Data_vi.csv','docs/production/NPC_Actor_Production_Registry_vi.csv','Implementation/Content/Narrative/Cinema_Production_Pack_v1.json'];
const sourceRecords=Object.entries(sources).map(([n,s])=>({path:'docs/narrative/workshop/ink/'+n,sha256:hash(s)}));
const canonicalSources=canonical.map(p=>({path:p,sha256:hash(normalize(fs.readFileSync(path.join(root,p),'utf8')))}));
const manifest={schemaVersion:1,status:'AUTHORING_CANDIDATE',runtimeActivationAllowed:false,authority:'LOCAL_READING_ROOM_ONLY',compiler:'inkjs@'+pinnedVersion,sourceDigest:hash(JSON.stringify(sourceRecords)),sources:sourceRecords,canonicalSources,scenes,warnings:compiler.warnings};
const outputs={'ben_mua.preview.json':normalize(story.ToJson())+'\n','scene_manifest.json':JSON.stringify(manifest,null,2)+'\n'};
for(const [name,data] of Object.entries(outputs)) {
 const file=path.join(__dirname,name);
 if(process.argv.includes('--check')) {if(!fs.existsSync(file)||normalize(fs.readFileSync(file,'utf8'))!==data) throw Error(name+' is stale; npm run build then review');}
 else fs.writeFileSync(file,data);
}
for(const [title,output,files] of [
 ['Bến Mưa','BEN_MUA_SCREENPLAY_vi.md',names.filter(n=>n.startsWith('p00_'))],
 ['Thăng Long — Con dấu qua phố','THANG_LONG_C1_06_SCREENPLAY_vi.md',['c1_06.ink']]
]) {
 let md='# '+title+' — kịch bản đầy đủ, bản biên tập 2026-10-31\n\nBản thảo để đọc và biên tập; giữ mọi nhánh, gồm lựa chọn khác nhau nên đây không phải một lượt chơi tuyến tính. Mở reading room để đọc theo nhánh. Runtime activation OFF; không thay CSV/quest graph hoặc cinema source.\n\n';
 for(const [file,text] of Object.entries(sources)) if(files.includes(file)) {
   md+='## '+file.replace('.ink','').replace('_','-').toUpperCase()+'\n\n';
   for(const line of text.split('\n')) {
    if(line.startsWith('//')||line.startsWith('~'))continue;
    if(line.startsWith('==='))md+='\n### '+line.replaceAll('=','').trim()+'\n\n';
    else if(line.startsWith('# '))md+='> '+line.slice(2)+'\n\n';
    else if(line.startsWith('+ '))md+='\n- Lựa chọn: '+line.slice(2).replaceAll('[','').replaceAll(']','')+'\n';
    else if(line.startsWith('->'))md+='\nChuyển cảnh: '+line.slice(2).trim()+'.\n\n';
    else md+=line+'\n\n';
   }
 }
 md=md.trimEnd()+'\n';
 const manuscript=path.join(root,'docs/narrative/workshop',output);
 if(process.argv.includes('--check')) {if(normalize(fs.readFileSync(manuscript,'utf8'))!==md) throw Error('Generated manuscript is stale');}
 else fs.writeFileSync(manuscript,md);
}
console.log(JSON.stringify({status:'PASS_COMPILE',scenes:scenes.length,sourceDigest:manifest.sourceDigest,runtimeActivationAllowed:false,warnings:compiler.warnings}));
