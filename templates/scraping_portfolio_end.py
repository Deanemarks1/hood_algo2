driver.execute_script("""
/* ============================= */
/* HOODALGO END MODAL v1         */
/* CLEAN + CONTROLLED            */
/* ============================= */

/* REMOVE OVERLAY */
var old_overlay = document.getElementById('blackout_overlay');
if (old_overlay){
    old_overlay.remove();
}

/* REMOVE OLD MODAL */
var old = document.getElementById('hoodalgo_end_modal');
if (old){
    old.remove();
}

/* FONT */
if (!document.getElementById('hoodalgo_font')){
    var font = document.createElement('link');
    font.id = 'hoodalgo_font';
    font.href = 'https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap';
    font.rel = 'stylesheet';
    document.head.appendChild(font);
}

/* OVERLAY */
var overlay = document.createElement('div');
overlay.id = 'hoodalgo_end_modal';
overlay.style.position = 'fixed';
overlay.style.top = '0';
overlay.style.left = '0';
overlay.style.width = '100vw';
overlay.style.height = '100vh';
overlay.style.background = 'rgba(0,0,0,0.6)';
overlay.style.display = 'flex';
overlay.style.alignItems = 'center';
overlay.style.justifyContent = 'center';
overlay.style.zIndex = '999999999';
overlay.style.backdropFilter = 'blur(6px)';
overlay.style.opacity = '0';

/* MODAL */
var modal = document.createElement('div');
modal.style.width = '92%';
modal.style.maxWidth = '600px';
modal.style.background = '#070c10';
modal.style.borderRadius = '22px';
modal.style.padding = '36px 32px';
modal.style.fontFamily = 'Poppins, sans-serif';
modal.style.boxShadow = '0 40px 120px rgba(0,0,0,0.9)';
modal.style.transform = 'scale(0.85)';
modal.style.opacity = '0';
modal.style.textAlign = 'center';

/* LOGO */
var logo = document.createElement('div');
logo.style.fontSize = '60px';
logo.style.fontWeight = '800';
logo.style.marginBottom = '16px';
logo.innerHTML = '<span style="color:#00ff9d;">Hood</span><span style="color:white;">Algo</span>';

/* CHECK (SVG DRAW STYLE) */
var check = document.createElement('div');
check.innerHTML = `
<svg viewBox="0 0 24 24" width="60" height="60" fill="none"
     stroke="white" stroke-width="3"
     stroke-linecap="round" stroke-linejoin="round">
    <path id="check_path" d="M5 13l4 4L19 7"
          stroke-dasharray="30"
          stroke-dashoffset="30"/>
</svg>
`;
check.style.margin = '30px 0';
check.style.opacity = '0';
check.style.transform = 'scale(0.5)';

/* MAIN TEXT */
var main = document.createElement('div');
main.innerText = 'Portfolio Updated';
main.style.fontSize = '28px';
main.style.fontWeight = '800';
main.style.color = 'white';
main.style.marginBottom = '10px';
main.style.opacity = '0';

/* SUB TEXT */
var sub = document.createElement('div');
sub.innerText = 'Portfolio scraped - database updated';
sub.style.fontSize = '15px';
sub.style.color = '#9ca3af';
sub.style.marginBottom = '24px';
sub.style.opacity = '0';

/* PROGRESS BAR (CLEAN FINISH LINE) */
var progress_container = document.createElement('div');
progress_container.style.width = '100%';
progress_container.style.height = '5px';
progress_container.style.background = '#111';
progress_container.style.borderRadius = '10px';
progress_container.style.overflow = 'hidden';

var progress_bar = document.createElement('div');
progress_bar.style.width = '0%';
progress_bar.style.height = '100%';
progress_bar.style.background = 'white';
progress_container.appendChild(progress_bar);

/* ANIMATIONS */
if (!document.getElementById('hoodalgo_end_anim')){
    var style = document.createElement('style');
    style.id = 'hoodalgo_end_anim';
    style.innerHTML = ''

    + '@keyframes fade_in { to { opacity:1; } }'

    + '@keyframes modal_pop {'
    + '0% { transform:scale(0.7); opacity:0; }'
    + '60% { transform:scale(1.05); }'
    + '100% { transform:scale(1); opacity:1; }'
    + '}'

    + '@keyframes draw_check { to { stroke-dashoffset:0; } }'

    + '@keyframes pop_check {'
    + '0% { transform:scale(0.5); opacity:0; }'
    + '70% { transform:scale(1.2); }'
    + '100% { transform:scale(1); opacity:1; }'
    + '}'

    + '@keyframes fill_bar { to { width:100%; } }';

    document.head.appendChild(style);
}

/* BUILD */
modal.appendChild(logo);
modal.appendChild(check);
modal.appendChild(main);
modal.appendChild(sub);
modal.appendChild(progress_container);

overlay.appendChild(modal);
document.body.appendChild(overlay);

/* ANIMATE */
overlay.style.animation = 'fade_in 0.25s ease forwards';

setTimeout(function(){
    modal.style.animation = 'modal_pop 0.45s cubic-bezier(.2,1.4,.4,1) forwards';
},50);

/* CHECK DRAW */
setTimeout(function(){
    check.style.animation = 'pop_check 0.4s ease forwards';
    var path = check.querySelector('#check_path');
    path.style.animation = 'draw_check 0.35s ease forwards';
},200);

/* TEXT */
setTimeout(function(){
    main.style.animation = 'fade_in 0.4s ease forwards';
},400);

setTimeout(function(){
    sub.style.animation = 'fade_in 0.4s ease forwards';
},550);

/* BAR */
setTimeout(function(){
    progress_bar.style.animation = 'fill_bar 0.5s ease forwards';
},300);

/* CLOSE */
setTimeout(function(){
    overlay.style.transition = 'opacity 0.35s ease';
    overlay.style.opacity = '0';
    setTimeout(function(){ overlay.remove(); },350);
},2400);

/* ============================= */
/* END */
/* ============================= */

""")