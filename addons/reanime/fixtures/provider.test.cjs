const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(require('node:path').join(__dirname,'../index.js'),'utf8');
const base = 'https://reanime.to';
const dto = {anime_id:'show-abc',anilist_id:123,mal_id:456,imdb_id:'tt1234567',title:{english:'Show',romaji:'Shou'},episodes_total:2,season_year:2020};
function harness(overrides={}) {
  const calls=[], storage=new Map();
  const responses=new Map([
    [base+'/api/v1/anime/show-abc',dto],
    [base+'/api/v1/anime/show-abc/episodes?limit=2000',{data:[{episode_number:1,title:'First',episodeId:'rotating-token'},{episode_number:2,title:'Second'},{episode_number:2,title:'Duplicate'},{episode_number:3,playable:false},{episode_number:1.5}]}],
    [base+'/api/flix/123/1',{success:true,servers:[{dataLink:'https://flixcloud.cc/e/abc?v=1',serverName:'HD-1',dataType:'sub'},{dataLink:'https://flixcloud.cc/e/abc?v=1',serverName:'HD-1',dataType:'sub'},{dataLink:'http://127.0.0.1/private',dataType:'dub'},{dataLink:'https://flixcloud.cc/e/abc?v=1',serverName:'HD-1',dataType:'dub'}]}],
    [base+'/api/v1/search?q=Show&limit=12&offset=0',{results:[dto]}],
    ...Object.entries(overrides),
  ]);
  function http(url,request) {calls.push({url,request}); if(!responses.has(url)) throw new Error('Unexpected request '+url); const value=responses.get(url);return JSON.stringify({status:200,body:typeof value==='string'?value:JSON.stringify(value)});}
  const nova={http:{get:(u)=>http(u),request:raw=>{const r=JSON.parse(raw);return http(r.url,r);}},storage:{get:k=>storage.get(k)||'',set:(k,v)=>storage.set(k,v)},crypto:{base64UrlEncode:s=>Buffer.from(s).toString('base64url'),base64UrlDecode:s=>Buffer.from(s,'base64url').toString()},metadata:{available:()=>false,resolveEpisode:()=>JSON.stringify({status:'ambiguous'})}};
  const context={nova};vm.runInNewContext(source,context);
  const handle=r=>JSON.parse(JSON.stringify(context.novaProvider.handle(r)));
  return {handle,calls,nova,responses};
}
const id='ep:'+Buffer.from(JSON.stringify({slug:'show-abc',number:1})).toString('base64url');
test('details preserve source identity, available episodes and explicit IDs',()=>{
 const h=harness();const d=h.handle({op:'details',sourceId:'show-abc'});
 assert.equal(d.media.external_ids.anilist,'123'); assert.equal(d.media.external_ids.imdb,'tt1234567');
 assert.deepEqual(d.episodes.map(e=>e.number),[1,2]); assert.equal(d.episodes[0].source_id,id);
 h.responses.get(base+'/api/v1/anime/show-abc/episodes?limit=2000').data[0].episodeId='new-token';
 assert.equal(h.handle({op:'details',sourceId:'show-abc'}).episodes[0].source_id,id);
});
test('latest follows snake-case cursor and never repeats page one for unknown offsets',()=>{
 const h=harness({[base+'/api/v1/home/latest-aired?limit=12&lang=']:{data:[dto],has_more:true,next_cursor:'next+/='},[base+'/api/v1/home/latest-aired?limit=12&lang=&cursor=next%2B%2F%3D']:{data:[dto],has_more:false,next_cursor:null}});
 assert.equal(h.handle({op:'catalog',catalogId:'reanime.latest',extra:{skip:'0'}}).length,1);
 assert.equal(h.handle({op:'catalog',catalogId:'reanime.latest',extra:{skip:'1'}}).length,1);
 const count=h.calls.length;assert.deepEqual(h.handle({op:'catalog',catalogId:'reanime.latest',extra:{skip:'2'}}),[]);assert.equal(h.calls.length,count);
});
test('discovery deduplicates servers, retains audio variants and defers secrets',()=>{
 const h=harness();const streams=h.handle({op:'streams',episodeId:id});assert.equal(streams.length,2);
 assert.ok(streams.every(s=>!s.url&&s.resolver.provider_id==='reanime'));assert.ok(streams[1].title.includes('[dub]'));
 assert.throws(()=>h.handle({op:'streams',episodeId:'ep:'+Buffer.from('{"slug":"../escape","number":1}').toString('base64url')}));
});
test('ambiguous contextual lookup emits no guessed episodes',()=>{
 const h=harness();assert.deepEqual(h.handle({op:'lookupStreams',lookup:{title:'Show',season:1,episode:1}}),[]);
 h.nova.metadata.resolveEpisode=raw=>{const r=JSON.parse(raw);assert.equal(r.sourceSequences[0].episodes[0].id,'reanime:'+id);return JSON.stringify({status:'confirmed',sourceEpisodeId:'reanime:'+id});};
 assert.equal(h.handle({op:'lookupStreams',lookup:{title:'Show',season:1,episode:1}}).length,2);
});
test('capability switches gate public operations and retain internal stream lookup',()=>{
 const h=harness();const manifest={resources:['catalog','meta','stream'],catalogs:[{}],types:['series']};
 assert.deepEqual(h.handle({op:'manifest',manifest,config:{metadata:false}}).resources,['stream']);
 assert.deepEqual(h.handle({op:'catalog',catalogId:'reanime.popular',config:{metadata:false}}),[]);
 assert.equal(h.handle({op:'streams',episodeId:id,config:{metadata:false}}).length,2);
 assert.deepEqual(h.handle({op:'streams',episodeId:id,config:{streams:false}}),[]);
});
test('resolver parses site literals without evaluation and supplies host relay data',()=>{
 const h=harness({
 'https://flixcloud.cc/e/abc?v=1':'<link href="/hls.js"><script>type:"data",data:{value:"a,b: undefined",optional:undefined,subtitles:[{url:"https://flixcloud.cc/sub.vtt",language:"English"},],intro_chapter:{start:1},},uses:</script>',
 'https://flixcloud.cc/hls.js':'for(var f=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]',
 'https://enc-dec.app/api/dec-flixcloud?type=token':{status:200,result:{token:'short-lived',context:{session:'context'}}},
 'https://flixcloud.cc/api/m3u8/short-lived':{encrypted:'stream'},
 'https://enc-dec.app/api/dec-flixcloud?type=stream':{status:200,result:{stream:'https://fetch.flixcloud.cc/master.m3u8?token=secret',context:{w_payload:'payload'}}},
 });
 const s=h.handle({op:'streams',episodeId:id})[0]; const resolved=h.handle({op:'resolveStream',token:s.resolver.token});
 assert.equal(resolved.hlsProxy.mask[15],16);assert.equal(resolved.hlsProxy.wPayload,'payload');assert.equal(resolved.subtitles[0].language,'English');
 const payload=h.calls.find(c=>c.url.endsWith('type=token')).request.body.value.data;
 assert.equal(payload.value,'a,b: undefined');assert.equal(payload.optional,null);assert.equal(payload.subtitles,undefined);assert.equal(payload.intro_chapter,undefined);
 assert.throws(()=>h.handle({op:'resolveStream',token:Buffer.from(JSON.stringify({episode:id,link:'https://evil.example/e/abc'})).toString('base64url')}));
});
