/* Open Prep V4.5: deterministic nutrition state operations; no AI or DOM dependencies. */
(function(root,factory){
 const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;
 root.NutritionCore=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 const fields=['calories','protein','carbs','fat'];
 const num=v=>{const n=Number(v);return Number.isFinite(n)&&n>=0?n:0;};
 function day(d){return Array.isArray(d)?d:[];}
 function visible(data,key){return day(data?.[key]).filter(m=>m&&!m.deleted);}
 function totals(data,key){const t={calories:0,protein:0,carbs:0,fat:0};for(const meal of visible(data,key)){for(const k of fields)t[k]+=num(meal[k]);}return t;}
 function put(data,key,meal){const out={...data};const entries=day(out[key]).slice();const idx=entries.findIndex(x=>x?.id===meal.id);if(idx<0)entries.push(meal);else entries[idx]=meal;out[key]=entries;return out;}
 function remove(data,key,id,when){const old=day(data?.[key]).find(x=>x?.id===id);if(!old)return data;return put(data,key,{...old,deleted:true,updated_at:when||new Date().toISOString()});}
 function merge(local,remote){const result={};for(const key of new Set([...Object.keys(remote||{}),...Object.keys(local||{})])){
  const entries=new Map();for(const m of [...day(remote?.[key]),...day(local?.[key])]){
   if(!m||!m.id)continue;const old=entries.get(m.id);
   // Legacy entries with no timestamp prefer the local copy; otherwise latest timestamp wins.
   if(!old||String(m.updated_at||'')>=String(old.updated_at||''))entries.set(m.id,m);
  }result[key]=[...entries.values()];
 }return result;}
 function valid(meal){return fields.every(k=>Number.isFinite(Number(meal[k]))&&Number(meal[k])>=0&&Number(meal[k])<=10000);}
 return {fields,totals,visible,put,remove,merge,valid};
});
