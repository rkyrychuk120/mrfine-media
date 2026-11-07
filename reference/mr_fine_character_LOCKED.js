// Mr Fine character design, LOCKED by owner on 7 Nov 2026. Do not change shape, colors, outline or proportions.
// Needs helpers from scene.html: g(), blinkAt(), T.
function mrFine(o){ // traced from Episode 1 end card (coords: feet at 215,692)
  const t=T, S=(o.s||0.9)*0.34, bob=0;
  const m=o.mouth||0, emo=o.emo||'neutral';
  const OL='#141218', BONE='#F3EBDC', HOOD='#3B3448', HEM='#28232F', PINK='#E48AA5', PINKD='#C96E8C';
  const W=14;
  const aL=o.armL||[-11,0], aR=o.armR||[11,0];
  const armF=(sx,a)=>{const r=Math.PI/180;const sy=420;const ex=sx+Math.sin(a[0]*r)*74,ey=sy+Math.cos(a[0]*r)*74,hx=ex+Math.sin((a[0]+a[1])*r)*84,hy=ey+Math.cos((a[0]+a[1])*r)*84;const p=`M${sx},${sy} L${ex},${ey} L${hx},${hy}`;
    return {s:`<path d="${p}" fill="none" stroke="${OL}" stroke-width="${52+W*2}" stroke-linecap="round" stroke-linejoin="round"/><path d="${p}" fill="none" stroke="${HOOD}" stroke-width="52" stroke-linecap="round" stroke-linejoin="round"/>`,hx,hy}};
  const L_=armF(108,aL), R_=armF(330,aR);
  const hand=(h,kind,side)=>{
    if(kind==='thumb') return `<g transform="translate(${h.hx},${h.hy}) scale(${side},1)"><rect x="-30" y="-24" width="60" height="54" rx="22" fill="${BONE}" stroke="${OL}" stroke-width="${W}"/><rect x="-24" y="-72" width="26" height="56" rx="13" fill="${BONE}" stroke="${OL}" stroke-width="${W}"/></g>`;
    if(kind==='point') return `<g transform="translate(${h.hx},${h.hy})"><rect x="-11" y="-74" width="22" height="52" rx="11" fill="${BONE}" stroke="${OL}" stroke-width="${W}"/><circle r="33" fill="${BONE}" stroke="${OL}" stroke-width="${W}"/></g>`;
    if(kind==='remote') return `<g transform="translate(${h.hx},${h.hy}) rotate(${o.remoteAng==null?70:o.remoteAng})"><rect x="-24" y="-100" width="48" height="104" rx="12" fill="#2A2730" stroke="${OL}" stroke-width="7"/><circle cx="0" cy="-78" r="11" fill="${o.press?'#ff7b7b':'#E2463A'}"/><rect x="-13" y="-56" width="26" height="7" fill="#8a8590"/><rect x="-13" y="-42" width="26" height="7" fill="#8a8590"/><circle r="33" fill="${BONE}" stroke="${OL}" stroke-width="${W}"/></g>`;
    return `<circle cx="${h.hx}" cy="${h.hy}" r="33" fill="${BONE}" stroke="${OL}" stroke-width="${W}"/>`;
  };
  let sv='';
  [[165,150],[260,275]].forEach(([lx,fx],i)=>{const sw=o.walk!=null?Math.sin(o.walk*Math.PI*2+i*Math.PI)*20:0;
    sv+=`<rect x="${lx-15+sw*0.4}" y="585" width="30" height="62" fill="${BONE}" stroke="${OL}" stroke-width="${W}"/><ellipse cx="${fx+sw}" cy="660" rx="52" ry="30" fill="${BONE}" stroke="${OL}" stroke-width="${W}"/>`});
  sv+=`<path d="M106,540 L334,540 L336,584 Q336,598 322,598 L120,598 Q104,598 104,584 Z" fill="${PINK}" stroke="${OL}" stroke-width="${W}" stroke-linejoin="round"/><rect x="124" y="566" width="80" height="10" rx="4" fill="${PINKD}"/><rect x="236" y="566" width="80" height="10" rx="4" fill="${PINKD}"/><path d="M220,544 L220,596" stroke="${OL}" stroke-width="8"/>`;
  sv+=L_.s;
  sv+=`<path d="M134,388 Q104,392 100,440 L94,518 Q92,548 118,548 L326,548 Q350,548 348,518 L342,440 Q338,392 310,388 Z" fill="url(#mfhood)" stroke="${OL}" stroke-width="${W}" stroke-linejoin="round"/>`;
  sv+=`<path d="M96,512 L346,512 L348,524 Q350,544 326,544 L118,544 Q94,544 94,524 Z" fill="${HEM}"/>`;
  sv+=`<rect x="183" y="400" width="12" height="20" rx="4" fill="#E8E3EA"/><rect x="243" y="400" width="12" height="20" rx="4" fill="#E8E3EA"/>`;
  sv+=`<g transform="translate(220,470) scale(.7)"><path d="M-62,10 C-78,6 -76,-24 -56,-28 C-58,-50 -28,-56 -16,-42 C-6,-58 22,-56 26,-38 C48,-46 62,-22 50,-8 C68,4 58,34 36,30 C30,48 2,48 -4,34 C-18,48 -48,42 -46,24 C-62,26 -70,16 -62,10Z" fill="#EE93AE" stroke="#C76487" stroke-width="5"/><path d="M0,-40 C-8,-14 8,6 0,38 M-40,-10 C-26,-6 -24,8 -34,14 M38,-14 C24,-8 24,6 36,12" stroke="#C76487" stroke-width="5" fill="none" stroke-linecap="round"/><ellipse cx="-28" cy="-26" rx="8" ry="5" fill="#fff" opacity=".7"/></g>`;
  sv+=R_.s+hand(L_,o.handL,-1)+hand(R_,o.handR,1);
  // head: round cranium + short narrow jaw
  let h=`<path d="M106.0,70.0 C96.0,76.3 82.3,86.7 74.0,94.0 C65.7,101.3 61.0,107.7 56.0,114.0 C51.0,120.3 48.3,123.7 44.0,132.0 C39.7,140.3 33.0,155.3 30.0,164.0 C27.0,172.7 26.7,172.3 26.0,184.0 C25.3,195.7 24.7,220.7 26.0,234.0 C27.3,247.3 30.7,255.0 34.0,264.0 C37.3,273.0 41.3,280.8 46.0,288.0 C50.7,295.2 55.0,300.7 62.2,307.2 C69.3,313.7 80.1,321.0 89.0,327.0 C97.9,333.0 109.9,339.3 115.6,343.2 C121.3,347.1 121.6,344.7 123.2,350.4 C124.8,356.1 123.8,371.4 125.1,377.4 C126.4,383.4 127.3,383.1 130.8,386.4 C134.3,389.7 141.9,395.1 146.0,397.2 C150.1,399.3 132.7,398.7 155.5,399.0 C178.3,399.3 258.7,399.9 282.8,399.0 C306.9,398.1 294.8,396.9 299.9,393.6 C305.0,390.3 310.3,383.7 313.2,379.2 C316.1,374.7 316.4,371.7 317.0,366.6 C317.6,361.5 311.9,354.9 317.0,348.6 C322.1,342.3 337.2,336.0 347.4,328.8 C357.6,321.6 370.7,312.5 378.4,305.4 C386.2,298.3 389.1,294.6 394.0,286.0 C398.9,277.4 405.0,262.3 408.0,254.0 C411.0,245.7 411.3,241.7 412.0,236.0 C412.7,230.3 411.7,223.0 412.0,220.0 C412.3,217.0 414.0,224.3 414.0,218.0 C414.0,211.7 413.7,193.0 412.0,182.0 C410.3,171.0 407.3,161.0 404.0,152.0 C400.7,143.0 397.0,136.0 392.0,128.0 C387.0,120.0 382.3,112.7 374.0,104.0 C365.7,95.3 352.0,83.3 342.0,76.0 C332.0,68.7 325.7,65.0 314.0,60.0 C302.3,55.0 282.3,48.7 272.0,46.0 C261.7,43.3 255.7,44.7 252.0,44.0 C248.3,43.3 260.7,42.3 250.0,42.0 C239.3,41.7 203.3,41.0 188.0,42.0 C172.7,43.0 167.0,45.7 158.0,48.0 C149.0,50.3 142.7,52.3 134.0,56.0 C125.3,59.7 116.0,63.7 106.0,70.0Z" fill="${BONE}" stroke="${OL}" stroke-width="${W}" stroke-linejoin="round"/>`;
  h+=`<path d="M282,60 L270,94 L294,112" fill="none" stroke="${OL}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>`;
  const blink=blinkAt(t,7)||o.blink;
  const eye=(cx,isR)=>{
    const wink=isR&&o.wink;
    if(blink||wink||emo==='happy') return `<path d="M${cx-30},${222} Q${cx},${190} ${cx+30},${222}" fill="none" stroke="${OL}" stroke-width="12" stroke-linecap="round"/>`;
    const r=emo==='shock'?52:46;
    return `<circle cx="${cx}" cy="212" r="${r}" fill="#1E1A24"/><circle cx="${cx+6}" cy="${200}" r="${emo==='shock'?16:21}" fill="#fff"/>`;
  };
  h+=eye(142,false)+eye(300,true);
  const brow=(x1,y1,x2,y2)=>`<path d="M${x1},${y1} L${x2},${y2}" stroke="${OL}" stroke-width="11" stroke-linecap="round"/>`;
  if(emo==='worried'||emo==='sad') h+=brow(102,162,170,146)+brow(274,146,342,162);
  else if(emo==='serious') h+=brow(104,144,172,158)+brow(272,158,340,144);
  else if(emo==='curious') h+=`<path d="M266,144 Q302,120 340,140" fill="none" stroke="${OL}" stroke-width="11" stroke-linecap="round"/>`;
  if(o.sweat||emo==='worried') h+=`<path d="M392,104 C404,126 410,138 400,150 C390,160 372,154 374,138 C376,126 386,116 392,104Z" fill="#8CC8EE" stroke="${OL}" stroke-width="7"/>`;
  h+=`<path d="M207,282 L233,282 L220,304 Z" fill="${OL}"/>`;
  h+=`<circle cx="95" cy="280" r="36" fill="#D6CBC0" opacity=".55"/><ellipse cx="100" cy="286" rx="28" ry="10" fill="#EC9DAA" opacity=".85"/><circle cx="350" cy="280" r="36" fill="#D6CBC0" opacity=".55"/><ellipse cx="345" cy="286" rx="28" ry="10" fill="#EC9DAA" opacity=".85"/>`;
  // mouth: Ep1 style
  if(m>0.07) h+=`<ellipse cx="222" cy="347" rx="${24+m*6}" ry="${5+m*16}" fill="#1E1A24"/>`;
  else if(emo==='shock') h+=`<ellipse cx="222" cy="347" rx="17" ry="21" fill="#1E1A24"/>`;
  else if(emo==='worried'||emo==='sad') h+=`<path d="M190,355 Q222,339 254,355" fill="none" stroke="${OL}" stroke-width="10" stroke-linecap="round"/>`;
  else if(emo==='serious') h+=`<path d="M194,347 L250,347" stroke="${OL}" stroke-width="10" stroke-linecap="round"/>`;
  else if(emo==='happy'||o.smile) h+=`<path d="M181,336 Q222,363 263,336" fill="none" stroke="${OL}" stroke-width="10" stroke-linecap="round"/>`;
  else h+=`<path d="M196,347 Q222,339 248,347 Q222,355 196,347 Z" fill="#1E1A24" stroke="#1E1A24" stroke-width="6" stroke-linejoin="round"/>`;
  const tilt=(o.tilt||0)+(o.shakeHead?Math.sin(t*14)*6:0)+(o.nod?Math.sin(t*10)*3:0);
  sv+=g(`translate(0,5) rotate(${tilt},220,400)`,h);
  return g(`translate(${o.x},${o.y+bob*S}) scale(${(o.flip?-1:1)*S},${S}) translate(-215,-692)`,sv);
}
