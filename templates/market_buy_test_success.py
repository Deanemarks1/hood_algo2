driver.execute_script("""

/* ============================= */
/* HOODALGO SUCCESS MODAL v5     */
/* BALANCED SPACING FIX          */
/* ============================= */

/* REMOVE OLD */
var old = document.getElementById('hoodalgo_modal');
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
overlay.id = 'hoodalgo_modal';
overlay.style.position = 'fixed';
overlay.style.top = '0';
overlay.style.left = '0';
overlay.style.width = '100vw';
overlay.style.height = '100vh';
overlay.style.background = 'rgba(0,0,0,0.55)';
overlay.style.display = 'flex';
overlay.style.alignItems = 'center';
overlay.style.justifyContent = 'center';
overlay.style.zIndex = '999999999';
overlay.style.backdropFilter = 'blur(6px)';
overlay.style.opacity = '0';

/* MODAL */
var modal = document.createElement('div');
modal.style.width = '92%';
modal.style.maxWidth = '640px';
modal.style.background = '#070c10';
modal.style.borderRadius = '22px';
modal.style.padding = '40px 36px';   /* 🔥 less vertical padding */
modal.style.fontFamily = 'Poppins, sans-serif';
modal.style.boxShadow = '0 40px 120px rgba(0,0,0,0.9), 0 0 40px rgba(74,222,128,0.15)';
modal.style.transform = 'scale(0.85)';
modal.style.opacity = '0';
modal.style.textAlign = 'center';
modal.style.position = 'relative';

/* LOGO */
var logo = document.createElement('div');
logo.style.fontSize = '66px';
logo.style.fontWeight = '800';
logo.style.marginBottom = '18px';   /* 🔥 spacing control */
logo.innerHTML = '<span style="color:#4ade80;">Hood</span><span style="color:white;">Algo</span>';

/* CHECK */
var check = document.createElement('div');
check.innerText = '✔';
check.style.fontSize = '72px';
check.style.color = '#4ade80';
check.style.marginBottom = '46px';
check.style.marginTop= '46px';

check.style.opacity = '0';
check.style.transform = 'scale(0.5)';
check.style.textShadow = '0 0 25px rgba(74,222,128,0.7)';

/* MAIN */
var main = document.createElement('div');
main.innerText = 'Test Trade Executed';
main.style.fontSize = '30px';
main.style.fontWeight = '800';
main.style.color = 'white';
main.style.marginBottom = '10px';   /* 🔥 key fix */
main.style.opacity = '0';

/* SUB */
var sub = document.createElement('div');
sub.innerText = 'Test Order completed successfully';
sub.style.fontSize = '16px';
sub.style.color = '#9ca3af';
sub.style.marginBottom = '26px';   /* 🔥 creates breathing room before bar */
sub.style.opacity = '0';

/* PROGRESS */
var progress_container = document.createElement('div');
progress_container.style.width = '100%';
progress_container.style.height = '6px';
progress_container.style.background = '#111';
progress_container.style.borderRadius = '10px';
progress_container.style.overflow = 'hidden';

var progress_bar = document.createElement('div');
progress_bar.style.width = '0%';
progress_bar.style.height = '100%';
progress_bar.style.background = 'linear-gradient(90deg,#4ade80,#22c55e)';
progress_container.appendChild(progress_bar);

/* CONFETTI CENTER */
var confetti_container = document.createElement('div');
confetti_container.style.position = 'absolute';
confetti_container.style.top = '50%';
confetti_container.style.left = '50%';
confetti_container.style.pointerEvents = 'none';

/* ANIMATIONS */
if (!document.getElementById('hoodalgo_modal_anim')){
    var style = document.createElement('style');
    style.id = 'hoodalgo_modal_anim';
    style.innerHTML = ''

    + '@keyframes fade_in { to { opacity:1; } }'

    + '@keyframes modal_pop {'
    + '0% { transform:scale(0.7); opacity:0; }'
    + '60% { transform:scale(1.05); }'
    + '100% { transform:scale(1); opacity:1; }'
    + '}'

    + '@keyframes check_pop {'
    + '0% { transform:scale(0.4); opacity:0; }'
    + '70% { transform:scale(1.25); }'
    + '100% { transform:scale(1); opacity:1; }'
    + '}'

    + '@keyframes firework {'
    + '0% { transform:translate(0,0) scale(1); opacity:1; }'
    + '100% { transform:translate(var(--x), var(--y)) scale(0.6); opacity:0; }'
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
modal.appendChild(confetti_container);

overlay.appendChild(modal);
document.body.appendChild(overlay);

/* ANIMATE */
overlay.style.animation = 'fade_in 0.25s ease forwards';

setTimeout(function(){
    modal.style.animation = 'modal_pop 0.45s cubic-bezier(.2,1.4,.4,1) forwards';
},50);

setTimeout(function(){
    check.style.animation = 'check_pop 0.5s ease forwards';
},200);

setTimeout(function(){
    main.style.animation = 'fade_in 0.4s ease forwards';
},400);

setTimeout(function(){
    sub.style.animation = 'fade_in 0.4s ease forwards';
},550);

setTimeout(function(){
    progress_bar.style.animation = 'fill_bar 1.3s ease forwards';
},300);

/* FIREWORK CONFETTI */
setTimeout(function(){
    for (var i = 0; i < 36; i++){
        var c = document.createElement('div');
        c.style.position = 'absolute';
        c.style.width = '6px';
        c.style.height = '10px';
        c.style.background = (Math.random() > 0.5) ? '#4ade80' : '#22c55e';

        var angle = Math.random() * 2 * Math.PI;
        var distance = 120 + Math.random() * 120;

        var x = Math.cos(angle) * distance + 'px';
        var y = Math.sin(angle) * distance + 'px';

        c.style.setProperty('--x', x);
        c.style.setProperty('--y', y);

        c.style.animation = 'firework 0.9s ease-out forwards';

        confetti_container.appendChild(c);
    }
},350);

/* CLOSE */
setTimeout(function(){
    overlay.style.transition = 'opacity 0.35s ease';
    overlay.style.opacity = '0';
    setTimeout(function(){ overlay.remove(); },350);
},2600);

/* ============================= */
/* END */
/* ============================= */

""")