const $=id=>document.getElementById(id);
const canvas=$('game'),ctx=canvas.getContext('2d');
const sprite=new Image();sprite.src='assets/clawd.png';
let animations={};
try{animations=await(await fetch('assets/animations.json')).json();await sprite.decode()}catch{$('overlayText').textContent='Sprites could not load. Please refresh.'}
let W=1000,H=340,dpr=1,ground=280;
let mode='ready',elapsed=0,distance=0,coins=0,score=0,best=0,obstacles=[],loot=[],particles=[],spawn=1.5,last=0,frame=0,shake=0,milestoneTimer=0,lastMilestone=0;
let sound=false,audio,player={x:120,y:ground,vy:0,grounded:true},jumpQueued=0;
try{best=Number(localStorage.getItem('clawd-best-v1'))||0}catch{}
const number=n=>String(Math.floor(n)).padStart(5,'0');
function hud(){$('score').textContent=number(score);$('coins').textContent=coins;$('best').textContent=number(best)}
function resize(){const rect=canvas.getBoundingClientRect(),oldGround=ground;W=rect.width;H=rect.height;ground=H-49;dpr=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.imageSmoothingEnabled=false;player.x=Math.max(58,W*.135);player.y=player.grounded?ground:player.y+(ground-oldGround)}
new ResizeObserver(resize).observe(canvas);resize();hud();
function beep(freq,length=.07){if(!sound)return;try{audio??=new(window.AudioContext||window.webkitAudioContext)();audio.resume();const o=audio.createOscillator(),g=audio.createGain();o.type='sine';o.frequency.setValueAtTime(freq,audio.currentTime);o.frequency.exponentialRampToValueAtTime(freq*1.3,audio.currentTime+length);g.gain.setValueAtTime(.035,audio.currentTime);g.gain.exponentialRampToValueAtTime(.001,audio.currentTime+length);o.connect(g);g.connect(audio.destination);o.start();o.stop(audio.currentTime+length)}catch{}}
function dust(x,y,color,count=8){for(let i=0;i<count;i++)particles.push({x,y,vx:(Math.random()-.5)*130,vy:-Math.random()*110,life:.4+Math.random()*.3,color});if(particles.length>120)particles.splice(0,particles.length-120)}
function overlay(tag,title,text,button){$('overlayTag').textContent=tag;$('overlayTitle').textContent=title;$('overlayText').textContent=text;$('start').innerHTML=button+' <span>→</span>';$('overlay').classList.remove('hidden')}
function start(){mode='running';elapsed=0;distance=0;coins=0;score=0;obstacles=[];loot=[];particles=[];spawn=1.7;lastMilestone=0;jumpQueued=0;player.y=ground;player.vy=0;player.grounded=true;$('overlay').classList.add('hidden');$('pause').textContent='Ⅱ';$('pause').setAttribute('aria-label','Pause game');hud();canvas.focus({preventScroll:true})}
function jump(){if(mode==='ready'||mode==='over'){start();return}if(mode==='paused'){pause();return}jumpQueued=.12;if(player.grounded)performJump()}
function performJump(){player.vy=-660;player.grounded=false;jumpQueued=0;dust(player.x,ground,'#a37655',5);beep(300,.05)}
function pause(){if(mode==='running'){mode='paused';overlay('TAKE YOUR TIME','A tiny breather.','Your run is right where you left it.','Keep running');$('pause').textContent='▶';$('pause').setAttribute('aria-label','Resume game')}else if(mode==='paused'){mode='running';$('overlay').classList.add('hidden');$('pause').textContent='Ⅱ';$('pause').setAttribute('aria-label','Pause game');canvas.focus({preventScroll:true})}}
function end(){mode='over';shake=.2;dust(player.x,player.y-20,'#d97a58',14);const record=score>best;if(record){best=score;try{localStorage.setItem('clawd-best-v1',String(best))}catch{}}hud();overlay(record?'NEW PERSONAL BEST':'ONE MORE TRY?','Run complete.',`${score.toLocaleString()} points · ${coins} coins collected`,'Run it back');beep(130,.16)}
$('start').onclick=()=>mode==='paused'?pause():start();$('pause').onclick=pause;
$('jump').onpointerdown=e=>{e.preventDefault();jump()};canvas.onpointerdown=e=>{e.preventDefault();jump()};
$('sound').onclick=()=>{sound=!sound;$('sound').setAttribute('aria-pressed',String(sound));$('sound').setAttribute('aria-label',sound?'Turn sound off':'Turn sound on');$('soundState').textContent=sound?'ON':'OFF';if(sound)beep(700)};
$('resetBest').onclick=()=>{best=0;try{localStorage.removeItem('clawd-best-v1')}catch{}hud()};
addEventListener('keydown',e=>{if(e.target instanceof HTMLButtonElement||e.target instanceof HTMLAnchorElement)return;if(['Space','ArrowUp','KeyW'].includes(e.code)){e.preventDefault();if(!e.repeat)jump()}if(e.code==='KeyP'){e.preventDefault();pause()}if(e.code==='KeyR'){e.preventDefault();start()}});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&mode==='running')pause()});
function pose(name,time){const frames=animations[name]||animations.Idle;if(!frames)return;const total=frames.reduce((n,f)=>n+Number(f.Delay),0);let t=time%total;for(const f of frames){if(t<Number(f.Delay))return f;t-=Number(f.Delay)}return frames[0]}
function drawClawd(){const name=mode==='running'?'WalkSide':mode==='over'?'Idle':'Wave';const f=pose(name,frame*30);if(!f)return;const scale=2;ctx.save();ctx.translate(Math.round(player.x),Math.round(player.y));ctx.drawImage(sprite,Number(f.XCrop),Number(f.YCrop),Number(f.Width),Number(f.Height),-Number(f.XPivot)*scale,-Number(f.YPivot)*scale,Number(f.Width)*scale,Number(f.Height)*scale);ctx.restore()}
function coin(x,y,t){const width=3+Math.abs(Math.cos(t*4))*6;ctx.fillStyle='#785430';ctx.fillRect(Math.round(x-width-2),Math.round(y-9),Math.round(width*2+4),18);ctx.fillStyle='#e8b85d';ctx.fillRect(Math.round(x-width),Math.round(y-7),Math.round(width*2),14);ctx.fillStyle='#ffdf98';ctx.fillRect(Math.round(x-width+1),Math.round(y-5),2,8)}
function block(o){ctx.fillStyle='#171614';ctx.fillRect(o.x+4,ground+1,o.w,5);ctx.fillStyle='#84503a';ctx.fillRect(o.x,ground-o.h,o.w,o.h);ctx.fillStyle='#d18359';ctx.fillRect(o.x+2,ground-o.h+2,o.w-4,5);ctx.fillStyle='#b36b48';ctx.fillRect(o.x+3,ground-o.h+8,o.w-6,o.h-8);ctx.fillStyle='#5c372a';ctx.fillRect(o.x+o.w-5,ground-o.h+8,3,o.h-8)}
function update(dt){frame+=dt;if(milestoneTimer>0){milestoneTimer-=dt;if(milestoneTimer<=0)$('milestone').classList.remove('show')}if(mode!=='running'){shake=Math.max(0,shake-dt);return}elapsed+=dt;const speed=Math.min(Math.max(205,W*.34)+elapsed*2.5,Math.max(260,W*.55));distance+=speed*dt;score=Math.floor(distance/10)+coins*25;
 jumpQueued=Math.max(0,jumpQueued-dt);player.vy+=2100*dt;player.y+=player.vy*dt;if(player.y>=ground){if(!player.grounded)dust(player.x,ground,'#78604a',4);player.y=ground;player.vy=0;player.grounded=true;if(jumpQueued>0)performJump()}
 spawn-=dt;if(spawn<=0){
  const x=W+40,spacing=Math.max(24,speed*.095);
  obstacles.push({x,w:22+Math.floor(Math.random()*11),h:27+Math.floor(Math.random()*14)});
  // One obstacle, one coin arc, one jump. Match the coins to the actual jump curve.
  for(let j=0;j<4;j++){
   const time=.15+j*.09;
   const rise=660*time-1050*time*time;
   loot.push({x:x-.8*spacing+j*spacing,y:ground-23-rise});
  }
  spawn=1.8+Math.random()*.6;
 }

 for(const o of obstacles)o.x-=speed*dt;for(const c of loot)c.x-=speed*dt;
 // Hitboxes are deliberately a little kinder than the visible pixel edges.
 const px=player.x-17,py=player.y-43;
 for(const o of obstacles)if(px+31>o.x+4&&px<o.x+o.w-4&&py+39>ground-o.h+5&&py<ground){end();return}
 for(const c of loot){if(!c.taken&&Math.abs(c.x-player.x)<36&&Math.abs(c.y-(player.y-23))<42){c.taken=true;coins++;dust(c.x,c.y,'#e8b85d',7);beep(800+(coins%4)*100,.05)}}
 obstacles=obstacles.filter(o=>o.x+o.w>-30);loot=loot.filter(c=>c.x>-30&&!c.taken);
 const mark=Math.floor(coins/10);if(mark>lastMilestone){lastMilestone=mark;$('milestone').textContent=`${mark*10} coins. Keep that little guy going.`;$('milestone').classList.add('show');milestoneTimer=2.2}
 for(const p of particles){p.life-=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=300*dt}particles=particles.filter(p=>p.life>0);hud()}
