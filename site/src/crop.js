function cropPhoto(g){
  // parchment coffee drying on a blue tarp, seen from above (a cheap phone photo)
  const R=i=>{const x=Math.sin(i*78.233+g.charCodeAt(0)*3.17)*43758.5453;return x-Math.floor(x)};
  let s=`<rect width="120" height="90" fill="#3D6C8A"/><path d="M0 30 L120 26 M0 62 L120 66 M40 0 L44 90 M86 0 L82 90" stroke="#335C76" stroke-width="1.4"/>`;
  let k=0;
  for(let r=0;r<9;r++)for(let c=0;c<12;c++){
    const x=6+c*9.7+(R(k)-.5)*4,y=6+r*9.7+(R(k+500)-.5)*4,rot=Math.floor(R(k+900)*180),u=R(k+1300);
    let f='#D8BC86',e='#B0925F';
    if(g==='B'){if(u<.16){f='#B08552';e='#8A6540'}else if(u>.96){f='#2E241C';e='#1B1510'}}
    if(g==='C'){if(u<.28){f='#86633F';e='#634830'}else if(u<.42){f='#2E241C';e='#1B1510'}else if(u<.5){f='#9AA08A';e='#7C826E'}}
    s+=`<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${rot})"><ellipse rx="4.3" ry="3" fill="${f}"/><path d="M-3 0 C -1 -1 1 1 3 0" stroke="${e}" stroke-width=".8" fill="none"/></g>`;k++}
  if(g==='C')s+=`<path d="M70 48 L96 40" stroke="#5A4630" stroke-width="2.2" stroke-linecap="round"/><ellipse cx="30" cy="66" rx="5" ry="4" fill="#8E8A80"/>`;
  return `<svg viewBox="0 0 120 90" xmlns="http://www.w3.org/2000/svg">${s}</svg>`;
}
