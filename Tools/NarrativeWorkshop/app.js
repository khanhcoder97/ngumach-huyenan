(() => {
'use strict';
const article=document.querySelector('#story'),choices=document.querySelector('#choices'),status=document.querySelector('#status');
const titles={p01_rope:'THƯ QUA BẾN',p02_bank:'CHUÔNG KHÔNG NGƯỜI',p03_call:'DƯỚI MẶT ĐẦM',p04_depart:'NGƯỜI GIỮ BỜ',p05_before:'MẢNH ẤN ĐẦU TIÊN',tl_arrival:'THĂNG LONG · CON DẤU QUA PHỐ'};
let story,storyData,manifest,currentScene,route=[];
const speakers=['Ly An','Tạ Vân Khanh','Dân chài','Người chèo đò','Hạ Mặc','Sầm Chủ Quỹ','Thợ phụ Bách Công','Quan thư lầu'];
function fail(error){document.body.dataset.readerReady='error';status.textContent='Không mở được bản thảo: '+error.message;}
function paragraph(text){
 const p=document.createElement('p');
 if(/^(BẢN ĐỌC|TRACKER|KẾT TUYẾN BẢN ĐỌC)/.test(text))p.className='annotation';
 const speaker=speakers.find(n=>text.startsWith(n+':'));
 if(speaker){p.classList.add('speech');const label=document.createElement('span');label.className='speaker';label.textContent=speaker;p.append(label,document.createTextNode(text.slice(speaker.length+1).trim()));}
 else p.textContent=text;
 p.dataset.scene=currentScene||'';article.append(p);
}
function advance(){
 choices.replaceChildren();let budget=0;
 while(story.canContinue){if(++budget>1000)throw Error('Vượt giới hạn đoạn đọc');const text=story.Continue().trim();for(const tag of story.currentTags)if(tag.startsWith('scene:'))currentScene=tag.slice(6);if(text)paragraph(text);}
 for(const choice of story.currentChoices){const b=document.createElement('button');b.textContent=choice.text;b.addEventListener('click',()=>{route.push({scene:currentScene,choice:choice.text});const mark=document.createElement('p');mark.className='past-choice';mark.textContent=choice.text;article.append(mark);const count=article.children.length;story.ChooseChoiceIndex(choice.index);advance();article.children[count]?.scrollIntoView({block:'start'});choices.querySelector('button')?.focus({preventScroll:true});});choices.append(b);}
 const meta=manifest.scenes.find(s=>s.id===currentScene);const entries={'P00-01':'p01_rope','P00-02':'p02_bank','P00-03':'p03_call','P00-04':'p04_depart','P00-05':'p05_before','C1-06':'tl_arrival'};const entry=meta?entries[meta.questId]:null;document.querySelector('#chapter').textContent=titles[entry]||'BẢN ĐỌC';document.querySelectorAll('[data-entry]').forEach(b=>b.classList.toggle('active',b.dataset.entry===entry));
 document.body.dataset.readerReady='true';document.body.dataset.scene=currentScene||'';
 status.textContent=story.currentChoices.length?'Chọn cách phản hồi để đọc tiếp.':'Đã hết nhánh đọc. Có thể mở lại nhiệm vụ ở cột bên.';
}
function start(entry){story=new inkjs.Story(storyData);story.onError=(m)=>{throw Error(m);};article.replaceChildren();route=[];currentScene=null;document.querySelector('#chapter').textContent=titles[entry]||'BẢN ĐỌC';document.querySelectorAll('[data-entry]').forEach(b=>b.classList.toggle('active',b.dataset.entry===entry));story.ChoosePathString(entry);advance();}
document.querySelector('#annotations').addEventListener('change',e=>document.body.classList.toggle('show-annotations',e.target.checked));
document.querySelectorAll('[data-entry]').forEach(b=>b.addEventListener('click',()=>{try{start(b.dataset.entry);}catch(e){fail(e);}}));
document.querySelector('#restart').addEventListener('click',()=>start('p01_rope'));
document.querySelector('#export').addEventListener('click',()=>{const payload={status:'READER_NOTES_NOT_APPROVAL',sourceDigest:manifest.sourceDigest,scene:currentScene,route,note:document.querySelector('#note').value,runtimeActivationAllowed:false};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='ben-mua-reader-notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
Promise.all([fetch('/story.json').then(r=>{if(!r.ok)throw Error('Thiếu compiled story');return r.text();}),fetch('/manifest.json').then(r=>{if(!r.ok)throw Error('Thiếu source manifest');return r.json();})]).then(([data,m])=>{
 storyData=data;manifest=m;if(m.runtimeActivationAllowed!==false)throw Error('Bản đọc phải tách runtime');
 document.querySelector('#version').textContent='Bản thảo '+m.sourceDigest.slice(0,12)+' · '+m.scenes.filter(s=>s.kind==='SCENE').length+' cảnh · '+m.scenes.filter(s=>s.kind==='CHECKPOINT').length+' mốc mô phỏng';start('p01_rope');
 const smoke=new URLSearchParams(location.search).get('smoke');
 if(smoke==='thang-long'){
  document.querySelector('[data-entry="tl_arrival"]').click();
  choices.querySelector('button').click();
  document.body.dataset.browserSmoke=article.textContent.includes('Bắt đầu từ hóa đơn.')&&document.querySelector('#chapter').textContent===titles.tl_arrival&&document.querySelector('[data-entry="tl_arrival"]').classList.contains('active')?'pass':'fail';
 }else if(smoke){choices.querySelector('button').click();document.body.dataset.browserSmoke=article.textContent.includes('Còn nguyên. May thật.')&&choices.children.length>=3?'pass':'fail';}
}).catch(fail);
})();
