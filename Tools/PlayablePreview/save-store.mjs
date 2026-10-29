import {Game} from './engine.mjs';
const MAX_BYTES=64000;

export function decodeSave(raw){
  if(typeof raw!=='string'||new TextEncoder().encode(raw).length>MAX_BYTES)throw new Error('Bản lưu quá lớn hoặc không đúng định dạng.');
  let data;try{data=JSON.parse(raw);}catch{throw new Error('Không đọc được JSON của bản lưu.');}
  if(data?.format!==undefined){if(data.format!=='NGUMACH_BENMUA_LOCAL'||data.fileVersion!==1)throw new Error('File không phải bản lưu Bến Mưa được hỗ trợ.');data=data.save;}
  const candidate=new Game();if(!candidate.restore(data))throw new Error('Dữ liệu bản lưu không hợp lệ hoặc thuộc phiên bản khác.');return candidate;
}
export function exportSave(game){return JSON.stringify({format:'NGUMACH_BENMUA_LOCAL',fileVersion:1,exportedAt:new Date().toISOString(),save:game.save()},null,2);}
export class SaveStore{
  constructor(storage,key){this.storage=storage;this.key=key;this.previous=key+'.previous';}
  load(){let found=false;for(const key of [this.key,this.previous]){
    let raw;try{raw=this.storage.getItem(key);}catch{return {game:new Game(),source:'unavailable'};}
    if(!raw)continue;found=true;try{return {game:decodeSave(raw),source:key===this.key?'primary':'previous'};}catch{}
  }return {game:new Game(),source:found?'invalid':'empty'};}
  write(game){const raw=JSON.stringify(game.save());decodeSave(raw);const old=this.storage.getItem(this.key);
    let validOld=false;if(old){try{decodeSave(old);validOld=true;}catch{}}
    // Preserve a known-good previous save; never replace it with malformed input.
    if(validOld&&old!==raw)this.storage.setItem(this.previous,old);
    this.storage.setItem(this.key,raw);
  }
  recovery(){const raw=this.storage.getItem(this.previous);if(!raw)throw new Error('Chưa có lần lưu trước để khôi phục.');return decodeSave(raw);}
}
