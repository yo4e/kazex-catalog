const app = document.querySelector('#app');
const publicMode = document.documentElement.dataset.mode === 'public';
let publicTracks;
const isPending = status => status==='pending_selection'||status==='candidate';
const artistOrder = ['templex-tsukino','nozom','gramarasfan','the-aerial-gravities','mri-music-resonance-imaging','satori-chandra'];
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm = value => String(value ?? '').normalize('NFKC').toLocaleLowerCase();
const badge = status => isPending(status)?'<span class="badge pending_selection">確認待ち</span>':'';
let catalog, token = 0, detail, lastList = '#/';
const url = (path = '/', values = {}) => '#'+path+(Object.keys(values).length ? '?'+new URLSearchParams(values) : '');
const current = () => {const u = new URL(location.hash.slice(1) || '/', location.origin);return {path:u.pathname,params:u.searchParams};};
const artist = id => catalog.artists.find(a=>a.id===id);
const readJSON = async path => {const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error('読み込みに失敗しました。再読み込みしてください。');return r.json();};
const fetchJSON = async path => {
  if(!publicMode)return readJSON(path);
  if(path==='/api/catalog')return readJSON('./data/catalog.json');
  const requested=new URL(path,location.origin);
  if(requested.pathname==='/api/candidates')return {available:false,versions:[]};
  if(requested.pathname==='/api/track'){
    publicTracks ||= readJSON('./data/tracks.json');
    const track=(await publicTracks)[requested.searchParams.get('key')];
    if(!track)throw new Error('曲が見つかりません。');return track;
  }
  throw new Error('この表示では利用できません。');
};
const setRoute = (path,values,replace=false) => {const next=url(path,values);if(replace){history.replaceState(null,'',next);render();}else if(location.hash===next){render();}else location.hash=next;};
function cover(release, className='art-block') {
  return `<div class="${className} image-frame image-frame--artwork">${release.cover ? `<img src="${release.cover.url}" alt="${esc(release.title)}の登録ジャケット" loading="lazy">` : `<div class="art-placeholder"><strong>${esc(release.title)}</strong><span>ジャケット未登録</span></div>`}</div>`;
}
function shell(content, selected='') {
  const artists=[...catalog.artists].sort((a,b)=>artistOrder.indexOf(a.id)-artistOrder.indexOf(b.id));
  app.innerHTML=`<div class="shell"><aside class="sidebar"><a href="#/" class="brand" aria-label="KazeX Records カタログ一覧">${catalog.brand?.logo ? `<img class="brand-logo" src="${catalog.brand.logo.url}" alt="KazeX Records — AI sings. Wind listens.">` : 'KAZEX'}</a><p class="brand-sub">CATALOG REVIEW</p><span class="private-tag">${publicMode?'公開カタログ':'このMacだけの確認用'}</span><div class="nav-caption">ARTISTS</div><nav aria-label="アーティスト"><a class="artist-link ${!selected?'active':''}" href="#/"><span class="artist-letter">す</span>すべて<span class="count">${catalog.releases.length}</span></a>${artists.map(a=>`<a class="artist-link ${a.id===selected?'active':''}" href="${url('/',{artist:a.id})}"><span class="artist-letter">${esc(a.name.slice(0,1))}</span><span>${esc(a.name)}</span><span class="count">${catalog.releases.filter(r=>r.artist_id===a.id).length}</span></a>`).join('')}</nav><p class="sidebar-note">${publicMode?'作品・画像・配信リンクと歌詞を掲載しています。':'作品・画像・歌詞候補を見比べられます。'}</p></aside><main id="main" class="main">${content}</main></div>`;
  document.querySelectorAll('[data-reload]').forEach(b=>b.onclick=()=>location.reload());
}
function gallery(a) {
  if(!a?.images.length)return '';
  return `<details class="image-section"><summary>画像を確認 <span class="muted small">${a.images.filter(i=>i.status!=='archived').length}点</span></summary><div class="gallery" data-gallery>${a.images.filter(i=>i.status!=='archived').map(imageCard).join('')}</div>${a.images.some(i=>i.status==='archived')?'<label class="archive-control"><input type="checkbox" id="show-archived"> 旧版・保管画像も表示する</label>':''}</details>`;
}
function imageCard(i) {
  const title=String(i.title||'').replaceAll('アー写','アーティスト画像');
  const kind=i.kind==='アー写'?'アーティスト画像':i.kind==='参考画像'?'':i.kind;
  const caption=[kind,title].filter(Boolean).join(' · ');
  return `<div class="image-card"><a class="image-frame image-frame--${i.kind==='アー写'?'portrait':'artwork'}" href="${i.url}" target="_blank" rel="noreferrer"><img src="${i.url}" alt="${esc(title)}${isPending(i.status)?'（確認待ち）':''}" loading="lazy">${badge(i.status)}</a><p>${esc(caption)}</p></div>`;
}
function wireGallery(a) {
  const toggle=document.querySelector('#show-archived');if(toggle)toggle.onchange=()=>{document.querySelector('[data-gallery]').innerHTML=a.images.filter(i=>toggle.checked||i.status!=='archived').map(imageCard).join('');};
}
function serviceLinks(links=[],label='配信サービス') {
  if(!links.length)return '';
  return `<nav class="service-links" aria-label="${esc(label)}">${links.map(link=>`<a href="${esc(link.url)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">${esc(link.label)} ↗</a>`).join('')}</nav>`;
}
function releaseInfo(r) {
  const m=r.metadata||{},ids=m.identifiers||{},rights=m.copyright||{};
  const types={single:'シングル',ep:'EP',album:'アルバム'};
  const rows=[['形式',types[r.type]||r.type],['ジャンル',m.genres?.join(' / ')],['レーベル',m.label],['UPC / EAN',ids.upc_ean],['カタログ番号',ids.catalog_number],['Amazon ASIN',ids.amazon_asin],['著作権表記',rights.c_line],['原盤権表記',rights.p_line]].filter(([,v])=>v);
  if(!rows.length)return '';
  return `<details class="catalog-info"><summary>作品情報</summary><dl>${rows.map(([label,value])=>`<dt>${esc(label)}</dt><dd>${esc(value)}</dd>`).join('')}</dl></details>`;
}
function trackInfo(track) {
  const seconds=track.duration_seconds;
  const duration=Number.isInteger(seconds)&&seconds>0?`${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')}`:null;
  const roles=[['lyricists','作詞'],['composers','作曲'],['vocalists','歌唱']];
  const credits=roles.map(([role,label])=>{
    const names=track[role]||[];
    const instrumental=track.instrumental===true&&role!=='composers';
    const value=names.length?esc(names.join(' / ')):instrumental?'—（Instrumental）':'未登録';
    return `<dt>${label}</dt><dd data-credit-role="${role}"${names.length?'':' class="muted"'}>${value}</dd>`;
  }).join('');
  return `${duration?`<p class="track-fact">配信表示の長さ：${duration}</p>`:''}<dl class="track-credits" aria-label="曲のクレジット">${credits}</dl>${track.songwriters?.length?`<p class="track-fact">ソングライター（役割未分離）：${esc(track.songwriters.join(' / '))}</p>`:''}${serviceLinks(track.links,'この曲の配信サービス')}`;
}
function artistHeading(a) {
  const hasCandidates=a.images.some(i=>i.kind==='アー写'&&i.status==='candidate');
  const state=a.portrait?'アーティスト画像':hasCandidates?'アーティスト画像は未選択':'アーティスト画像は未登録';
  return `<div class="artist-heading"><div class="artist-portrait image-frame image-frame--portrait">${a.portrait?`<img src="${a.portrait.url}" alt="${esc(a.name)}のアーティスト画像">`:`<div class="portrait-placeholder"><span>${esc(a.name.slice(0,1))}</span><small>${state}</small></div>`}</div><div class="artist-intro"><p class="eyebrow">KAZEX RECORDS / ARTIST</p><h1>${esc(a.name)}</h1>${a.description?`<p class="artist-description">${esc(a.description)}</p>`:''}${a.biography?`<details class="artist-biography"><summary>プロフィールを読む</summary><p>${esc(a.biography)}</p></details>`:''}${serviceLinks(a.links,'アーティストの配信ページ')}<p class="portrait-state">${state}${hasCandidates&&!a.portrait?' · 下の「画像を確認」から候補を見られます。':''}</p></div></div>`;
}
function listView(params) {
  const aid=params.get('artist')||'',query=params.get('q')||'',status=params.get('status')==='pending_selection'?'pending_selection':'';
  const a=artist(aid);const all=catalog.releases.filter(r=>!aid||r.artist_id===aid);
  const matches=r=>{const general=norm(`${r.title} ${artist(r.artist_id).name}`).includes(norm(query));return r.tracks.filter(t=>(!status||t.status===status)&&(general||norm(`${t.title} ${t.isrc}`).includes(norm(query))));};
  const rows=all.map(r=>({r,matched:matches(r)})).filter(x=>x.matched.length).sort((a,b)=>b.r.release_date.localeCompare(a.r.release_date));
  const pendingCount=all.reduce((n,r)=>n+r.tracks.filter(t=>t.status==='pending_selection').length,0);
  const focus=document.activeElement?.id==='search';const caret=document.activeElement?.selectionStart;
  const filters=[['','すべて',all.reduce((n,r)=>n+r.tracks.length,0)],['pending_selection','確認待ち',pendingCount]];
  shell(`<div class="topline">${a?artistHeading(a):'<div><div class="eyebrow">KAZEX RECORDS / CATALOG</div><h1>カタログ</h1><p class="intro">作品を開いて、画像と歌詞をまとめて確認。</p></div>'}<div class="top-actions"><button data-reload>再読み込み</button></div></div><div class="search-row"><input id="search" type="search" placeholder="曲名・作品名・アーティスト・ISRCで検索" aria-label="カタログを検索" value="${esc(query)}"></div><div class="filters" aria-label="歌詞の状態">${filters.map(([s,n,c])=>`<button class="filter ${status===s?'active':''}" data-filter="${s}" aria-pressed="${status===s}">${n}<span class="num">${c}</span></button>`).join('')}</div>${gallery(a)}<div class="section-line"><h2>${query?'検索結果':'作品一覧'}</h2><span class="small muted">${rows.length}作品 / ${rows.reduce((n,x)=>n+x.matched.length,0)}曲</span></div>${rows.length?`<div class="cards">${rows.map(({r,matched})=>{const first=matched[0];return `<a class="release-card" href="${url('/release/'+r.id,{track:first.isrc||first.number})}" data-release="${r.id}">${cover(r)}<div class="card-content"><h3>${esc(r.title)}</h3><p class="artist-name">${esc(artist(r.artist_id).name)}</p><div class="card-footer"><span>${esc(r.release_date)}</span><span>· ${r.tracks.length}曲</span>${badge(r.tracks.some(t=>t.status==='pending_selection')?'pending_selection':r.tracks[0]?.status)}</div>${query||status?`<p class="card-match">${matched.length}曲が一致 · ${esc(first.title)}</p>`:''}</div></a>`;}).join('')}</div>`:'<div class="empty">見つかりませんでした。<br>別の曲名やISRCで検索してみてください。</div>'}`,aid);
  const input=document.querySelector('#search');let timer;
  input.oninput=()=>{clearTimeout(timer);timer=setTimeout(()=>{const values={};if(aid)values.artist=aid;if(input.value)values.q=input.value;if(status)values.status=status;setRoute('/',values,true);},180);};
  if(focus){input.focus();if(caret!==null)input.setSelectionRange?.(caret,caret);}
  document.querySelectorAll('[data-filter]').forEach(b=>b.onclick=()=>{const values={};if(aid)values.artist=aid;if(query)values.q=query;if(b.dataset.filter)values.status=b.dataset.filter;setRoute('/',values);});
  if(a)wireGallery(a);lastList=location.hash||'#/';sessionStorage.setItem('catalog-last-list',lastList);
}
function diffIndices(left,right) {
  const a=left.split('\n'),b=right.split('\n');const dp=Array.from({length:a.length+1},()=>new Uint16Array(b.length+1));
  for(let i=a.length-1;i>=0;i--)for(let j=b.length-1;j>=0;j--)dp[i][j]=a[i]===b[j]?1+dp[i+1][j+1]:Math.max(dp[i+1][j],dp[i][j+1]);
  const x=new Set(),y=new Set();let i=0,j=0;
  while(i<a.length||j<b.length){if(i<a.length&&j<b.length&&a[i]===b[j]){i++;j++;}else if(i<a.length&&(j===b.length||dp[i+1][j]>=dp[i][j+1]))x.add(i++);else y.add(j++);}
  return [x,y];
}
function bodyHTML(v,changed,compare) {return `<section><p class="body-label">${esc(v.displayLabel)}</p>${compare?`<div class="lyric-copy" aria-label="${esc(v.displayLabel)}の歌詞">${v.body.split('\n').map((line,i)=>`<span class="lyric-line ${changed.has(i)?'changed':''}">${esc(line)||'\u00a0'}</span>`).join('')}</div>`:`<pre class="lyric-copy" aria-label="歌詞本文">${esc(v.body)}</pre>`}</section>`;}
async function detailView(rid,params,myToken) {
  const r=catalog.releases.find(r=>r.id===rid);if(!r){shell('<div class="empty">作品が見つかりません。<a href="#/">一覧へ</a></div>');return;}
  const a=artist(r.artist_id),track=r.tracks.find(t=>String(t.isrc||t.number)===params.get('track'))||r.tracks[0];
  const back=sessionStorage.getItem('catalog-last-list')||'#/';
  shell(`<div class="breadcrumbs"><a href="${esc(back)}">← 一覧に戻る</a><span>/</span><a href="${url('/',{artist:a.id})}">${esc(a.name)}</a><span>/</span><span>${esc(r.title)}</span></div><div class="release-hero">${cover(r,'hero-cover')}<div><p class="eyebrow">${esc(a.name)}</p><h1>${esc(r.title)}</h1><div class="hero-meta"><span>${esc(r.release_date)}</span><span>${r.tracks.length}曲</span><span>${publicMode?'公開カタログ':'ローカル確認用'}</span></div>${r.smartlink?`<a class="smartlink" href="${r.smartlink}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Too Lost 配信リンク ↗</a>`:'<p class="small muted">配信リンク未登録</p>'}${serviceLinks(r.links,'作品の配信サービス')}</div></div>${releaseInfo(r)}${gallery(a)}<div class="album-layout"><ol class="track-list" aria-label="曲一覧">${r.tracks.map(t=>`<li><a class="track-row ${t.key===track.key?'active':''}" href="${url('/release/'+rid,{track:t.isrc||t.number})}" aria-current="${t.key===track.key?'true':'false'}"><span class="track-num">${String(t.number).padStart(2,'0')}</span><span><span class="track-name">${esc(t.title)}</span><br>${badge(t.status)}${t.candidate_count?`<span class="candidate-count">${t.candidate_count}候補</span>`:''}</span></a></li>`).join('')}</ol><article class="lyric-panel" aria-label="曲の確認"><div class="lyric-heading"><h2>${esc(track.title)}</h2>${badge(track.status)}</div><div class="identifier">ISRC: ${esc(track.isrc||'未登録')}<br><span class="mono">${esc(track.key)}</span></div>${trackInfo(track)}<div id="reading"><p class="muted small">歌詞を読み込んでいます…</p></div></article></div>`,a.id);
  wireGallery(a);
  try {
    const [publicTrack,privateTrack]=await Promise.all([fetchJSON('/api/track?'+new URLSearchParams({key:track.key})),fetchJSON('/api/candidates?'+new URLSearchParams({key:track.key}))]);
    if(myToken!==token)return;
    const versions=[];
    if(publicTrack.adopted)versions.push({...publicTrack.adopted,displayLabel:'歌詞',isAdopted:true,reference:track.key+':adopted'});
    for(const v of privateTrack.versions)versions.push({...v,displayLabel:`${v.label} · ${v.kinds.map(k=>k==='nas'?'保存原稿':'Suno').join(' / ')} · ${v.id.slice(0,6)}`,isAdopted:false});
    detail={r,a,track,versions};
    renderReading(params,privateTrack.available);
  }catch(e){if(myToken===token)document.querySelector('#reading').innerHTML=`<div class="status-message">${esc(e.message)}</div>`;}
}
function renderReading(params,privateAvailable) {
  const {r,track,versions}=detail;const target=document.querySelector('#reading');
  if(!versions.length){
    if(track.instrumental===true){target.innerHTML='<div class="status-message">Instrumental</div>';return;}
    if(track.status==='no_lyrics'){target.replaceChildren();return;}
    const message=track.status==='pending_selection'
      ? (publicMode?'歌詞は確認待ちです。':privateAvailable?'この曲の歌詞候補はまだありません。':'私的候補を接続していません。')
      : '歌詞はまだ掲載されていません。';
    target.innerHTML=`<div class="status-message">${message}</div>`;return;
  }
  const selected=versions.find(v=>v.id===params.get('version'))||versions[0];
  const compared=versions.find(v=>v.id===params.get('compare')&&v.id!==selected.id);const comparing=!!compared;
  const optionHTML=id=>versions.map(v=>`<option value="${esc(v.id)}" ${v.id===id?'selected':''}>${esc(v.displayLabel)}</option>`).join('');
  const [x,y]=compared?diffIndices(selected.body,compared.body):[new Set(),new Set()];
  const chooser=versions.length>1?`<div class="chooser"><div class="selects ${comparing?'comparing':''}"><div><label for="version">表示する歌詞${comparing?' A':''}</label><select id="version">${optionHTML(selected.id)}</select></div>${compared?`<div><label for="compare-version">比較する歌詞 B</label><select id="compare-version">${optionHTML(compared.id)}</select></div>`:''}</div><div class="compare-toggle"><input type="checkbox" id="compare-toggle" ${comparing?'checked':''}><label for="compare-toggle">2つの本文を並べて比較する</label></div></div>`:'';
  const candidateNote=!selected.isAdopted?`<p class="candidate-note">確認用の候補です。表示順や候補番号は採用順位ではありません。${r.id==='glamorous'?' 同名曲から集めた候補で、配信版との一致は未確認です。':''}</p>`:'';
  const evidence=!selected.isAdopted?`<details class="evidence"><summary>候補の識別情報・出典（ローカルのみ）</summary><p class="mono" id="candidate-reference">${esc(selected.reference)}</p><p>本文 SHA256: <span class="mono">${selected.sha256}</span></p><ul>${selected.sources.map(s=>`<li>${s.kind==='nas'?'保存原稿':'Suno表示歌詞'} · ${esc(s.label)}${s.url?`<br><a href="${esc(s.url)}" target="_blank" rel="noreferrer">出典を開く</a>`:''}</li>`).join('')}</ul><p>配信音源との一致を確定した表示ではありません。</p></details>`:'';
  target.innerHTML=`${chooser}${candidateNote}${comparing?`<p class="diff-note">${x.size+y.size?`違いがある行に色を付けています（A ${x.size}行 / B ${y.size}行）。`:'この2候補の本文は同一です。'}</p>`:''}<div class="body-grid ${comparing?'comparing':''}">${bodyHTML(selected,x,comparing)}${compared?bodyHTML(compared,y,true):''}</div>${evidence}`;
  const change=(v,c)=>{const p={track:track.isrc||track.number,version:v};if(c&&c!==v)p.compare=c;setRoute('/release/'+r.id,p);};
  const first=document.querySelector('#version');if(first)first.onchange=e=>change(e.target.value,compared?.id);
  const toggle=document.querySelector('#compare-toggle');if(toggle)toggle.onchange=e=>change(selected.id,e.target.checked?versions.find(v=>v.id!==selected.id).id:null);
  const second=document.querySelector('#compare-version');if(second)second.onchange=e=>change(selected.id,e.target.value);
}
async function render() {
  const myToken=++token;const {path,params}=current();
  if(path.startsWith('/release/'))await detailView(decodeURIComponent(path.slice(9)),params,myToken);
  else listView(params);
}
window.addEventListener('hashchange',render);
try{catalog=await fetchJSON('/api/catalog');for(const [key,value] of Object.entries(catalog.brand?.colors||{})){if(['accent','background'].includes(key)&&/^#[0-9a-f]{6}$/i.test(value))document.documentElement.style.setProperty(key==='background'?'--page-background':'--accent',value);}await render();}catch(e){app.innerHTML=`<p class="loading">${esc(e.message)}<br>${publicMode?'ページを再読み込みしてください。':'ローカルサーバーを起動してから再読み込みしてください。'}</p>`;}