function draw(){ctx.setTransform(dpr,0,0,dpr,0,0);ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,W,H);ctx.fillStyle='#201d1b';ctx.fillRect(0,0,W,H);ctx.save();if(shake>0)ctx.translate((Math.random()-.5)*4,(Math.random()-.5)*3);
 // Slow parallax, a warm sun, and restrained pixel terrain.
 ctx.fillStyle='#302821';ctx.beginPath();ctx.arc(W*.78,H*.35,41,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#48352b';ctx.beginPath();ctx.arc(W*.78,H*.35,52,Math.PI*.2,Math.PI*1.1);ctx.stroke();
 for(let j=0;j<16;j++){const x=((j*97-distance*.08)%(W+120)+W+120)%(W+120)-40;const h=23+(j*17)%48;ctx.fillStyle=j%2?'#2d2520':'#302720';ctx.fillRect(x,ground-h,35+(j%3)*15,h)}
 ctx.fillStyle='#5b4030';ctx.fillRect(0,ground+3,W,2);ctx.fillStyle='#261f1b';ctx.fillRect(0,ground+5,W,H-ground);
 for(let j=0;j<Math.ceil(W/28)+2;j++){const x=(j*28-distance*.8)% (W+56);ctx.fillStyle='#443025';ctx.fillRect(x,ground+15+(j%3)*7,8+(j%2)*7,2)}
 if(mode==='ready'&&loot.length===0)for(let j=0;j<4;j++)coin(W*.56+j*31,ground-65-Math.sin(j)*8,frame+j);
 for(const c of loot)coin(c.x,c.y,frame+c.x*.01);for(const o of obstacles)block(o);
 ctx.fillStyle='#15131155';ctx.beginPath();ctx.ellipse(player.x,ground+3,21,4,0,0,Math.PI*2);ctx.fill();drawClawd();
 for(const p of particles){ctx.globalAlpha=Math.min(1,p.life*3);ctx.fillStyle=p.color;ctx.fillRect(p.x,p.y,3,3)}ctx.globalAlpha=1;ctx.restore()}
function loop(now){const dt=Math.min((now-last)/1000||0,.035);last=now;update(dt);draw();requestAnimationFrame(loop)}requestAnimationFrame(loop);
// Read-only state makes browser QA possible without changing game behavior.
Object.defineProperty(window,'coinRunState',{get:()=>({mode,score,coins,best,grounded:player.grounded,playerY:player.y,ground,obstacles:obstacles.map(o=>({...o})),loot:loot.map(c=>({...c})),width:W})});
