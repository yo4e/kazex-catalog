const app = document.querySelector('#app');
const publicMode = document.documentElement.dataset.mode === 'public';
let publicTracks;
const names = {adopted:'採用済み',pending_selection:'確認待ち',not_collected:'未取得',no_lyrics:'歌詞なし',candidate:'候補',selected:'採用済み',archived:'旧版・保管',registered:'登録ジャケット'};
const artistOrder = ['templex-tsukino','nozom','gramarasfan','the-aerial-gravities','mri-music-resonance-imaging','satori-chandra'];
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm = value => String(value ?? '').normalize('NFKC').toLocaleLowerCase();
const badge = status => `<span class="badge ${esc(status)}">${esc(names[status] || status)}</span>`;
let catalog, token = 0, detail, lastList = '#/', toastTimer;
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
const toast = text => {const t=document.querySelector('#toast');t.textContent=text;t.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove('visible'),2600);};
const setRoute = (path,values,replace=false) => {const next=url(path,values);if(replace){history.replaceState(null,'',next);render();}else if(location.hash===next){render();}else location.hash=next;};
function cover(release, className='art-block') {
  return `<div class="${className}">${release.cover ? `<img src="${release.cover.url}" alt="${esc(release.title)}の登録ジャケット" loading="lazy">` : `<div class="art-placeholder"><strong>${esc(release.title)}</strong><span>ジャケット未登録</span></div>`}</div>`;
}
function shell(content, selected='') {
  const artists=[...catalog.artists].sort((a,b)=>artistOrder.indexOf(a.id)-artistOrder.indexOf(b.id));
  app.innerHTML=`<div class="shell"><aside class="sidebar"><a href="#/" class="brand" aria-label="KazeX Records カタログ一覧">${catalog.brand?.logo ? `<img class="brand-logo" src="${catalog.brand.logo.url}" alt="KazeX Records — AI sings. Wind listens.">` : 'KAZEX'}</a><p class="brand-sub">CATALOG REVIEW</p><span class="private-tag">${publicMode?'公開カタログ':'このMacだけの確認用'}</span><div class="nav-caption">ARTISTS</div><nav aria-label="アーティスト"><a class="artist-link ${!selected?'active':''}" href="#/"><span class="artist-letter">す</span>すべて<span class="count">${catalog.releases.length}</span></a>${artists.map(a=>`<a class="artist-link ${a.id===selected?'active':''}" href="${url('/',{artist:a.id})}"><span class="artist-letter">${esc(a.name.slice(0,1))}</span><span>${esc(a.name)}</span><span class="count">${catalog.releases.filter(r=>r.artist_id===a.id).length}</span></a>`).join('')}</nav><p class="sidebar-note">${publicMode?'作品・画像・配信リンクと、採用済みの歌詞を掲載しています。':'曲と候補を選んで、採用依頼をコピー。<br>この画面から公開・採用は実行しません。'}</p></aside><main id="main" class="main">${content}</main></div>`;
  document.querySelectorAll('[data-reload]').forEach(b=>b.onclick=()=>location.reload());
}
function gallery(a) {
  if(!a?.images.length)return '';
  return `<details class="image-section"><summary>画像を確認 <span class="muted small">${a.images.filter(i=>i.status!=='archived').length}点 · 候補・採用状態を表示</span></summary><div class="gallery" data-gallery>${a.images.filter(i=>i.status!=='archived').map(imageCard).join('')}</div>${a.images.some(i=>i.status==='archived')?'<label class="archive-control"><input type="checkbox" id="show-archived"> 旧版・保管画像も表示する</label>':''}</details>`;
}
function imageCard(i) {return `<div class="image-card">${badge(i.status)}<a href="${i.url}" target="_blank" rel="noreferrer"><img src="${i.url}" alt="${esc(i.title)}（${esc(names[i.status])}）" loading="lazy"></a><p>${esc(i.kind)} · ${esc(i.title)}</p><button data-image="${i.id}">${i.status==='candidate'?'この画像の採用依頼をコピー':'この画像への確認依頼をコピー'}</button></div>`;}
function wireGallery(a) {
  const wire=()=>document.querySelectorAll('[data-image]').forEach(b=>b.onclick=()=>{const i=a.images.find(i=>i.id===b.dataset.image);request(`${i.status==='candidate'?'画像の採用依頼':'画像の確認依頼'}\nアーティスト：${a.name}\n画像ID：${i.id}\n画像：${i.path}\n現在の状態：${names[i.status]}\nSHA256：${i.sha256}\n\n${i.status==='candidate'?'この候補画像を採用してください。':'この画像について確認をお願いします。'}`);});
  wire();const toggle=document.querySelector('#show-archived');if(toggle)toggle.onchange=()=>{document.querySelector('[data-gallery]').innerHTML=a.images.filter(i=>toggle.checked||i.status!=='archived').map(imageCard).join('');wire();};
}
function artistHeading(a) {
  const hasCandidates=a.images.some(i=>i.kind==='アー写'&&i.status==='candidate');
  const state=a.portrait?'代表アー写':hasCandidates?'代表アー写は未選択':'アー写は未登録';
  return `<div class="artist-heading"><div class="artist-portrait">${a.portrait?`<img src="${a.portrait.url}" alt="${esc(a.name)}の代表アー写">`:`<div class="portrait-placeholder"><span>${esc(a.name.slice(0,1))}</span><small>${state}</small></div>`}</div><div class="artist-intro"><p class="eyebrow">KAZEX RECORDS / ARTIST</p><h1>${esc(a.name)}</h1>${a.description?`<p class="artist-description">${esc(a.description)}</p>`:''}<p class="portrait-state">${state}${hasCandidates&&!a.portrait?' · 下の「画像を確認」から候補を見られます。':''}</p>${a.default_has_lyrics===false?'<span class="badge no_lyrics">基本は歌詞なし · 例外は個別指定</span>':''}</div></div>`;
}
function listView(params) {
  const aid=params.get('artist')||'',query=params.get('q')||'',status=params.get('status')||'';
  const a=artist(aid);const all=catalog.releases.filter(r=>!aid||r.artist_id===aid);
  const matches=r=>{const general=norm(`${r.title} ${artist(r.artist_id).name}`).includes(norm(query));return r.tracks.filter(t=>(!status||t.status===status)&&(general||norm(`${t.title} ${t.isrc}`).includes(norm(query))));};
  const rows=all.map(r=>({r,matched:matches(r)})).filter(x=>x.matched.length).sort((a,b)=>b.r.release_date.localeCompare(a.r.release_date));
  const scopeCounts=Object.fromEntries(Object.keys(names).map(s=>[s,all.reduce((n,r)=>n+r.tracks.filter(t=>t.status===s).length,0)]));
  const focus=document.activeElement?.id==='search';const caret=document.activeElement?.selectionStart;
  const filters=[['','すべて',all.reduce((n,r)=>n+r.tracks.length,0)],...['adopted','pending_selection','not_collected','no_lyrics'].map(s=>[s,names[s],scopeCounts[s]])];
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
function listening(track) {
  if(!track.spotify_id)return '<p class="small muted">Spotifyの曲リンクは未登録です。</p>';
  return `<div class="listening"><div class="listen-actions"><button id="load-spotify">Spotifyプレーヤーを表示</button><a href="https://open.spotify.com/track/${track.spotify_id}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Spotifyで開く ↗</a></div><p class="small muted">プレーヤーはクリック時に読み込みます。自動再生はしません。</p><div id="spotify-frame"></div></div>`;
}
function wirePlayer(track) {
  const button=document.querySelector('#load-spotify');if(!button)return;
  button.onclick=()=>{
    const target=document.querySelector('#spotify-frame');
    if(target.children.length){target.replaceChildren();button.textContent='Spotifyプレーヤーを表示';return;}
    if(!/^[A-Za-z0-9]{22}$/.test(track.spotify_id))return;
    const frame=document.createElement('iframe');
    frame.src='https://open.spotify.com/embed/track/'+track.spotify_id;
    frame.title=track.title+' — Spotify';frame.loading='lazy';frame.referrerPolicy='no-referrer';
    frame.allow="encrypted-media; autoplay 'none'; camera 'none'; microphone 'none'; geolocation 'none'";frame.setAttribute('sandbox','allow-scripts allow-same-origin allow-popups');
    target.append(frame);button.textContent='Spotifyプレーヤーを閉じる';
  };
}
async function detailView(rid,params,myToken) {
  const r=catalog.releases.find(r=>r.id===rid);if(!r){shell('<div class="empty">作品が見つかりません。<a href="#/">一覧へ</a></div>');return;}
  const a=artist(r.artist_id),track=r.tracks.find(t=>String(t.isrc||t.number)===params.get('track'))||r.tracks[0];
  const back=sessionStorage.getItem('catalog-last-list')||'#/';
  shell(`<div class="breadcrumbs"><a href="${esc(back)}">← 一覧に戻る</a><span>/</span><a href="${url('/',{artist:a.id})}">${esc(a.name)}</a><span>/</span><span>${esc(r.title)}</span></div><div class="release-hero">${cover(r,'hero-cover')}<div><p class="eyebrow">${esc(a.name)}</p><h1>${esc(r.title)}</h1><div class="hero-meta"><span>${esc(r.release_date)}</span><span>${r.tracks.length}曲</span><span>${publicMode?'公開カタログ':'ローカル確認用'}</span></div>${r.smartlink?`<a class="smartlink" href="${r.smartlink}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Too Lost 配信リンク ↗</a>`:'<p class="small muted">配信リンク未登録</p>'}</div></div>${gallery(a)}<div class="album-layout"><ol class="track-list" aria-label="曲一覧">${r.tracks.map(t=>`<li><a class="track-row ${t.key===track.key?'active':''}" href="${url('/release/'+rid,{track:t.isrc||t.number})}" aria-current="${t.key===track.key?'true':'false'}"><span class="track-num">${String(t.number).padStart(2,'0')}</span><span><span class="track-name">${esc(t.title)}</span><br>${badge(t.status)}${t.candidate_count?`<span class="candidate-count">${t.candidate_count}候補</span>`:''}</span></a></li>`).join('')}</ol><article class="lyric-panel" aria-label="曲の確認"><div class="lyric-heading"><h2>${esc(track.title)}</h2>${badge(track.status)}</div><div class="identifier">ISRC: ${esc(track.isrc||'未登録')}<br><span class="mono">${esc(track.key)}</span></div>${listening(track)}<div id="reading"><p class="muted small">歌詞を読み込んでいます…</p></div></article></div>`,a.id);
  wireGallery(a);wirePlayer(track);
  try {
    const [publicTrack,privateTrack]=await Promise.all([fetchJSON('/api/track?'+new URLSearchParams({key:track.key})),fetchJSON('/api/candidates?'+new URLSearchParams({key:track.key}))]);
    if(myToken!==token)return;
    const versions=[];
    if(publicTrack.adopted)versions.push({...publicTrack.adopted,displayLabel:'採用済みの歌詞',isAdopted:true,reference:track.key+':adopted'});
    for(const v of privateTrack.versions)versions.push({...v,displayLabel:`${v.label} · ${v.kinds.map(k=>k==='nas'?'保存原稿':'Suno').join(' / ')} · ${v.id.slice(0,6)}`,isAdopted:false});
    detail={r,a,track,versions};
    renderReading(params,privateTrack.available);
  }catch(e){if(myToken===token)document.querySelector('#reading').innerHTML=`<div class="status-message">${esc(e.message)}</div>`;}
}
function renderReading(params,privateAvailable) {
  const {r,a,track,versions}=detail;const target=document.querySelector('#reading');
  if(!versions.length){const message=track.status==='no_lyrics'?['歌詞なし','本人の指定またはカタログ登録情報に基づく状態です。歌詞の収集対象には含めません。例外は個別に指定できます。']:track.status==='pending_selection'&&!privateAvailable?(publicMode?['歌詞は採用版を確認中です','公開する本文が決まり次第掲載します。']:['私的候補を接続していません','ローカル候補付きの起動設定で開くと、確認待ちの本文を見られます。']):['歌詞はまだ取得できていません','空欄を「歌詞なし」として扱っていません。本文が見つかったらこの曲へ紐づけます。'];target.innerHTML=`<div class="status-message"><strong>${message[0]}</strong>${message[1]}</div><div class="request-area"><button id="track-request">この曲への依頼文をコピー</button></div>`;document.querySelector('#track-request').onclick=()=>request(`カタログ確認依頼\n作品：${r.title}\nアーティスト：${a.name}\n曲：${track.title}\nISRC：${track.isrc}\n曲ID：${track.key}\n現在の状態：${names[track.status]}\n\nこの曲について確認をお願いします。`);return;}
  const selected=versions.find(v=>v.id===params.get('version'))||versions[0];
  const compared=versions.find(v=>v.id===params.get('compare')&&v.id!==selected.id);const comparing=!!compared;
  const optionHTML=id=>versions.map(v=>`<option value="${esc(v.id)}" ${v.id===id?'selected':''}>${esc(v.displayLabel)}</option>`).join('');
  const [x,y]=compared?diffIndices(selected.body,compared.body):[new Set(),new Set()];
  target.innerHTML=`<div class="chooser"><div class="selects ${comparing?'comparing':''}"><div><label for="version">表示する歌詞${comparing?' A':''}</label><select id="version">${optionHTML(selected.id)}</select></div>${compared?`<div><label for="compare-version">比較する歌詞 B</label><select id="compare-version">${optionHTML(compared.id)}</select></div>`:''}</div>${versions.length>1?`<div class="compare-toggle"><input type="checkbox" id="compare-toggle" ${comparing?'checked':''}><label for="compare-toggle">2つの本文を並べて比較する</label></div>`:''}</div><p class="candidate-note">${selected.isAdopted?'カタログに採用済みの本文です。':'確認用の候補です。表示順や候補番号は採用順位ではありません。'}${!selected.isAdopted&&r.id==='glamorous'?' 同名曲から集めた候補で、配信版との一致は未確認です。':''}</p>${comparing?`<p class="diff-note">${x.size+y.size?`違いがある行に色を付けています（A ${x.size}行 / B ${y.size}行）。`:'この2候補の本文は同一です。'}</p>`:''}<div class="body-grid ${comparing?'comparing':''}">${bodyHTML(selected,x,comparing)}${compared?bodyHTML(compared,y,true):''}</div><div class="request-area"><button class="primary" id="adopt-request">${selected.isAdopted?'この歌詞への確認依頼をコピー':'この候補の採用依頼をコピー'}</button><p>${comparing?'左側の歌詞 A が依頼対象です。 ':''}コピーするだけでは採用・公開されません。</p><p class="mono" id="candidate-reference">${esc(selected.reference)}</p></div>${!selected.isAdopted?`<details class="evidence"><summary>候補の識別情報・出典（ローカルのみ）</summary><p>本文 SHA256: <span class="mono">${selected.sha256}</span></p><ul>${selected.sources.map(s=>`<li>${s.kind==='nas'?'保存原稿':'Suno表示歌詞'} · ${esc(s.label)}${s.url?`<br><a href="${esc(s.url)}" target="_blank" rel="noreferrer">出典を開く</a>`:''}</li>`).join('')}</ul><p>配信音源との一致を確定した表示ではありません。</p></details>`:''}`;
  const change=(v,c)=>{const p={track:track.isrc||track.number,version:v};if(c&&c!==v)p.compare=c;setRoute('/release/'+r.id,p);};
  document.querySelector('#version').onchange=e=>change(e.target.value,compared?.id);
  const toggle=document.querySelector('#compare-toggle');if(toggle)toggle.onchange=e=>change(selected.id,e.target.checked?versions.find(v=>v.id!==selected.id).id:null);
  const second=document.querySelector('#compare-version');if(second)second.onchange=e=>change(selected.id,e.target.value);
  document.querySelector('#adopt-request').onclick=()=>request(`${selected.isAdopted?'歌詞の確認依頼':'歌詞の採用依頼'}\nアーティスト：${a.name}\n作品：${r.title}\n曲：${track.title}\nISRC：${track.isrc}\n候補ID：${selected.reference}\n本文SHA256：${selected.sha256}\n\n${selected.isAdopted?'この採用済み歌詞について確認をお願いします。':'この候補の歌詞をカタログに採用してください。出典リンクや別版は公開しないでください。'}`);
}
async function request(text) {
  document.querySelector('#request-text').value=text;
  try{await navigator.clipboard.writeText(text);toast('依頼文をコピーしました。会話に貼り付けてください。');}
  catch{document.querySelector('#request-dialog').showModal();document.querySelector('#request-text').select();}
}
document.querySelector('#dialog-close').onclick=()=>document.querySelector('#request-dialog').close();
document.querySelector('#dialog-copy').onclick=async()=>{try{await navigator.clipboard.writeText(document.querySelector('#request-text').value);document.querySelector('#request-dialog').close();toast('依頼文をコピーしました。');}catch{document.querySelector('#request-text').select();toast('選択した依頼文を手動でコピーしてください。');}};
async function render() {
  const myToken=++token;const {path,params}=current();
  if(path.startsWith('/release/'))await detailView(decodeURIComponent(path.slice(9)),params,myToken);
  else listView(params);
}
window.addEventListener('hashchange',render);
try{catalog=await fetchJSON('/api/catalog');for(const [key,value] of Object.entries(catalog.brand?.colors||{})){if(['accent','background'].includes(key)&&/^#[0-9a-f]{6}$/i.test(value))document.documentElement.style.setProperty(key==='background'?'--page-background':'--accent',value);}await render();}catch(e){app.innerHTML=`<p class="loading">${esc(e.message)}<br>${publicMode?'ページを再読み込みしてください。':'ローカルサーバーを起動してから再読み込みしてください。'}</p>`;}
