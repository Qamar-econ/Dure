// Runs rules.js (the same engine as the live demo) and writes its readings plus routing signals:
// sure, unknown, spelling fixes, how many words it recognised. Usage: node rules_detail.js OUT.json TEST.json
const fs=require('fs'),path=require('path');
const src=fs.readFileSync(path.join(__dirname,'rules.js'),'utf8');
const core=src.slice(0,src.indexOf('const T=require('));
const DureAI=new Function(core+'\nreturn DureAI;')();
const T=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const out=T.map(t=>{const e=['kg','ask','decide'].includes(t.expect)?t.expect:null;const p=DureAI.parse(t.msg,e);
  return {lang:p.unknown?'unknown':p.lang,crop:p.crop?'coffee':(p.other?'other':null),kg:p.kg,ask:p.ask,any:p.any,grade:p.grade,
    yn:t.expect==='decide'?(p.yes&&!p.no?'yes':p.no?'no':null):null,_sure:!!p.sure,_fixes:(p.fixes||[]).length,_raw_lang:p.lang,_unknown:!!p.unknown}});
fs.writeFileSync(process.argv[2],JSON.stringify(out));
