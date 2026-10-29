import {Game,QUESTS,xpNext,distance} from './engine.mjs';
import {Renderer} from './renderer.mjs';
const $=id=>document.getElementById(id), QA=new URLSearchParams(location.search).has('qa');
const SAVE=QA?'ngumach.benmua.qa.v1':'ngumach.benmua.local.v1', OPTIONS=QA?'ngumach.benmua.qa.options.v1':'ngumach.benmua.options.v1';
let content,game,renderer,started=false,modal=false,opener=null,accumulator=0,previous=0,lastSave=0,lastHud=0,frameCount=0,fps=0,fpsAt=0;
let touch={x:0,y:0},stickPointer=null,needsRelease=true,held=new Set(),uiStamp='',saveWarning=false,walkGoal=null;
const options={volume:.35,music:true,rain:true,reduced:false};
try{const stored=JSON.parse(localStorage.getItem(OPTIONS)||'null');if(stored){if(Number.isFinite(stored.volume))options.volume=Math.max(0,Math.min(1,stored.volume));for(const k of ['music','rain','reduced'])if(typeof stored[k]==='boolean')options[k]=stored[k];}}catch{}

class Sound{
  constructor(){this.voices=[];this.music=null;this.ambience=null;this.enabled=true;this.last={};}
  play(path,gain=1){if(!this.enabled||!started)return;const now=performance.now();if(now-(this.last[path]||-1000)<85)return;this.last[path]=now;
    this.voices=this.voices.filter(a=>!a.ended&&!a.paused);if(this.voices.length>=8)this.voices.shift().pause();
    const a=new Audio('/audio/'+path);a.volume=options.volume*gain;this.voices.push(a);a.play().catch(()=>{});
  }
  track(boss=false){const path=boss?'boss_mang_cot.ogg':'ben_mua.ogg';if(this.trackName!==path){if(this.music)this.music.pause();this.music=new Audio('/audio/music/'+path);this.music.loop=true;this.trackName=path;}
    if(!this.ambience){this.ambience=new Audio('/audio/ambience/rain_light.ogg');this.ambience.loop=true;}this.apply();
  }
  apply(){if(this.music){this.music.volume=options.volume*.55;if(this.enabled&&options.music&&started)this.music.play().catch(()=>{});else this.music.pause();}
    if(this.ambience){this.ambience.volume=options.volume*.22;if(this.enabled&&options.rain&&started)this.ambience.play().catch(()=>{});else this.ambience.pause();}
    $('sound-btn').textContent=this.enabled?'♫':'♪̸';$('sound-btn').setAttribute('aria-label',this.enabled?'Tắt âm thanh':'Bật âm thanh');
  }
}
const sound=new Sound();
function notice(text){const node=document.createElement('div');node.textContent=text;$('toasts').append(node);setTimeout(()=>node.remove(),3300);}
function resetControls(){held.clear();touch={x:0,y:0};walkGoal=null;needsRelease=true;$('stick').style.transform='';if(stickPointer!==null){try{$('joystick').releasePointerCapture(stickPointer);}catch{}stickPointer=null;}}
function save(){if(!started||!game)return;try{localStorage.setItem(SAVE,JSON.stringify(game.save()));}catch{if(!saveWarning){notice('Trình duyệt không cho tự lưu. Hãy giữ tab để tiếp tục hành trình.');saveWarning=true;}}}
function text(tag,text,cls){const node=document.createElement(tag);node.textContent=text;if(cls)node.className=cls;return node;}
function openModal(title,body,actions=[],kicker='HÀNH TRÌNH BẾN MƯA'){
  if(!modal)opener=document.activeElement;modal=true;resetControls();$('modal-title').textContent=title;$('modal-kicker').textContent=kicker;
  $('modal-content').replaceChildren();if(typeof body==='string')$('modal-content').append(text('p',body));else $('modal-content').append(body);
  $('modal-actions').replaceChildren();for(const [label,callback,primary]of actions){const b=text('button',label,primary?'primary':'');b.addEventListener('click',callback);$('modal-actions').append(b);}
  $('modal-backdrop').classList.remove('hidden');$('close-modal').focus();sound.play('sfx/ui/panel_open_v01.wav',.5);
}
function closeModal(){if(game?.player.hp<=0)return;modal=false;$('modal-backdrop').classList.add('hidden');resetControls();opener?.focus?.();sound.play('sfx/ui/panel_close_v01.wav',.5);}
function dialogue(q,type){return content.dialogue.find(d=>d.quest_id==='P00-0'+(q+1)&&d.node_type===type)?.text_vi||'Có những lời phải tới đúng người trước đã.';}
function interact(){if(!started||modal||game.player.hp<=0)return;const target=game.nearest();if(!target){notice('Hãy tới gần NPC hoặc vật thể có dấu sáng rồi nhấn E.');return;}
  const result=game.interact(target.id);if(!result)return;
  if(result.kind==='collected'){notice(result.name);processEvents();save();return;}
  if(result.kind==='offer'){
    const q=result.quest;openModal(result.npc,dialogue(q,'OFFER'),[['Để sau',closeModal],['Nhận nhiệm vụ',()=>{game.accept();closeModal();processEvents();save();},true]],`P00-0${q+1} · ${QUESTS[q]}`);
  }else if(result.kind==='turnin'){
    const q=result.quest,fragment=document.createDocumentFragment();fragment.append(text('p',dialogue(q,'TURN_IN')));
    fragment.append(text('p',q===4?'Minh Kiếm · Một lời thề đã có từ ngày bước xuống bến. Giờ đây, ngươi đã hiểu mình muốn bảo vệ điều gì.':'Hoàn thành nhiệm vụ để nhận hành trang cho đoạn đường kế tiếp.'));
    openModal(result.npc,fragment,[['Nhận thưởng',()=>{if(game.turnIn()){closeModal();processEvents();save();if(game.quest===5)ending(false);}},true]],`P00-0${q+1} · HOÀN THÀNH`);
  }else if(result.kind==='waystone'){
    openModal('Bia bến gỗ','Chạm vào vết khắc còn ấm. Con đường trở về bến hiện lên trong ký ức.',[['Ở lại',closeModal],['Trở về Bến Gỗ',()=>{game.travelHome();closeModal();save();},true]]);
  }else if(result.kind==='medic'){
    openModal('Thầy thuốc','“Mưa ở đây ngấm vào người lâu lắm. Nghỉ một lát, rồi hãy đi tiếp.”',[['Nghỉ và hồi phục',()=>{game.player.hp=game.player.maxHp;game.player.mp=game.player.maxMp;closeModal();save();notice('Khí huyết và nội lực đã hồi phục.');},true],['Mua 3 thuốc · 10 Đồng',()=>{if(game.player.coin>=10){game.player.coin-=10;game.player.potions+=3;closeModal();save();notice('Đã nhận 3 thuốc.');}else notice('Cần 10 Đồng. Bạn vẫn có thể nghỉ hồi phục miễn phí.');}]]);
  }else if(result.kind==='ending')ending(true);
  else openModal(target.name,result.text,[['Tiếp tục',()=>{closeModal();processEvents();save();},true]],'DẤU VẾT DƯỚI MƯA');
}
function ending(atGate){const body=document.createDocumentFragment();body.append(text('p','Mảnh ấn đã thức giấc. Sau lưng, Bến Mưa vẫn phủ một làn mưa mỏng. Phía trước, những cánh cờ Thanh Lạc chờ một người mang theo lá thư chưa có lời giải.'));
  body.append(text('p',atGate?'Bạn đã chơi hết tuyến mở đầu của bản thử này. Các chương tiếp theo sẽ được nối vào sau. Có thể tiếp tục khám phá bờ Đông, luyện kỹ năng và thu thập linh thảo.':'Đã hoàn thành 5 nhiệm vụ mở đầu. Vũ khí Mưa Khởi đã vào túi, tấn công tăng lên 26 trong bản chơi thử. Bạn có thể đi tiếp tới cổng phía Đông hoặc khám phá quanh bến.'));
  openModal('Một lời thề dưới mưa',body,[['Tiếp tục khám phá',closeModal,true],['Xem hành trang',bag]],'HOÀN THÀNH MỞ ĐẦU');
}
function bag(){const b=document.createDocumentFragment();const items=[['✚','Thuốc hỗ trợ','Hồi 100 HP và 50 MP · phím Q · hồi10 giây',game.player.potions],['❧','Linh thảo','Đã hái trên hành trình',game.flags.herbs.length]];
  if(game.completed.includes(0))items.push(['▤','Áo Mưa Khởi','Thưởng Thư qua bến · ngoại hình tạm',1]);
  if(game.completed.includes(2))items.push(['♜','Giày Mưa Khởi','Thưởng Dưới mặt đầm · ngoại hình tạm',1]);
  if(game.completed.includes(4))items.push(['⚔','Kiếm Mưa Khởi','Đang trang bị · tấn công26 trong bản thử',1]);
  for(const [icon,name,detail,count]of items){const row=text('div','','item-row');row.append(text('span',icon,'item-icon'));const d=document.createElement('div');d.append(text('strong',`${name} ×${count}`),text('small',detail));row.append(d);b.append(row);}
  b.append(text('p',`${game.player.coin} Đồng · Cấp ${game.player.level} · ${game.player.xp}/${xpNext(game.player.level)} EXP`));
  openModal('Túi hành trang',b,[['Dùng thuốc [Q]',()=>{game.action('potion');processEvents();bag();}],['Đóng',closeModal,true]],'LỮ KHÁCH · MINH KIẾM');
}
function journal(){const b=document.createDocumentFragment();QUESTS.forEach((q,i)=>{const row=text('p',`${i<game.quest?'✓':i===game.quest?'◇':'·'} P00-0${i+1} · ${q}`);row.style.color=i<game.quest?'#91b998':i===game.quest?'#edd697':'#758f87';b.append(row);});
  b.append(text('p','Mục tiêu được ghi ở bảng bên trái. Dấu vàng chỉ hướng cần đi. Tiếp cận NPC hoặc vật thể rồi nhấn E; Space đánh thường, 1 đỡ, 2 áp sát, 3 quét nhóm.'));
  openModal('Nhật ký hành trình',b,[['Trở lại hành trình',closeModal,true]],'NƯỚC KHÔNG SOI BÓNG');
}
function settings(){const b=document.createDocumentFragment();
  const volume=text('label','','setting');volume.append(text('span','Âm lượng'));const slider=document.createElement('input');slider.type='range';slider.min='0';slider.max='100';slider.value=String(options.volume*100);slider.setAttribute('aria-label','Âm lượng');slider.oninput=()=>{options.volume=Number(slider.value)/100;sound.apply();storeOptions();};volume.append(slider);b.append(volume);
  for(const [key,label]of [['music','Nhạc nền'],['rain','Mưa và âm thanh mưa'],['reduced','Giảm hiệu ứng phụ']]){const row=text('label','','setting');row.append(text('span',label));const toggle=document.createElement('input');toggle.type='checkbox';toggle.checked=options[key];toggle.onchange=()=>{options[key]=toggle.checked;renderer.rain=options.rain;renderer.reduced=options.reduced;sound.apply();storeOptions();};row.append(toggle);b.append(row);}
  b.append(text('p','Chơi thử một người; khi mở bảng hoặc rời tab, hành trình tạm dừng. Tiến độ chỉ lưu trong trình duyệt trên máy này.'));
  openModal('Cài đặt',b,[['Chơi lại từ đầu',()=>openModal('Bắt đầu hành trình mới?','Tiến độ chơi thử Bến Mưa hiện tại trên trình duyệt này sẽ được thay bằng hành trình mới.',[['Giữ hành trình',settings],['Bắt đầu lại',()=>{game=new Game();closeModal();uiStamp='';save();sound.track(false);notice('Một lá thư lại chờ bên bến.');},true]])],['Tiếp tục hành trình',closeModal,true]],'NGŨ MẠCH · HUYỀN ẤN');
}
function storeOptions(){try{localStorage.setItem(OPTIONS,JSON.stringify(options));}catch{}}
function processEvents(){for(const e of game.drain()){
  if(e.type==='number'){renderer.number(e,game.tick);continue;}
  if(e.type==='notice'||e.type==='warning'||e.type==='bossWarning'){notice(e.text);if(e.type==='bossWarning')sound.play('sfx/boss/mang_cot_'+({A:'sweep',B:'emerge',C:'bubble'}[e.attack])+'_warning_v01.wav',.7);}
  if(e.type==='accepted'){sound.play('sfx/quest/accepted_v01.wav');notice('Đã nhận: '+QUESTS[e.quest]);}
  if(e.type==='reward'){sound.play('sfx/quest/completed_v01.wav');notice('Hoàn thành '+QUESTS[e.quest]+' · nhận thưởng');}
  if(e.type==='pickup')sound.play('sfx/ui/item_pickup_common_v01.wav',.6);
  if(e.type==='discovery')sound.play('sfx/quest/discovery_v01.wav',.6);
  if(e.type==='swing'||e.type==='cleave')sound.play('sfx/combat/basic_blade_v01.wav',.7);
  if(e.type==='hit')sound.play('sfx/combat/heavy_hit_v01.wav',.45);
  if(e.type==='hurt')sound.play('sfx/combat/actor_hurt_v01.wav',.5);
  if(e.type==='parry'){sound.play('sfx/skill/metal_parry_v01.wav');notice('Đỡ chuẩn · +2 Kiếm Ý');}
  if(e.type==='heal')sound.play('sfx/ui/potion_use_v01.wav',.7);
  if(e.type==='dash')sound.play('sfx/combat/dodge_v01.wav',.6);
  if(e.type==='level')notice('Cấp '+e.level+' · Một bước trưởng thành');
  if(e.type==='bossStart'){sound.track(true);notice('Mãng Cốt trồi lên từ đáy đầm!');}
  if(e.type==='bossDefeated'){sound.track(false);notice('Mãng Cốt đã được giải thoát. Một mảnh ấn lộ dưới nước.');}
  if(e.type==='death'){sound.play('sfx/combat/death_v01.wav',.6);save();openModal('Mưa chưa dứt','Ngươi gục xuống giữa làn mưa. Những gì đã tìm thấy vẫn còn. Hãy trở về Bến Gỗ, lấy lại hơi thở rồi tiếp tục.',[['Hồi sinh ở Bến Gỗ',()=>{game.action('respawn');closeModal();sound.track(false);save();},true]],'HÀNH TRÌNH CHƯA KẾT THÚC');}
  if(['progress','accepted','reward','level','respawn'].includes(e.type))save();
}}
function updateHud(){const p=game.player;$('hp').textContent=`${Math.ceil(p.hp)} / ${p.maxHp}`;$('mp').textContent=`${Math.floor(p.mp)} / ${p.maxMp}`;
  $('hp-fill').style.width=p.hp/p.maxHp*100+'%';$('mp-fill').style.width=p.mp/p.maxMp*100+'%';$('level').textContent='Cấp '+p.level;$('coin').textContent=p.coin+' ◈';$('xp').textContent=p.xp+' / '+xpNext(p.level)+' EXP';$('intent').textContent=Array.from({length:5},(_,i)=>i<p.intent?'◆':'◇').join(' ');
  const stamp=JSON.stringify([game.quest,game.active,game.flags]);if(stamp!==uiStamp){uiStamp=stamp;$('quest-name').textContent=game.quest>=5?'Đường tới Thanh Lạc':`P00-0${game.quest+1} · ${QUESTS[game.quest]}`;$('objectives').replaceChildren(...game.objectives().map(o=>text('div',o.text,'objective'+(o.done?' done':''))));}
  const nearby=game.nearest();$('interact-wrap').classList.toggle('hidden',!nearby||modal);$('interact-hint').textContent=nearby?.name||'';
  $('coordinates').textContent=`${p.x.toFixed(1)}, ${p.y.toFixed(1)}`;$('telemetry').textContent=`${fps} FPS · E tương tác · J nhật ký · Esc cài đặt`;
  document.querySelectorAll('[data-action]').forEach(b=>{const action=b.dataset.action,seconds=game.cooldown(action),em=b.querySelector('em');em.style.display=seconds>0?'grid':'none';em.textContent=String(Math.ceil(seconds));b.disabled=p.hp<=0||modal;if(action==='potion')b.querySelector('span').textContent='Thuốc ×'+p.potions;});
  $('attack').disabled=p.hp<=0||modal;$('boss-hud').classList.toggle('hidden',!game.boss.active);$('boss-fill').style.width=game.boss.hp/game.boss.maxHp*100+'%';$('boss-phase').textContent='PHA '+game.boss.phase+' · '+Math.ceil(game.boss.hp)+' / '+game.boss.maxHp;
}
function doAction(action){if(!started||modal||needsRelease||document.hidden)return;game.action(action);processEvents();}
function keyAction(code){return ({Space:'attack',Digit1:'guard',Digit2:'dash',Digit3:'cleave',KeyQ:'potion',ShiftLeft:'dodge',ShiftRight:'dodge'})[code];}
window.addEventListener('keydown',e=>{
  if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Tab'].includes(e.code)&&started&&e.code!=='Tab')e.preventDefault();
  if(!started)return;
  if(e.code==='Escape'){e.preventDefault();if(modal)closeModal();else settings();return;}
  if(modal){if(e.code==='Tab'){const nodes=[...$('modal').querySelectorAll('button,input')].filter(n=>!n.disabled);if(nodes.length){const i=nodes.indexOf(document.activeElement),next=e.shiftKey?(i-1+nodes.length)%nodes.length:(i+1)%nodes.length;e.preventDefault();nodes[next].focus();}}return;}
  if(e.repeat&&needsRelease)return;
  if(needsRelease&&!e.repeat&&held.size===0)needsRelease=false;
  held.add(e.code);if(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))walkGoal=null;if(e.repeat)return;
  if(e.code==='KeyE'){if(!needsRelease)interact();return;}
  if(e.code==='KeyB'){bag();return;}if(e.code==='KeyJ'){journal();return;}
  const action=keyAction(e.code);if(action)doAction(action);
});
window.addEventListener('keyup',e=>{held.delete(e.code);if(held.size===0&&stickPointer===null)needsRelease=false;});
window.addEventListener('blur',()=>{resetControls();if(started&&!modal)openModal('Chờ một nhịp mưa','Hành trình đã tạm dừng khi bạn rời cửa sổ.',[['Tiếp tục',closeModal,true]],'TẠM DỪNG');});
document.addEventListener('visibilitychange',()=>{if(document.hidden){resetControls();save();if(sound.music)sound.music.pause();if(sound.ambience)sound.ambience.pause();}else if(started)sound.apply();});
window.addEventListener('beforeunload',save);window.addEventListener('resize',()=>renderer?.resize());
$('journal-btn').onclick=journal;$('bag-btn').onclick=bag;$('settings-btn').onclick=settings;$('close-modal').onclick=closeModal;
$('sound-btn').onclick=()=>{sound.enabled=!sound.enabled;sound.apply();};$('interact-btn').onclick=interact;$('attack').onclick=()=>doAction('attack');
document.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>doAction(b.dataset.action));
$('track-btn').onclick=()=>{if(modal||!started)return;const goal=game.goal();if(goal){walkGoal={x:goal.x,y:goal.y,stop:2.3};renderer.tracking=true;needsRelease=false;notice('Đang tới '+(goal.name||'mục tiêu')+'. WASD hoặc nhấp đất để đổi hướng.');}};
const joystick=$('joystick');
function updateStick(e){const r=joystick.getBoundingClientRect(),dx=e.clientX-r.left-r.width/2,dy=e.clientY-r.top-r.height/2,n=Math.hypot(dx,dy),max=r.width*.34;
  touch={x:n>5?dx/Math.max(max,n):0,y:n>5?-dy/Math.max(max,n):0};$('stick').style.transform=`translate(${dx/Math.max(1,n/max)}px,${dy/Math.max(1,n/max)}px)`;}
