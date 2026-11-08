import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {test} from 'node:test';

const source=fs.readFileSync(new URL('../viewer/web/app.js',import.meta.url),'utf8').split("window.addEventListener('hashchange',render);")[0];
function viewer(releases) {
  const app={innerHTML:''}, search={value:''},reading={innerHTML:'',replaceChildren(){this.innerHTML='';}};
  const storage=new Map();
  const context=vm.createContext({document:{documentElement:{dataset:{mode:'public'}},querySelector:s=>s==='#app'?app:s==='#search'?search:s==='#reading'?reading:null,querySelectorAll:()=>[]},location:{hash:'#/',origin:'https://example.com'},URL,URLSearchParams,sessionStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},fetch:async()=>({ok:true,json:async()=>({})})});
  vm.runInContext(source,context);
  context.fixture={artists:[{id:'artist',name:'Artist',images:[]}],releases,brand:{}};
  vm.runInContext('catalog=fixture',context);
  return {context,app,run:code=>vm.runInContext(code,context)};
}
const release=(id,state,date='',tracks=[{number:1,key:`${id}:1`,title:'Track',status:'no_lyrics',candidate_count:0}])=>({id,title:id,artist_id:'artist',release_status:state,release_date:date,tracks,metadata:{},links:[]});

test('planned and upcoming are labeled; dates do not silently release them',()=>{
  const v=viewer([]);
  for(const state of ['planned','upcoming'])for(const date of ['', '2020-01-01','2099-01-01']){
    v.context.sample=release('draft',state,date);
    assert.match(v.run('releaseBadge(sample)'),/リリース前/);
    assert.equal(v.run('releaseDateLabel(sample)'),date?`${date} 予定`:'リリース日未定');
  }
  for(const state of ['released',null]){
    v.context.sample=release('ordinary',state,'2026-01-01');
    assert.equal(v.run('releaseBadge(sample)'),'');
    assert.equal(v.run('releaseDateLabel(sample)'),'2026-01-01');
  }
});
test('catalog cards show prereleases first and preserve search',()=>{
  const v=viewer([release('released','released','2026-11-01'),release('draft','planned')]);
  v.run('listView(new URLSearchParams())');
  assert.ok(v.app.innerHTML.indexOf('data-release="draft"')<v.app.innerHTML.indexOf('data-release="released"'));
  assert.match(v.app.innerHTML,/class="badge prerelease">リリース前/);
  assert.match(v.app.innerHTML,/リリース日未定/);
  v.run('listView(new URLSearchParams("q=draft"))');
  assert.match(v.app.innerHTML,/data-release="draft"/);
  assert.doesNotMatch(v.app.innerHTML,/data-release="released"/);
  v.run('listView(new URLSearchParams())');
  assert.match(v.app.innerHTML,/data-release="released"/);
});
test('empty planned releases can be listed, searched and opened repeatedly',async()=>{
  const v=viewer([release('empty','planned','',[])]);
  v.run('listView(new URLSearchParams())');
  assert.match(v.app.innerHTML,/href="#\/release\/empty"/);
  v.run('listView(new URLSearchParams("q=empty"))');
  assert.match(v.app.innerHTML,/data-release="empty"/);
  v.run('listView(new URLSearchParams("status=pending_selection"))');
  assert.doesNotMatch(v.app.innerHTML,/data-release="empty"/);
  for(let i=0;i<2;i++){
    await v.run('detailView("empty",new URLSearchParams(),0)');
    assert.match(v.app.innerHTML,/リリース前/);
    assert.match(v.app.innerHTML,/曲目はまだ登録されていません/);
  }
});
test('detail displays scheduled date and prerelease status with existing tracks',async()=>{
  const v=viewer([release('scheduled','upcoming','2027-01-02')]);
  await v.run('detailView("scheduled",new URLSearchParams("track=1"),0)');
  assert.match(v.app.innerHTML,/class="badge prerelease">リリース前/);
  assert.match(v.app.innerHTML,/2027-01-02 予定/);
  assert.match(v.app.innerHTML,/Track/);
});
