import {createFalClient} from '@fal-ai/client';
import {wma} from '@fal-ai/client/realtime';
const demo=await (await fetch('/demo.json')).json();
const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d'),video=document.querySelector('video');
const poster=new Image();poster.src='/opening.jpg';await poster.decode();
let session,recorder,audioContext,destination,stopped=false,timers=[],version=1,generated=0,started=0,caption=null;
const events=e=>window.saveEvent?.({at:new Date().toISOString(),...e});
const status=s=>document.querySelector('#status').textContent=s;
const audios=await Promise.all([0,1,2].map(async i=>{const a=new Audio(`/audio/${i}.mp3`);a.preload='auto';return a;}));
function draw(){
 ctx.fillStyle='#101927';ctx.fillRect(0,0,1280,800);
 ctx.drawImage(video.readyState>=2?video:poster,0,0,1280,650);
 ctx.fillStyle='#101927';ctx.fillRect(0,650,1280,150);
 ctx.fillStyle='#eef4ff';ctx.textAlign='center';ctx.font='32px "Yu Gothic",sans-serif';
 ctx.fillText(caption?.jp||'もういちど、あした',640,707);
 ctx.fillStyle='#b2c5da';ctx.font='23px sans-serif';ctx.fillText(caption?.en||'Tomorrow, Once More · Learn Japanese through story',640,750);
 requestAnimationFrame(draw);
}draw();
async function speak(i,c){caption=c;await audioContext.resume();audios.forEach(a=>a.pause());audios[i].currentTime=0;await audios[i].play();}
async function choose(index){if(!session||stopped)return;version++;session.send({type:'prompt',prompt_version:version,prompt:demo.choices[index].prompt+' No speech; quiet cafe ambience only.',replan:true});events({type:'choice_sent',id:demo.choices[index].id,prompt_version:version});await speak(index+1,demo.choices[index].caption);}
async function stop(reason){
 if(stopped)return;stopped=true;timers.forEach(clearTimeout);
 try{session?.send({type:'stop'});}catch{}
 try{await Promise.race([session?.close(),new Promise(r=>setTimeout(r,4000))]);}catch{}
 if(recorder?.state==='recording'){recorder.stop();}else window.captureDone=true;
 status('Stopped · '+reason);events({type:'local_stop',reason,estimated_generated_seconds:generated});
}window.stopCapture=stop;
document.querySelector('#start').onclick=async()=>{
 document.querySelector('#start').disabled=true;started=Date.now();
 audioContext=new AudioContext();destination=audioContext.createMediaStreamDestination();
 audios.forEach(a=>audioContext.createMediaElementSource(a).connect(destination));
 const stream=canvas.captureStream(24);destination.stream.getAudioTracks().forEach(t=>stream.addTrack(t));
 const parts=[];recorder=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp9,opus',videoBitsPerSecond:2500000});
 recorder.ondataavailable=e=>{if(e.data.size)parts.push(e.data);};
 recorder.onstop=async()=>{const blob=new Blob(parts,{type:'video/webm'});const reader=new FileReader();reader.onload=async()=>{await window.saveCapture(reader.result.split(',')[1]);window.captureDone=true;};reader.readAsDataURL(blob);};
 timers.push(setTimeout(()=>stop('startup/wall-time watchdog'),85000));
 const fal=createFalClient({proxyUrl:'/api/fal/proxy',retry:{maxRetries:0},requestMiddleware:async request=>({...request,headers:{...request.headers,'x-capture-token':window.captureToken}})});
 try{
 session=fal.realtime.open(wma('minimax/h3-max/director'),{receive:['video','audio'],onMedia:s=>{video.srcObject=s;video.play();},onState:s=>status(String(s)),onError:e=>{events({type:'client_error',message:String(e.message||e)});stop('connection error');},onData:raw=>{
   const m=JSON.parse(raw);events(m);
   if(m.type==='error')stop('server error');
   if(m.type==='chunk'){
     generated+=m.requested_duration_seconds||10;
     if(recorder.state==='inactive'){
       recorder.start(1000);speak(0,demo.opening_captions[1]);
       document.querySelector('#receipt').disabled=false;document.querySelector('#call').disabled=false;
       timers.push(setTimeout(()=>choose(0),15000),setTimeout(()=>choose(1),34000),setTimeout(()=>stop('60-second recording target'),60000));
     }
     if(generated>=70)stop('generated-duration limit');
   }
 }});
 await session.ready;
 session.send({...demo.configure,prompt:demo.configure.prompt+' No dialogue or music; only quiet cafe ambience. Leave the bottom of the picture free of text.'});
 }catch(e){events({type:'capture_error',message:String(e.message||e)});await stop('capture failed');}
};
document.querySelector('#receipt').onclick=()=>choose(0);document.querySelector('#call').onclick=()=>choose(1);document.querySelector('#stop').onclick=()=>stop('manual stop');
window.captureReady=true;