joystick.onpointerdown=e=>{if(modal||!started)return;if(needsRelease&&held.size===0)needsRelease=false;if(needsRelease)return;e.preventDefault();walkGoal=null;stickPointer=e.pointerId;joystick.setPointerCapture(e.pointerId);updateStick(e);};
joystick.onpointermove=e=>{if(stickPointer===e.pointerId)updateStick(e);};
joystick.onpointerup=joystick.onpointercancel=joystick.onlostpointercapture=e=>{if(stickPointer===e.pointerId){stickPointer=null;touch={x:0,y:0};$('stick').style.transform='';}};
document.addEventListener('pointerup',()=>{if(held.size===0&&stickPointer===null)needsRelease=false;});
$('world').onpointerdown=e=>{if(modal||!started)return;const r=$('world').getBoundingClientRect(),dx=e.clientX-r.left-$('world').width/2,dy=-(e.clientY-r.top-$('world').height/2),n=Math.hypot(dx,dy);if(n>1)game.player.face={x:dx/n,y:dy/n};walkGoal={x:renderer.camera.x+dx/20,y:Math.max(-11,Math.min(9,renderer.camera.y+dy/20)),stop:.3};needsRelease=false;};

function frame(now){const dt=Math.min(.15,(now-(previous||now))/1000);previous=now;frameCount++;if(now-fpsAt>1000){fps=frameCount;frameCount=0;fpsAt=now;}
  if(renderer&&game){if(started&&!modal&&!document.hidden){accumulator+=dt;
      let x=needsRelease?0:(held.has('KeyD')||held.has('ArrowRight')?1:0)-(held.has('KeyA')||held.has('ArrowLeft')?1:0)+touch.x;
      let y=needsRelease?0:(held.has('KeyW')||held.has('ArrowUp')?1:0)-(held.has('KeyS')||held.has('ArrowDown')?1:0)+touch.y;
      if(walkGoal&&!needsRelease){if(distance(game.player,walkGoal)<=walkGoal.stop)walkGoal=null;else{x=walkGoal.x-game.player.x;y=walkGoal.y-game.player.y;}}
      while(accumulator>=.05){game.step({x,y});if(held.has('Space'))doAction('attack');processEvents();accumulator-=.05;if(modal){accumulator=0;break;}}
      if(now-lastSave>5000){save();lastSave=now;}
    }else accumulator=0;
    renderer.draw(game,now,!started);if(started&&now-lastHud>=100){updateHud();lastHud=now;}
  }requestAnimationFrame(frame);
}
async function boot(){try{
    if(QA)document.querySelector('.local-label').textContent='PHIÊN KIỂM THỬ · LƯU RIÊNG';
    const response=await fetch('content.json');if(!response.ok)throw new Error('content');content=await response.json();
    const images={};await Promise.all(Object.entries(content.sprites).map(async([name,spec])=>{images[name]=await new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(new Error('sprite '+name));img.src=spec.url;});}));
    game=new Game();let resumed=false;try{const raw=localStorage.getItem(SAVE);if(raw&&raw.length<50000)resumed=game.restore(JSON.parse(raw));}catch{}
    renderer=new Renderer($('world'),$('mini'),content,images);renderer.rain=options.rain;renderer.reduced=options.reduced;
    $('start').disabled=false;$('start').textContent=resumed?'Tiếp tục hành trình':'Bước xuống bến';
    $('start').onclick=()=>{started=true;$('title').classList.add('hidden');$('hud').classList.remove('hidden');resetControls();renderer.camera.x=game.player.x;renderer.camera.y=game.player.y;sound.track(game.boss.active);$('area-title').textContent='BẾN MƯA';setTimeout(()=>$('area-title').style.opacity=0,3200);notice('Nhấp đất hoặc WASD để đi · Tới mục tiêu ở bảng nhiệm vụ · E nói chuyện.');
      if(game.player.hp<=0)openModal('Trở về dưới mưa','Hành trình vẫn còn đợi ở Bến Gỗ.',[['Hồi sinh',()=>{game.action('respawn');closeModal();},true]]);
    };
    requestAnimationFrame(frame);
  }catch(err){console.error(err);$('load-error').textContent='Chưa tải được dữ liệu hoặc ảnh. Hãy chạy CHOI_THU.cmd và mở lại địa chỉ local.';$('start').textContent='Chưa thể vào game';}
}
boot();
